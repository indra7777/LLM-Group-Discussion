#!/usr/bin/env python3
"""
Comprehensive testing script for LLM Group Discussion app.
Tests all major functionality before deployment.
"""

import requests
import time
import json
import asyncio
import websockets
from concurrent.futures import ThreadPoolExecutor
import sys

class AppTester:
    def __init__(self, backend_url="http://localhost:8000", frontend_url="http://localhost:3000"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.session_id = None
        
    def test_backend_health(self):
        """Test backend health endpoint."""
        print("Testing backend health...")
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            if response.status_code == 200:
                print("✅ Backend health check passed")
                return True
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend health check failed: {e}")
            return False
    
    def test_frontend_accessibility(self):
        """Test if frontend is accessible."""
        print("Testing frontend accessibility...")
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                print("✅ Frontend is accessible")
                return True
            else:
                print(f"❌ Frontend not accessible: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Frontend not accessible: {e}")
            return False
    
    def test_discussion_start(self):
        """Test starting a discussion."""
        print("Testing discussion start...")
        try:
            payload = {
                "topic": "The impact of AI on future job markets",
                "goal": "explore"
            }
            response = requests.post(
                f"{self.backend_url}/api/discussion/start",
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.session_id = data.get("session_id")
                    print("✅ Discussion start successful")
                    return True
            print(f"❌ Discussion start failed: {response.text}")
            return False
        except Exception as e:
            print(f"❌ Discussion start failed: {e}")
            return False
    
    def test_human_message(self):
        """Test adding human message."""
        print("Testing human message...")
        try:
            payload = {
                "message": "This is a test message from human user",
                "username": "TestUser"
            }
            response = requests.post(
                f"{self.backend_url}/api/discussion/speak",
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ Human message test successful")
                    return True
            print(f"❌ Human message test failed: {response.text}")
            return False
        except Exception as e:
            print(f"❌ Human message test failed: {e}")
            return False
    
    def test_discussion_status(self):
        """Test getting discussion status."""
        print("Testing discussion status...")
        try:
            response = requests.get(f"{self.backend_url}/api/discussion/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ Discussion status test successful")
                    return True
            print(f"❌ Discussion status test failed: {response.text}")
            return False
        except Exception as e:
            print(f"❌ Discussion status test failed: {e}")
            return False
    
    def test_get_messages(self):
        """Test getting messages."""
        print("Testing get messages...")
        try:
            response = requests.get(f"{self.backend_url}/api/discussion/messages", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and isinstance(data.get("messages"), list):
                    print(f"✅ Get messages test successful (found {len(data['messages'])} messages)")
                    return True
            print(f"❌ Get messages test failed: {response.text}")
            return False
        except Exception as e:
            print(f"❌ Get messages test failed: {e}")
            return False
    
    async def test_websocket_connection(self):
        """Test WebSocket connection."""
        print("Testing WebSocket connection...")
        try:
            uri = f"ws://localhost:8000/ws"
            async with websockets.connect(uri) as websocket:
                # Send a test message
                await websocket.send("test message")
                
                # Try to receive response (with timeout)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print("✅ WebSocket connection test successful")
                    return True
                except asyncio.TimeoutError:
                    print("✅ WebSocket connection established (no response expected)")
                    return True
        except Exception as e:
            print(f"❌ WebSocket connection test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("🧪 Starting comprehensive app testing...")
        print("=" * 60)
        
        tests = [
            self.test_backend_health,
            self.test_frontend_accessibility,
            self.test_discussion_start,
            self.test_human_message,
            self.test_discussion_status,
            self.test_get_messages,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()
        
        # Test WebSocket separately (async)
        print("Testing WebSocket connection...")
        ws_result = asyncio.run(self.test_websocket_connection())
        if ws_result:
            passed += 1
        total += 1
        
        print("=" * 60)
        print(f"🧪 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! App is ready for deployment.")
            return True
        else:
            print("❌ Some tests failed. Please fix issues before deployment.")
            return False

def main():
    """Main testing function."""
    print("LLM Group Discussion - Deployment Testing")
    print("=" * 60)
    
    tester = AppTester()
    
    # Wait a moment for services to be ready
    print("Waiting for services to be ready...")
    time.sleep(2)
    
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Ready for deployment!")
        sys.exit(0)
    else:
        print("\n❌ Not ready for deployment. Please fix issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()