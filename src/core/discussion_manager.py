"""Core discussion management and orchestration logic."""

from typing import Dict, List, Optional, Tuple, Any
import random
import time
import os
import json
from datetime import datetime
from uuid import uuid4

from src.agents.discussion_agents import AgentFactory, BaseDiscussionAgent
from src.agents.demo_agent import DemoAgentFactory
from src.core.multi_provider_client import MultiProviderClient
from src.core.conversation_storage import ConversationStorage
from config.agent_config import DISCUSSION_CONFIG


class DiscussionSession:
    """Represents a single discussion session."""
    
    def __init__(self, topic: str, session_id: str = None):
        self.topic = topic
        self.session_id = session_id or f"session_{int(time.time())}"
        self.created_at = datetime.now()
        self.messages = []
        self.round_number = 0
        self.is_active = True
        self.human_participants = []
    
    def add_message(self, speaker: str, content: str, message_type: str = "agent"):
        """Add a message to the session."""
        message = {
            "id": str(uuid4()),
            "speaker": speaker,
            "content": content,
            "type": message_type,  # "agent", "human", "system"
            "timestamp": datetime.now(),
            "round": self.round_number
        }
        self.messages.append(message)
        return message
    
    def get_recent_messages(self, count: int = 5) -> List[Dict]:
        """Get the most recent messages."""
        return self.messages[-count:] if self.messages else []
    
    def get_messages_by_round(self, round_num: int) -> List[Dict]:
        """Get all messages from a specific round."""
        return [msg for msg in self.messages if msg["round"] == round_num]


