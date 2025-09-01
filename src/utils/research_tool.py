"""
Research tool combining Google Custom Search API with web crawling capabilities.
This tool provides automated research functionality for the AI agents.
"""

import os
import re
import time
import json
import requests
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
from datetime import datetime
import hashlib

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("Warning: beautifulsoup4 not available. Install with: pip install beautifulsoup4")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not available")


class ResearchTool:
    """Automated research tool using Google Custom Search and web crawling."""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        self.cache_dir = "research_cache"
        self.max_results = 10
        self.crawl_delay = 1  # Seconds between requests
        self.timeout = 10
        self.user_agent = "Mozilla/5.0 (compatible; LLM-Research-Bot/1.0)"
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def is_configured(self) -> bool:
        """Check if the research tool is properly configured."""
        if not BS4_AVAILABLE:
            return False
        return bool(self.google_api_key and self.google_cse_id)
    
    def get_config_instructions(self) -> str:
        """Get setup instructions for the research tool."""
        return """
To enable the Research Tool, you need:

1. Google Custom Search API Key:
   - Visit: https://developers.google.com/custom-search/v1/overview
   - Create a project and enable Custom Search API
   - Generate an API key

2. Google Custom Search Engine ID:
   - Visit: https://cse.google.com/cse/
   - Create a new search engine
   - Set it to search the entire web
   - Copy the Search Engine ID

3. Add to your .env file:
   GOOGLE_SEARCH_API_KEY=your_api_key_here
   GOOGLE_CSE_ID=your_cse_id_here

4. Install required packages:
   pip install beautifulsoup4 lxml html5lib
        """
    
    def search_web(self, query: str, num_results: int = None) -> List[Dict[str, Any]]:
        """Search the web using Google Custom Search API."""
        if not self.is_configured():
            raise Exception("Research tool not configured. " + self.get_config_instructions())
        
        if num_results is None:
            num_results = self.max_results
        
        # Check cache first
        cache_key = hashlib.md5(f"{query}_{num_results}".encode()).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"search_{cache_key}.json")
        
        if os.path.exists(cache_file):
            # Check if cache is less than 24 hours old
            cache_time = os.path.getmtime(cache_file)
            if time.time() - cache_time < 86400:  # 24 hours
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        # Make API request
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.google_api_key,
            'cx': self.google_cse_id,
            'q': query,
            'num': min(num_results, 10),  # API limit
            'safe': 'active',
            'lr': 'lang_en'
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if 'items' in data:
                for item in data['items']:
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': urlparse(item.get('link', '')).netloc
                    })
            
            # Cache results
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            return results
            
        except requests.RequestException as e:
            raise Exception(f"Search API error: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse search results: {e}")
    
    def crawl_url(self, url: str) -> Dict[str, Any]:
        """Crawl and extract text content from a URL."""
        if not BS4_AVAILABLE:
            raise Exception("beautifulsoup4 required for web crawling")
        
        # Check cache first
        cache_key = hashlib.md5(url.encode()).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"crawl_{cache_key}.json")
        
        if os.path.exists(cache_file):
            # Check if cache is less than 24 hours old
            cache_time = os.path.getmtime(cache_file)
            if time.time() - cache_time < 86400:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script, style, and other non-content elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else ''
            
            # Extract main content
            content_selectors = [
                'article', 'main', '.content', '#content', '.post', '.article-body',
                '.entry-content', '.post-content', '.article-content'
            ]
            
            content_text = ''
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content_text = content_elem.get_text(separator='\n', strip=True)
                    break
            
            # Fallback to body if no specific content found
            if not content_text:
                body = soup.find('body')
                if body:
                    content_text = body.get_text(separator='\n', strip=True)
            
            # Clean up text
            content_text = re.sub(r'\n\s*\n', '\n\n', content_text)  # Remove extra whitespace
            content_text = content_text.strip()
            
            # Extract metadata
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '') if meta_description else ''
            
            result = {
                'url': url,
                'title': title_text,
                'description': description,
                'content': content_text[:5000],  # Limit content length
                'word_count': len(content_text.split()),
                'crawled_at': datetime.now().isoformat(),
                'source': urlparse(url).netloc
            }
            
            # Cache result
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            return result
            
        except requests.RequestException as e:
            return {
                'url': url,
                'error': f"Failed to crawl: {e}",
                'crawled_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'url': url,
                'error': f"Parsing error: {e}",
                'crawled_at': datetime.now().isoformat()
            }
    
    def research_topic(self, topic: str, num_urls: int = 5, crawl_content: bool = True) -> Dict[str, Any]:
        """
        Complete research workflow: search + crawl.
        
        Args:
            topic: Research topic or question
            num_urls: Number of URLs to search for and potentially crawl
            crawl_content: Whether to crawl and extract content from URLs
            
        Returns:
            Dictionary with search results and crawled content
        """
        research_data = {
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'search_results': [],
            'crawled_content': [],
            'summary': {}
        }
        
        try:
            # Step 1: Search for URLs
            print(f"🔍 Searching for: {topic}")
            search_results = self.search_web(topic, num_urls)
            research_data['search_results'] = search_results
            
            if not search_results:
                research_data['summary'] = {
                    'status': 'no_results',
                    'message': 'No search results found'
                }
                return research_data
            
            # Step 2: Crawl content if requested
            if crawl_content:
                print(f"🕷️  Crawling {len(search_results)} URLs...")
                crawled_content = []
                
                for i, result in enumerate(search_results):
                    print(f"  Crawling {i+1}/{len(search_results)}: {result['url']}")
                    
                    # Add delay between requests to be respectful
                    if i > 0:
                        time.sleep(self.crawl_delay)
                    
                    crawled = self.crawl_url(result['url'])
                    crawled_content.append(crawled)
                
                research_data['crawled_content'] = crawled_content
                
                # Generate summary statistics
                successful_crawls = [c for c in crawled_content if 'content' in c and not c.get('error')]
                total_words = sum(c.get('word_count', 0) for c in successful_crawls)
                
                research_data['summary'] = {
                    'status': 'success',
                    'urls_found': len(search_results),
                    'urls_crawled': len(successful_crawls),
                    'total_words': total_words,
                    'sources': list(set(c.get('source', '') for c in successful_crawls if c.get('source')))
                }
            else:
                research_data['summary'] = {
                    'status': 'search_only',
                    'urls_found': len(search_results)
                }
            
            return research_data
            
        except Exception as e:
            research_data['summary'] = {
                'status': 'error',
                'message': str(e)
            }
            return research_data
    
    def get_content_summary(self, research_data: Dict[str, Any], max_length: int = 1000) -> str:
        """Generate a concise summary of researched content for LLM consumption."""
        if research_data['summary'].get('status') == 'error':
            return f"Research failed: {research_data['summary'].get('message')}"
        
        if not research_data.get('crawled_content'):
            # Return search results only
            results = research_data.get('search_results', [])
            summary_parts = [f"Found {len(results)} search results for '{research_data['topic']}':"]
            
            for i, result in enumerate(results[:5]):  # Top 5 results
                summary_parts.append(f"{i+1}. {result['title']} ({result['source']})")
                if result['snippet']:
                    summary_parts.append(f"   {result['snippet']}")
            
            return "\n".join(summary_parts)[:max_length]
        
        # Generate summary from crawled content
        successful_crawls = [
            c for c in research_data['crawled_content'] 
            if 'content' in c and not c.get('error') and c.get('content', '').strip()
        ]
        
        if not successful_crawls:
            return f"Could not extract content from any URLs for topic: {research_data['topic']}"
        
        summary_parts = [
            f"Research Summary for '{research_data['topic']}':",
            f"Sources: {', '.join(research_data['summary'].get('sources', []))}",
            f"Total content: {research_data['summary'].get('total_words', 0)} words",
            "",
            "Key findings:"
        ]
        
        # Add excerpts from each source
        current_length = len("\n".join(summary_parts))
        remaining_length = max_length - current_length - 100  # Buffer for formatting
        
        for i, content in enumerate(successful_crawls[:3]):  # Top 3 sources
            if remaining_length <= 0:
                break
                
            source_info = f"\nSource {i+1}: {content.get('title', 'Unknown')} ({content.get('source', '')})"
            excerpt_length = min(remaining_length // (3-i), 300)  # Distribute remaining space
            
            content_text = content.get('content', '')
            if len(content_text) > excerpt_length:
                # Try to find a good breaking point
                excerpt = content_text[:excerpt_length]
                last_sentence = excerpt.rfind('.')
                if last_sentence > excerpt_length * 0.7:  # If we can find a sentence break
                    excerpt = excerpt[:last_sentence + 1]
                excerpt += "..."
            else:
                excerpt = content_text
            
            summary_parts.append(source_info)
            summary_parts.append(excerpt)
            
            remaining_length -= len(source_info) + len(excerpt)
        
        return "\n".join(summary_parts)
    
    def clear_cache(self, older_than_hours: int = 24):
        """Clear cached research data older than specified hours."""
        if not os.path.exists(self.cache_dir):
            return
        
        cutoff_time = time.time() - (older_than_hours * 3600)
        cleared_count = 0
        
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                os.remove(file_path)
                cleared_count += 1
        
        return cleared_count


# Global instance for easy access
research_tool = ResearchTool()


# Convenience functions for easy integration
def web_search(query: str, num_results: int = 10) -> List[Dict[str, Any]]:
    """Quick web search function."""
    return research_tool.search_web(query, num_results)


def research_topic(topic: str, num_urls: int = 5, crawl: bool = True) -> Dict[str, Any]:
    """Quick research function."""
    return research_tool.research_topic(topic, num_urls, crawl)


def quick_research_summary(topic: str, max_sources: int = 3) -> str:
    """Get a quick research summary for LLM consumption."""
    research_data = research_tool.research_topic(topic, max_sources, crawl_content=True)
    return research_tool.get_content_summary(research_data)