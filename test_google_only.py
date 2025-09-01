#!/usr/bin/env python3
"""Test script for Google AI Studio only configuration."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_google_keys():
    """Test Google API key configuration."""
    print("Testing Google AI Studio Configuration...")
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    google_keys = {
        "Account 1": os.getenv("GOOGLE_AI_STUDIO_KEY_1"),
        "Account 2": os.getenv("GOOGLE_AI_STUDIO_KEY_2"),
        "Account 3": os.getenv("GOOGLE_AI_STUDIO_KEY_3"),
        "Account 4": os.getenv("GOOGLE_AI_STUDIO_KEY_4"),
        "Pro Account": os.getenv("GOOGLE_AI_STUDIO_PRO_KEY")
    }
    
    configured = 0
    for name, key in google_keys.items():
        if key and len(key) > 20:  # Google keys are long
            print(f"✓ {name}: Configured")
            configured += 1
        else:
            print(f"✗ {name}: Not configured")
    
    print(f"\nGoogle Accounts Configured: {configured}/5")
    return configured > 0

def test_agent_routing():
    """Test that all agents are routed to Google AI Studio."""
    print("\nTesting Agent Routing Configuration...")
    
    try:
        from config.provider_config import AGENT_PROVIDER_MAPPING
        
        all_google = True
        for agent_type, config in AGENT_PROVIDER_MAPPING.items():
            primary = config.get("primary")
            fallback = config.get("fallback")
            
            if primary != "google_ai_studio" or fallback != "google_ai_studio":
                print(f"✗ {agent_type}: Not using Google AI Studio")
                all_google = False
            else:
                print(f"✓ {agent_type}: Using Google AI Studio")
        
        if all_google:
            print("✓ All agents correctly routed to Google AI Studio")
        
        return all_google
        
    except Exception as e:
        print(f"✗ Error checking routing: {e}")
        return False

def test_discussion_basic():
    """Test basic discussion functionality."""
    print("\nTesting Basic Discussion (Demo Mode)...")
    
    try:
        from core.discussion_manager import DiscussionManager
        
        # Test in demo mode first
        manager = DiscussionManager(demo_mode=True)
        session = manager.start_discussion("Test Google configuration")
        manager.add_human_message("Tester", "Testing Google-only setup")
        responses = manager.generate_agent_responses(["skeptic"])
        
        if responses:
            print("✓ Demo mode working correctly")
            manager.end_discussion()
            return True
        else:
            print("✗ Demo mode failed")
            return False
            
    except Exception as e:
        print(f"✗ Discussion test error: {e}")
        return False

def main():
    """Run Google-only configuration tests."""
    print("Google AI Studio Configuration Tests")
    print("=" * 40)
    
    tests = [
        test_google_keys,
        test_agent_routing,
        test_discussion_basic
    ]
    
    passed = 0
    for i, test in enumerate(tests, 1):
        print(f"\n--- Test {i}/{len(tests)} ---")
        if test():
            passed += 1
            print("PASSED ✓")
        else:
            print("FAILED ✗")
    
    print("\n" + "=" * 40)
    print(f"Tests completed: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("🎉 Google-only configuration is working!")
        print("\nNext steps:")
        print("1. Add your additional Google API keys to .env")
        print("2. Run: ./setup_environment.sh")
        print("3. Run: source venv/bin/activate && python3 src/main.py")
    else:
        print("⚠️  Some tests failed. Check your configuration.")
    
    return 0 if passed == len(tests) else 1

if __name__ == "__main__":
    sys.exit(main())