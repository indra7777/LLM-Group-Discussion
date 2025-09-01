#!/usr/bin/env python3
"""
Quick start script for the web interface.
Runs both the FastAPI backend and React frontend in development mode.
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def run_command(cmd, cwd=None, name="Process"):
    """Run a command and stream output."""
    print(f"\n🚀 Starting {name}...")
    print(f"Command: {' '.join(cmd)}")
    print(f"Directory: {cwd or os.getcwd()}")
    print("-" * 50)
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Stream output
        for line in process.stdout:
            print(f"[{name}] {line.rstrip()}")
            
    except KeyboardInterrupt:
        print(f"\n⏹️ Stopping {name}...")
        process.terminate()
    except Exception as e:
        print(f"❌ Error running {name}: {e}")

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import fastapi
        import uvicorn
        print("✅ Python dependencies OK")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    # Check if Node.js is available
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js OK - {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js from https://nodejs.org/")
        return False
    
    # Check if npm is available
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm OK - {result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not found")
        return False
    
    return True

def install_frontend_deps():
    """Install frontend dependencies."""
    web_dir = Path(__file__).parent / "web"
    package_json = web_dir / "package.json"
    node_modules = web_dir / "node_modules"
    
    if not package_json.exists():
        print("❌ package.json not found in web directory")
        return False
    
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        result = subprocess.run(["npm", "install"], cwd=web_dir, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to install frontend dependencies: {result.stderr}")
            return False
        print("✅ Frontend dependencies installed")
    else:
        print("✅ Frontend dependencies already installed")
    
    return True

def main():
    """Main function to start both services."""
    print("🌟 LLM Group Discussion - Web Interface Startup")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Install frontend dependencies
    if not install_frontend_deps():
        sys.exit(1)
    
    print("\n🎯 Starting services...")
    print("Backend will be available at: http://localhost:8000")
    print("Frontend will be available at: http://localhost:3000")
    print("\nPress Ctrl+C to stop both services\n")
    
    # Start backend in a thread
    backend_thread = threading.Thread(
        target=run_command,
        args=[
            [sys.executable, "web_api.py"],
            None,
            "Backend"
        ]
    )
    
    # Start frontend in a thread
    web_dir = Path(__file__).parent / "web"
    frontend_thread = threading.Thread(
        target=run_command,
        args=[
            ["npm", "start"],
            str(web_dir),
            "Frontend"
        ]
    )
    
    try:
        backend_thread.start()
        time.sleep(2)  # Give backend a moment to start
        frontend_thread.start()
        
        # Wait for both threads
        backend_thread.join()
        frontend_thread.join()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        print("✅ Services stopped")

if __name__ == "__main__":
    main()