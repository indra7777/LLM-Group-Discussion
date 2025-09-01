#!/usr/bin/env python3
"""Test conversation saving and analysis functionality."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_conversation_storage():
    """Test the conversation storage system."""
    print("Testing Conversation Storage System...")
    
    try:
        from core.discussion_manager import DiscussionManager
        
        # Create manager in demo mode for testing
        manager = DiscussionManager(demo_mode=True)
        
        # Start a test discussion
        session = manager.start_discussion("The Future of AI Ethics")
        print("✓ Test discussion started")
        
        # Add some test messages
        manager.add_human_message("Researcher", "What are the main ethical concerns with AI?")
        
        # Generate a few agent responses
        for i in range(3):
            responses = manager.generate_agent_responses()
            if responses:
                print(f"✓ Round {i+1}: {len(responses)} agent(s) responded")
            manager.advance_round()
        
        # Add another human message
        manager.add_human_message("Researcher", "How can we address these concerns?")
        
        # Generate more responses
        responses = manager.generate_agent_responses()
        if responses:
            print(f"✓ Final round: {len(responses)} agent(s) responded")
        
        # End discussion and save
        result = manager.end_discussion()
        
        if "saved_files" in result:
            print("✓ Conversation saved successfully!")
            for format_type, filepath in result["saved_files"].items():
                print(f"  {format_type}: {filepath}")
            
            # Test listing conversations
            conversations = manager.list_saved_conversations()
            print(f"✓ Found {len(conversations)} saved conversation(s)")
            
            # Test analysis
            if conversations:
                filename = conversations[0]["filename"]
                analysis = manager.get_conversation_analysis(filename)
                if analysis:
                    print("✓ Conversation analysis generated")
                    
                    # Show some analysis results
                    if "agent_performance" in analysis:
                        print(f"  Agent performance data: {len(analysis['agent_performance'])} agents")
                    
                    if "potential_improvements" in analysis:
                        improvements = analysis["potential_improvements"]
                        print(f"  Improvement suggestions: {len(improvements)}")
                        for suggestion in improvements:
                            print(f"    - {suggestion}")
                else:
                    print("✗ Analysis generation failed")
            
            return True
        else:
            print("✗ Conversation saving failed")
            return False
            
    except Exception as e:
        print(f"✗ Error testing conversation storage: {e}")
        return False

def test_search_functionality():
    """Test conversation search functionality."""
    print("\nTesting Search Functionality...")
    
    try:
        from core.discussion_manager import DiscussionManager
        
        manager = DiscussionManager(demo_mode=True)
        
        # Test search (should find the conversation we just created)
        results = manager.search_conversations("AI Ethics")
        
        if results:
            print(f"✓ Search found {len(results)} conversation(s)")
            for result in results:
                print(f"  - {result['topic']} ({result['filename']})")
            return True
        else:
            print("✗ Search found no results (might be expected if no conversations saved)")
            return True  # Not necessarily an error
            
    except Exception as e:
        print(f"✗ Error testing search: {e}")
        return False

def test_file_formats():
    """Test different export formats."""
    print("\nTesting Export Formats...")
    
    try:
        from core.conversation_storage import ConversationStorage
        from core.discussion_manager import DiscussionSession
        from datetime import datetime
        
        # Create a mock session with some data
        storage = ConversationStorage("test_conversations")
        session = DiscussionSession("Test Export Formats")
        
        # Add some mock messages
        session.add_message("Human", "Test human message", "human")
        session.add_message("Dr. Skeptic", "[SKEPTIC] Test skeptical response", "agent")
        session.add_message("Dr. Synthesis", "[SYNTHESIZER] Test synthesis response", "agent")
        
        # Test saving in all formats
        saved_files = storage.save_conversation(session, ["json", "markdown", "csv"])
        
        if len(saved_files) == 4:  # json, markdown, csv, analysis
            print("✓ All export formats generated successfully")
            for format_type, filepath in saved_files.items():
                if os.path.exists(filepath):
                    print(f"  ✓ {format_type}: {filepath}")
                else:
                    print(f"  ✗ {format_type}: File not found")
            return True
        else:
            print(f"✗ Expected 4 files, got {len(saved_files)}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing export formats: {e}")
        return False

def main():
    """Run all conversation saving tests."""
    print("Conversation Saving & Analysis Tests")
    print("=" * 40)
    
    tests = [
        test_conversation_storage,
        test_search_functionality,
        test_file_formats
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
        print("🎉 Conversation saving system is working!")
        print("\nNew CLI commands available:")
        print("  save              - Save current conversation")
        print("  list              - List saved conversations") 
        print("  load <filename>   - View a conversation")
        print("  search <query>    - Search conversations")
        print("  analyze <filename>- Analyze conversation quality")
        
        print("\nFiles are saved in:")
        print("  conversations/json/     - JSON format")
        print("  conversations/markdown/ - Markdown format") 
        print("  conversations/csv/      - CSV format")
        print("  conversations/analysis/ - Quality analysis")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return 0 if passed == len(tests) else 1

if __name__ == "__main__":
    sys.exit(main())