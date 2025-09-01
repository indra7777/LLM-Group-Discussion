#!/usr/bin/env python3
"""
FastAPI web server for the Multi-Agent Discussion System.
Provides REST API and WebSocket endpoints for the web UI.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os
import sys
import asyncio
import re
from uuid import uuid4
from datetime import datetime

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.discussion_manager import DiscussionManager
from src.utils.research_tool import quick_research_summary, research_tool

# Initialize FastAPI app
app = FastAPI(title="LLM Group Discussion API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://*.onrender.com",
        "https://*.netlify.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global discussion manager instance
discussion_manager = None

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: Dict):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Connection might be closed, remove it
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Pydantic models for API
class StartDiscussionRequest(BaseModel):
    topic: str
    goal: Optional[str] = "explore"  # explore, outline, stress_test

class SpeakRequest(BaseModel):
    message: str
    username: Optional[str] = "Human"

class ResearchRequest(BaseModel):
    topic: str
    max_sources: Optional[int] = 3

# Initialize discussion manager
@app.on_event("startup")
async def startup_event():
    global discussion_manager
    discussion_manager = DiscussionManager(demo_mode=False)

# API Routes
@app.get("/")
async def read_root():
    """Serve the main web application."""
    if os.path.exists("web/build/index.html"):
        from fastapi.responses import FileResponse
        return FileResponse("web/build/index.html")
    else:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>LLM Group Discussion</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <div id="root">
                <h1>LLM Group Discussion API</h1>
                <p>Frontend not built yet. Build the frontend first:</p>
                <pre>cd web && npm run build</pre>
                <p>API endpoints are available at /api/</p>
            </div>
        </body>
        </html>
        """)

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/discussion/start")
async def start_discussion(request: StartDiscussionRequest):
    """Start a new discussion."""
    try:
        session = discussion_manager.start_discussion(request.topic)
        
        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "discussion_started",
            "data": {
                "session_id": session.session_id,
                "topic": request.topic,
                "goal": request.goal
            }
        })
        
        return {
            "success": True,
            "session_id": session.session_id,
            "topic": request.topic,
            "message": "Discussion started successfully!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/discussion/speak")
async def speak_in_discussion(request: SpeakRequest):
    """Add a human message to the discussion."""
    try:
        if not discussion_manager.current_session:
            raise HTTPException(status_code=400, detail="No active discussion")
        
        discussion_manager.add_human_message(request.username, request.message)
        
        # Get the latest message
        latest_message = discussion_manager.current_session.messages[-1]
        
        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "new_message",
            "data": {
                "id": latest_message.get("id"),
                "speaker": latest_message["speaker"],
                "content": latest_message["content"],
                "type": latest_message["type"],
                "timestamp": latest_message["timestamp"].isoformat()
            }
        })
        
        return {"success": True, "message": "Message added to discussion"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/discussion/next")
async def next_round():
    """Let agents respond in the discussion."""
    try:
        if not discussion_manager.current_session:
            raise HTTPException(status_code=400, detail="No active discussion")
        
        if not discussion_manager.should_continue_discussion():
            return {"success": False, "message": "Discussion has reached its limit"}
        
        # Broadcast "thinking" status
        await manager.broadcast({
            "type": "agents_thinking",
            "data": {"status": "Agents are thinking..."}
        })
        
        # Generate responses (this might take a while)
        responses = discussion_manager.generate_agent_responses()
        
        # Broadcast each response with simulated streaming chunks
        for i, response in enumerate(responses):
            content = response["content"]
            speaker = response["speaker"]
            msg_id = response.get("id") or str(uuid4())

            # Send start event
            await manager.broadcast({
                "type": "message_start",
                "data": {
                    "id": msg_id,
                    "speaker": speaker,
                    "type": response["type"],
                    "timestamp": response["timestamp"].isoformat()
                }
            })

            # Stream chunks by sentence/words for smoother UI
            # Split by sentences, then further by small word groups
            sentences = re.split(r"(?<=[\.!?])\s+", content)
            for sent in sentences:
                words = sent.split(" ")
                chunk = []
                for w in words:
                    chunk.append(w)
                    if len(chunk) >= 4:  # send in groups of ~4 words
                        await asyncio.sleep(0.08)
                        await manager.broadcast({
                            "type": "message_chunk",
                            "data": {"id": msg_id, "delta": " ".join(chunk) + " "}
                        })
                        chunk = []
                if chunk:
                    await asyncio.sleep(0.08)
                    await manager.broadcast({
                        "type": "message_chunk",
                        "data": {"id": msg_id, "delta": " ".join(chunk) + " "}
                    })
                # Slight pause between sentences
                await asyncio.sleep(0.12)

            # Send end event with full content
            await manager.broadcast({
                "type": "message_end",
                "data": {
                    "id": msg_id,
                    "speaker": speaker,
                    "content": content,
                    "type": response["type"],
                    "timestamp": response["timestamp"].isoformat()
                }
            })
        
        # Advance round
        discussion_manager.advance_round()
        
        return {
            "success": True,
            "responses_count": len(responses),
            "message": f"{len(responses)} agent(s) responded"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/discussion/status")
async def get_discussion_status():
    """Get current discussion status."""
    try:
        status = discussion_manager.get_session_status()
        return {"success": True, "data": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/discussion/summary")
async def get_discussion_summary():
    """Get discussion summary."""
    try:
        if not discussion_manager.current_session:
            raise HTTPException(status_code=400, detail="No active discussion")
        
        summary = discussion_manager.generate_discussion_summary()
        return {"success": True, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/discussion/messages")
async def get_messages(limit: int = 50):
    """Get recent messages from the discussion."""
    try:
        if not discussion_manager.current_session:
            return {"success": True, "messages": []}
        
        messages = discussion_manager.current_session.messages[-limit:]
        
        # Format messages for JSON serialization
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": msg.get("id"),
                "speaker": msg["speaker"],
                "content": msg["content"],
                "type": msg["type"],
                "timestamp": msg["timestamp"].isoformat()
            })
        
        return {"success": True, "messages": formatted_messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research")
async def research_topic(request: ResearchRequest):
    """Research a topic using web search."""
    try:
        if not research_tool.is_configured():
            raise HTTPException(
                status_code=400, 
                detail="Research tool not configured. Please set up API keys."
            )
        
        summary = quick_research_summary(request.topic, max_sources=request.max_sources)
        
        return {
            "success": True,
            "topic": request.topic,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/discussion/end")
async def end_discussion():
    """End the current discussion."""
    try:
        if not discussion_manager.current_session:
            raise HTTPException(status_code=400, detail="No active discussion")
        
        result = discussion_manager.end_discussion()
        
        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "discussion_ended",
            "data": result
        })
        
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for any client messages
            data = await websocket.receive_text()
            # For now, just echo back (could add client-side commands later)
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Mount static files (for the React frontend when it's built)
if os.path.exists("web/build"):
    app.mount("/static", StaticFiles(directory="web/build/static"), name="static")
    # Also serve the main index.html
    from fastapi.responses import FileResponse
    
    @app.get("/static/index.html")
    async def serve_index():
        return FileResponse("web/build/index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "True").lower() == "true"
    uvicorn.run("web_api:app", host="0.0.0.0", port=port, reload=debug)