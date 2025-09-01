#!/usr/bin/env python3
"""Test script for multi-provider API functionality."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_api_keys():
    """Test if API keys are configured."""
    print("Testing API Key Configuration...")
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    api_keys = {
        "Google AI Studio 1": os.getenv("GOOGLE_AI_STUDIO_KEY_1"),
        "Google AI Studio 2": os.getenv("GOOGLE_AI_STUDIO_KEY_2"), 
        "Google Pro": os.getenv("GOOGLE_AI_STUDIO_PRO_KEY"),
        "Groq": os.getenv("GROQ_API_KEY"),
        "OpenRouter": os.getenv("OPENROUTER_API_KEY"),
        "Cerebras": os.getenv("CEREBRAS_API_KEY")
    }
    
    configured = 0
    for name, key in api_keys.items():
        if key and key != "your_api_key_here" and len(key) > 10:
            print(f"✓ {name}: Configured")
            configured += 1
        else:
            print(f"✗ {name}: Not configured")
    
    print(f"\nConfigured: {configured}/{len(api_keys)} providers")
    return configured > 0

def test_multi_provider_client():
    """Test the multi-provider client."""
    print("\nTesting Multi-Provider Client...")
    
    try:
        from core.multi_provider_client import MultiProviderClient
        
        client = MultiProviderClient()
        print("✓ Multi-provider client created successfully")
        
        # Test usage summary
        usage = client.get_usage_summary()
        print(f"✓ Usage summary: {usage['total_requests']} total requests")
        
        # Test cost estimate
        costs = client.get_cost_estimate()
        print(f"✓ Cost estimate: ${costs['total_daily_cost']:.4f} daily")
        
        return True
        
    except Exception as e:
        print(f"✗ Multi-provider client error: {e}")
        return False

def test_discussion_with_real_apis():
    """Test discussion manager with real APIs."""
    print("\nTesting Discussion with Real APIs...")
    
    try:
        from core.discussion_manager import DiscussionManager
        
        # Create manager with real APIs (not demo mode)
        manager = DiscussionManager(demo_mode=False)
        print("✓ Discussion manager created with real APIs")
        
        # Start a session
        session = manager.start_discussion("Testing API integration")
        print(f"✓ Session started: {session.session_id}")
        
        # Add human message
        manager.add_human_message("Tester", "What do you think about multi-provider systems?")
        print("✓ Human message added")
        
        # Generate ONE agent response to test API
        print("Making real API call...")
        responses = manager.generate_agent_responses(["skeptic"])  # Test just one agent
        
        if responses:
            response = responses[0]
            print(f"✓ API Response received from {response['speaker']}")
            print(f"  Content preview: {response['content'][:100]}...")
            
            # Get usage report
            usage_report = manager.get_api_usage_report()
            if "usage_summary" in usage_report:
                usage = usage_report["usage_summary"]
                print(f"✓ Usage tracking: {usage['total_requests']} requests made")
        else:
            print("✗ No response generated")
            return False
        
        # End session
        manager.end_discussion()
        print("✓ Session ended successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Discussion test error: {e}")
        return False

def main():
    """Run all tests."""
    print("Multi-Provider API System Tests")
    print("=" * 40)
    
    tests = [
        test_api_keys,
        test_multi_provider_client,
        test_discussion_with_real_apis
    ]
    
    passed = 0
    for i, test in enumerate(tests, 1):
        print(f"\n--- Test {i}/{len(tests)} ---")
        if test():
            passed += 1
            print("PASSED ✓")
        else:
            print("FAILED ✗")
            # Stop on first failure for safety
            break
    
    print("\n" + "=" * 40)
    print(f"Tests completed: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Your multi-provider system is working!")
        print("\nYou can now run the full system with:")
        print("  python3 src/main.py")
    else:
        print("⚠️  Some tests failed. Check your API configuration.")
    
    return 0 if passed == len(tests) else 1

if __name__ == "__main__":
    sys.exit(main())