#!/usr/bin/env python3
"""Basic test script for the Multi-Agent Discussion System."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from agents.discussion_agents import AgentFactory
        print("✓ Agent factory imported successfully")
        
        from core.discussion_manager import DiscussionManager
        print("✓ Discussion manager imported successfully")
        
        from config.agent_config import AGENT_CONFIGS
        print("✓ Agent configuration imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_agent_creation():
    """Test creating agents without API calls."""
    print("\nTesting agent creation...")
    
    try:
        from agents.discussion_agents import AgentFactory
        
        # Test creating individual agents
        skeptic = AgentFactory.create_agent("skeptic")
        print(f"✓ Created {skeptic.name} ({skeptic.role})")
        
        synthesizer = AgentFactory.create_agent("synthesizer")
        print(f"✓ Created {synthesizer.name} ({synthesizer.role})")
        
        analyst = AgentFactory.create_agent("analyst")
        print(f"✓ Created {analyst.name} ({analyst.role})")
        
        explorer = AgentFactory.create_agent("explorer")
        print(f"✓ Created {explorer.name} ({explorer.role})")
        
        # Test creating all agents
        all_agents = AgentFactory.create_all_agents()
        print(f"✓ Created all {len(all_agents)} agents")
        
        return True
    except Exception as e:
        print(f"✗ Agent creation error: {e}")
        return False

def test_discussion_manager():
    """Test discussion manager functionality."""
    print("\nTesting discussion manager...")
    
    try:
        from core.discussion_manager import DiscussionManager
        
        # Create manager
        manager = DiscussionManager()
        print("✓ Discussion manager created")
        
        # Test starting a session
        session = manager.start_discussion("Test topic: The future of AI")
        print(f"✓ Discussion session started: {session.session_id}")
        
        # Test adding human message
        manager.add_human_message("Test User", "What do you think about AI safety?")
        print("✓ Human message added")
        
        # Test getting status
        status = manager.get_session_status()
        print(f"✓ Status retrieved: {status['status']}")
        
        # Test ending session
        result = manager.end_discussion()
        print(f"✓ Discussion ended: {result['total_messages']} messages")
        
        return True
    except Exception as e:
        print(f"✗ Discussion manager error: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from config.agent_config import AGENT_CONFIGS, MODEL_CONFIG, DISCUSSION_CONFIG
        
        print(f"✓ Agent configs loaded: {len(AGENT_CONFIGS)} agents")
        print(f"✓ Model config loaded: {MODEL_CONFIG['primary_model']}")
        print(f"✓ Discussion config loaded: {DISCUSSION_CONFIG['max_rounds']} max rounds")
        
        # Verify all required agents are configured
        required_agents = ["skeptic", "synthesizer", "analyst", "explorer"]
        for agent in required_agents:
            if agent in AGENT_CONFIGS:
                print(f"✓ {agent} configuration found")
            else:
                print(f"✗ {agent} configuration missing")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def main():
    """Run all tests."""
    print("Multi-Agent Discussion System - Basic Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_agent_creation,
        test_discussion_manager
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All tests passed! The system is ready.")
        print("\nTo start the system, run:")
        print("  python src/main.py")
        print("\nOr install dependencies first:")
        print("  pip install -r requirements.txt")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())