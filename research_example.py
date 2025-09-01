#!/usr/bin/env python3
"""
Example usage of the research tool for web search and crawling.
This demonstrates how to use the research functionality in your own code.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def example_basic_search():
    """Example: Basic web search."""
    print("🔍 Example 1: Basic Web Search")
    print("-" * 40)
    
    try:
        from src.utils.research_tool import web_search, research_tool
        
        if not research_tool.is_configured():
            print("⚠️  Research tool not configured. Please see setup instructions.")
            return
        
        # Search for information
        query = "latest artificial intelligence breakthroughs 2024"
        print(f"Searching for: {query}")
        
        results = web_search(query, num_results=3)
        
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results):
            print(f"\n{i+1}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Source: {result['source']}")
            print(f"   Snippet: {result['snippet']}")
        
    except Exception as e:
        print(f"Error: {e}")

def example_web_crawling():
    """Example: Web crawling and content extraction."""
    print("\n🕷️  Example 2: Web Crawling")
    print("-" * 40)
    
    try:
        from src.utils.research_tool import research_tool
        
        if not research_tool.is_configured():
            print("⚠️  Research tool not configured. Please see setup instructions.")
            return
        
        # Crawl a specific URL
        url = "https://en.wikipedia.org/wiki/Machine_learning"
        print(f"Crawling: {url}")
        
        result = research_tool.crawl_url(url)
        
        if 'content' in result and not result.get('error'):
            print(f"\n✅ Successfully crawled!")
            print(f"Title: {result['title']}")
            print(f"Source: {result['source']}")
            print(f"Word count: {result.get('word_count', 0)}")
            print(f"Content preview (first 200 chars):")
            print(f"'{result['content'][:200]}...'")
        else:
            print(f"❌ Crawling failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"Error: {e}")

def example_complete_research():
    """Example: Complete research workflow."""
    print("\n🧠 Example 3: Complete Research Workflow")
    print("-" * 40)
    
    try:
        from src.utils.research_tool import research_topic, research_tool
        
        if not research_tool.is_configured():
            print("⚠️  Research tool not configured. Please see setup instructions.")
            return
        
        # Research a topic comprehensively
        topic = "quantum computing current applications"
        print(f"Researching topic: {topic}")
        
        research_data = research_tool.research_topic(
            topic=topic, 
            num_urls=3, 
            crawl_content=True
        )
        
        # Display results
        print(f"\n📊 Research Summary:")
        summary = research_data.get('summary', {})
        print(f"Status: {summary.get('status', 'unknown')}")
        print(f"URLs found: {summary.get('urls_found', 0)}")
        print(f"URLs crawled: {summary.get('urls_crawled', 0)}")
        print(f"Total words: {summary.get('total_words', 0)}")
        print(f"Sources: {', '.join(summary.get('sources', []))}")
        
        # Get formatted summary for AI consumption
        formatted_summary = research_tool.get_content_summary(research_data)
        print(f"\n📝 Formatted Summary (first 300 chars):")
        print(f"'{formatted_summary[:300]}...'")
        
    except Exception as e:
        print(f"Error: {e}")

def example_quick_research():
    """Example: Quick research for AI agents."""
    print("\n⚡ Example 4: Quick Research (AI Agent Style)")
    print("-" * 40)
    
    try:
        from src.utils.research_tool import quick_research_summary, research_tool
        
        if not research_tool.is_configured():
            print("⚠️  Research tool not configured. Please see setup instructions.")
            return
        
        # This is what an AI agent would call
        topic = "renewable energy statistics 2024"
        print(f"Quick research on: {topic}")
        
        summary = quick_research_summary(topic, max_sources=2)
        
        print(f"\n📋 AI-Ready Summary:")
        print(summary)
        
    except Exception as e:
        print(f"Error: {e}")

def example_integration_with_llm():
    """Example: How to integrate with LLM responses."""
    print("\n🤖 Example 5: LLM Integration Pattern")
    print("-" * 40)
    
    # Simulate an LLM conversation where research is needed
    user_message = "Can you research the latest developments in sustainable energy?"
    
    print(f"User: {user_message}")
    
    try:
        from src.utils.research_tool import research_tool, quick_research_summary
        
        if not research_tool.is_configured():
            print("\nAI Agent: I'd like to research that for you, but my research tool needs to be configured first.")
            print("Please set up Google Custom Search API credentials.")
            return
        
        # Detect if research is needed (simple keyword matching)
        research_triggers = ["research", "latest", "current", "recent"]
        needs_research = any(trigger in user_message.lower() for trigger in research_triggers)
        
        if needs_research:
            # Extract topic (simplified)
            if "research" in user_message.lower():
                # Extract what comes after "research"
                parts = user_message.lower().split("research")
                if len(parts) > 1:
                    topic = parts[1].strip().replace("the ", "").replace("about ", "")
                    topic = topic.split("?")[0].strip()  # Remove question mark
                else:
                    topic = "sustainable energy developments"
            else:
                topic = "sustainable energy developments"
            
            print(f"\nAI Agent: Let me research '{topic}' for you...")
            
            # Perform research
            research_summary = quick_research_summary(topic, max_sources=2)
            
            # Generate response with research
            response = f"Based on my research, here's what I found about {topic}:\n\n{research_summary}"
            
            print(f"\nAI Agent: {response}")
        else:
            print(f"\nAI Agent: I can help with that! (No research needed)")
        
    except Exception as e:
        print(f"\nAI Agent: I encountered an error while researching: {e}")

def show_setup_instructions():
    """Show setup instructions."""
    print("⚙️  Setup Instructions")
    print("=" * 50)
    
    try:
        from src.utils.research_tool import research_tool
        print(research_tool.get_config_instructions())
    except ImportError:
        print("Please install dependencies first:")
        print("pip install beautifulsoup4 lxml html5lib requests python-dotenv")

def main():
    """Run all examples."""
    print("🚀 Research Tool Usage Examples")
    print("=" * 50)
    
    # Check if configured first
    try:
        from src.utils.research_tool import research_tool
        
        if research_tool.is_configured():
            print("✅ Research tool is configured! Running examples...\n")
            
            # Run examples
            example_basic_search()
            example_web_crawling()
            example_complete_research()
            example_quick_research()
            example_integration_with_llm()
            
        else:
            print("❌ Research tool not configured.")
            show_setup_instructions()
            print("\n💡 After configuration, run this script again to see examples.")
            
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please run: pip install -r requirements.txt")

if __name__ == "__main__":
    main()