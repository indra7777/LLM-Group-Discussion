#!/usr/bin/env python3
"""
Test script for the research tool functionality.
This demonstrates how the Google Custom Search + Web Crawling tool works.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

def test_research_configuration():
    """Test if research tool is properly configured."""
    print("🔧 Testing Research Tool Configuration...")
    
    try:
        from src.utils.research_tool import research_tool
        
        if research_tool.is_configured():
            print("✅ Research tool is properly configured!")
            return True
        else:
            print("❌ Research tool is not configured.")
            print("\nConfiguration needed:")
            print(research_tool.get_config_instructions())
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required dependencies: pip install beautifulsoup4 lxml html5lib")
        return False

def test_basic_search():
    """Test basic web search functionality."""
    print("\n🔍 Testing Basic Web Search...")
    
    try:
        from src.utils.research_tool import web_search
        
        # Test search
        results = web_search("artificial intelligence 2024", num_results=3)
        
        print(f"✅ Found {len(results)} search results")
        for i, result in enumerate(results[:2]):  # Show first 2
            print(f"  {i+1}. {result['title']}")
            print(f"     URL: {result['url']}")
            print(f"     Snippet: {result['snippet'][:100]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False

def test_web_crawling():
    """Test web crawling functionality."""
    print("\n🕷️  Testing Web Crawling...")
    
    try:
        from src.utils.research_tool import research_tool
        
        # Test crawling a simple page
        test_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
        result = research_tool.crawl_url(test_url)
        
        if 'content' in result and not result.get('error'):
            print(f"✅ Successfully crawled {result['source']}")
            print(f"   Title: {result['title'][:60]}...")
            print(f"   Content length: {len(result['content'])} characters")
            print(f"   Word count: {result.get('word_count', 0)} words")
        else:
            print(f"❌ Crawling failed: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Crawling failed: {e}")
        return False

def test_complete_research():
    """Test complete research workflow."""
    print("\n🧠 Testing Complete Research Workflow...")
    
    try:
        from src.utils.research_tool import research_topic, quick_research_summary
        
        # Test topic research
        topic = "latest AI developments 2024"
        print(f"   Researching: {topic}")
        
        # Get quick summary
        summary = quick_research_summary(topic, max_sources=2)
        
        print("✅ Research completed!")
        print(f"\nSummary (first 300 chars):\n{summary[:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete research failed: {e}")
        return False

def test_research_agent():
    """Test research agent functionality."""
    print("\n🤖 Testing Research Agent...")
    
    try:
        from src.agents.research_agent import ResearchAgent
        from src.utils.research_tool import research_tool
        
        if not research_tool.is_configured():
            print("⚠️  Research tool not configured, skipping agent test")
            return False
        
        # Create research agent
        agent = ResearchAgent()
        
        # Test research trigger detection
        test_contexts = [
            "Can you research the latest AI trends?",
            "Look up information about quantum computing",
            "What are the current statistics on renewable energy?"
        ]
        
        for context in test_contexts:
            topics = agent._should_research(context)
            if topics:
                print(f"✅ Detected research topics in: '{context[:50]}...'")
                print(f"   Topics: {topics}")
            else:
                print(f"❌ No research topics detected in: '{context[:50]}...'")
        
        return True
        
    except Exception as e:
        print(f"❌ Research agent test failed: {e}")
        return False

def demo_research():
    """Demonstrate the research functionality with a real example."""
    print("\n🚀 DEMO: Research Tool in Action")
    print("=" * 50)
    
    try:
        from src.utils.research_tool import research_tool
        
        if not research_tool.is_configured():
            print("Please configure the research tool first (see instructions above)")
            return
        
        demo_topic = "Claude AI language model capabilities"
        print(f"Demo topic: {demo_topic}")
        
        # Perform research
        research_data = research_tool.research_topic(demo_topic, num_urls=3, crawl_content=True)
        summary = research_tool.get_content_summary(research_data, max_length=800)
        
        print("\n" + "=" * 50)
        print("RESEARCH RESULTS:")
        print("=" * 50)
        print(summary)
        print("=" * 50)
        
    except Exception as e:
        print(f"Demo failed: {e}")

def main():
    """Run all tests."""
    print("🧪 Research Tool Test Suite")
    print("=" * 40)
    
    # Run tests
    tests = [
        test_research_configuration,
        test_basic_search,
        test_web_crawling,
        test_complete_research,
        test_research_agent
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY:")
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    
    if results[0]:  # If configuration test passed
        demo_research()

if __name__ == "__main__":
    main()