class DiscussionManager:
    """Manages multi-agent discussions with human moderation."""
    
    def __init__(self, model_config: Dict[str, Any] = None, demo_mode: bool = False):
        if demo_mode:
            self.agents = DemoAgentFactory.create_all_agents()
            self.demo_mode = True
            self.multi_provider_client = None
        else:
            # Initialize multi-provider client
            try:
                self.multi_provider_client = MultiProviderClient()
            except Exception as e:
                print(f"Warning: Multi-provider client failed to initialize: {e}")
                self.multi_provider_client = None
            
            self.agents = AgentFactory.create_all_agents(model_config, self.multi_provider_client)
            self.demo_mode = False
        
        self.current_session = None
        self.config = DISCUSSION_CONFIG
        
        # Initialize conversation storage
        self.storage = ConversationStorage()
        
        # Agent participation tracking
        self.agent_participation = {name: 0 for name in self.agents.keys()}
        
    def start_discussion(self, topic: str, session_id: str = None) -> DiscussionSession:
        """Start a new discussion session."""
        self.current_session = DiscussionSession(topic, session_id)
        
        # Reset agent histories
        for agent in self.agents.values():
            agent.reset_history()
        
        # Add opening system message
        self.current_session.add_message(
            "SYSTEM", 
            f"Discussion started on topic: {topic}",
            "system"
        )
        
        return self.current_session
    
    def add_human_message(self, speaker_name: str, message: str) -> Dict:
        """Add a human participant's message to the discussion."""
        if not self.current_session:
            raise ValueError("No active discussion session")
        
        if speaker_name not in self.current_session.human_participants:
            self.current_session.human_participants.append(speaker_name)
        
        return self.current_session.add_message(speaker_name, message, "human")
    
    def get_next_speakers(self, max_speakers: int = 2) -> List[str]:
        """Determine which agents should speak next based on participation balance."""
        if not self.current_session:
            return []
        
        # Sort agents by participation count (least active first)
        sorted_agents = sorted(
            self.agent_participation.items(),
            key=lambda x: x[1]
        )
        
        # Select up to max_speakers agents, prioritizing less active ones
        selected = []
        for agent_name, _ in sorted_agents:
            if len(selected) < max_speakers:
                selected.append(agent_name)
        
        return selected
    
    def generate_agent_responses(self, agent_names: List[str] = None) -> List[Dict]:
        """Generate responses from specified agents."""
        if not self.current_session:
            raise ValueError("No active discussion session")
        
        if agent_names is None:
            agent_names = self.get_next_speakers()
        
        responses = []
        recent_messages = self.current_session.get_recent_messages(5)
        context = f"Topic: {self.current_session.topic}"
        
        # Format recent messages for context
        message_context = []
        for msg in recent_messages:
            if msg["type"] != "system":
                message_context.append(f"{msg['speaker']}: {msg['content']}")
        
        for agent_name in agent_names:
            if agent_name in self.agents:
                try:
                    response = self.agents[agent_name].generate_response(
                        context, 
                        message_context
                    )
                    
                    message = self.current_session.add_message(
                        self.agents[agent_name].name,
                        response,
                        "agent"
                    )
                    
                    # Update participation tracking
                    self.agent_participation[agent_name] += 1
                    
                    # Add to agent's history
                    self.agents[agent_name].add_to_history(response, True)
                    
                    responses.append(message)
                    
                except Exception as e:
                    error_msg = f"Error generating response from {agent_name}: {str(e)}"
                    self.current_session.add_message("SYSTEM", error_msg, "system")
        
        return responses
    
    def advance_round(self) -> int:
        """Advance to the next discussion round."""
        if self.current_session:
            self.current_session.round_number += 1
            
            # Add round marker
            self.current_session.add_message(
                "SYSTEM",
                f"--- Round {self.current_session.round_number} ---",
                "system"
            )
        
        return self.current_session.round_number if self.current_session else 0
    
    def should_continue_discussion(self) -> bool:
        """Determine if the discussion should continue based on configured limits."""
        if not self.current_session:
            return False
        
        # Check round limit
        if self.current_session.round_number >= self.config["max_rounds"]:
            return False
        
        # Check if discussion is still active
        if not self.current_session.is_active:
            return False
        
        return True
    
    def end_discussion(self, save_conversation: bool = True) -> Dict:
        """End the current discussion and generate a summary."""
        if not self.current_session:
            return {"error": "No active discussion"}
        
        self.current_session.is_active = False
        
        # Generate summary
        summary = self.generate_discussion_summary()
        
        self.current_session.add_message(
            "SYSTEM",
            f"Discussion ended. Summary: {summary}",
            "system"
        )
        
        result = {
            "session_id": self.current_session.session_id,
            "topic": self.current_session.topic,
            "total_messages": len(self.current_session.messages),
            "rounds": self.current_session.round_number,
            "summary": summary,
            "participants": {
                "agents": list(self.agents.keys()),
                "humans": self.current_session.human_participants
            }
        }
        
        # Save conversation if requested
        if save_conversation:
            try:
                saved_files = self.storage.save_conversation(self.current_session)
                result["saved_files"] = saved_files
            except Exception as e:
                result["save_error"] = str(e)
        
        return result
    
    def generate_discussion_summary(self) -> str:
        """Generate a summary of the current discussion."""
        if not self.current_session or not self.current_session.messages:
            return "No discussion to summarize."
        
        # Simple summary based on message count and participation
        agent_messages = [msg for msg in self.current_session.messages if msg["type"] == "agent"]
        human_messages = [msg for msg in self.current_session.messages if msg["type"] == "human"]
        
        summary = f"Discussion on '{self.current_session.topic}' with {len(agent_messages)} agent contributions and {len(human_messages)} human contributions across {self.current_session.round_number} rounds."
        
        return summary
    
    def get_session_status(self) -> Dict:
        """Get the current session status."""
        if not self.current_session:
            return {"status": "no_active_session"}
        
        status = {
            "status": "active" if self.current_session.is_active else "ended",
            "session_id": self.current_session.session_id,
            "topic": self.current_session.topic,
            "round": self.current_session.round_number,
            "total_messages": len(self.current_session.messages),
            "agent_participation": self.agent_participation.copy(),
            "human_participants": self.current_session.human_participants.copy()
        }
        
        # Add API usage info if available
        if self.multi_provider_client:
            status["api_usage"] = self.multi_provider_client.get_usage_summary()
            status["cost_estimate"] = self.multi_provider_client.get_cost_estimate()
        
        return status
    
    def get_api_usage_report(self) -> Dict:
        """Get detailed API usage report."""
        if not self.multi_provider_client:
            return {"error": "Multi-provider client not available"}
        
        return {
            "usage_summary": self.multi_provider_client.get_usage_summary(),
            "cost_estimate": self.multi_provider_client.get_cost_estimate(),
            "provider_status": {
                provider: self.multi_provider_client._can_use_provider(provider)
                for provider in ["google_ai_studio", "groq", "openrouter", "cerebras"]
            }
        }
    
    def save_current_conversation(self, formats: List[str] = None) -> Dict:
        """Manually save the current conversation."""
        if not self.current_session:
            return {"error": "No active discussion to save"}
        
        try:
            saved_files = self.storage.save_conversation(self.current_session, formats)
            return {"success": True, "saved_files": saved_files}
        except Exception as e:
            return {"error": str(e)}
    
    def list_saved_conversations(self) -> List[Dict]:
        """List all saved conversations."""
        return self.storage.list_conversations()
    
    def load_conversation(self, filename: str) -> Optional[Dict]:
        """Load a specific conversation."""
        return self.storage.load_conversation(filename)
    
    def search_conversations(self, query: str) -> List[Dict]:
        """Search conversations by content."""
        return self.storage.search_conversations(query)
    
    def get_conversation_analysis(self, filename: str) -> Optional[Dict]:
        """Get analysis for a specific conversation."""
        # Load the analysis file
        analysis_filename = filename.replace('.json', '_analysis.json')
        analysis_path = os.path.join(self.storage.storage_dir, "analysis", analysis_filename)
        
        if os.path.exists(analysis_path):
            try:
                with open(analysis_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                return {"error": str(e)}
        
        return None