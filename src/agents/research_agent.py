"""
Research-enhanced agent that can perform web searches and content analysis.
This agent can automatically research topics when mentioned in discussions.
"""

import re
from typing import Dict, List, Any, Optional
from .base_agent import BaseDiscussionAgent
from src.utils.research_tool import research_tool, quick_research_summary
from config.agent_config import AGENT_CONFIGS, MODEL_CONFIG


class ResearchAgent(BaseDiscussionAgent):
    """Agent enhanced with web research capabilities."""
    
    def __init__(self, model_config: Dict[str, Any] = None, multi_provider_client=None):
        # Use analyst configuration as base
        config = AGENT_CONFIGS["analyst"]
        
        # Enhanced system message for research capabilities
        enhanced_system_message = f"""{config["system_message"]}

RESEARCH CAPABILITIES:
You have access to a powerful research tool that can:
- Search the web using Google Custom Search API
- Crawl and extract content from web pages
- Provide summaries of research findings

When you encounter topics that would benefit from current information or fact-checking, you can:
1. Identify research-worthy topics in discussions
2. Automatically gather relevant information
3. Provide evidence-based responses

RESEARCH TRIGGERS:
Automatically research when you detect:
- Questions about current events, trends, or recent developments
- Requests for statistics, data, or factual verification  
- Topics marked with research keywords: "research this", "look up", "find information about"
- Discussions needing factual backing or recent sources

Always cite your sources and indicate when information comes from web research.
"""
        
        if model_config is None:
            model_config = {
                "model": MODEL_CONFIG["premium_model"],  # Use better model for research
                "temperature": 0.3,  # Lower temperature for factual accuracy
                "max_tokens": 800
            }
        
        super().__init__(
            name="Research Analyst",
            role="Research-Enhanced Analyst", 
            system_message=enhanced_system_message,
            agent_type="analyst",  # Use analyst provider mapping
            model_config=model_config,
            multi_provider_client=multi_provider_client
        )
        
        self.research_triggers = [
            r"research\s+(this|that|about)",
            r"look\s+up",
            r"find\s+information\s+about",
            r"what\s+(are\s+the\s+)?latest",
            r"current\s+(trends|data|statistics)",
            r"recent\s+(developments|studies|reports)",
            r"verify\s+(this|that)",
            r"fact[- ]check",
            r"is\s+it\s+true\s+that",
            r"according\s+to\s+sources?"
        ]
    
    def _should_research(self, context: str, previous_messages: List[str] = None) -> List[str]:
        """
        Determine if research is needed and extract research topics.
        Returns list of topics to research.
        """
        topics = []
        
        # Check context for research triggers
        context_lower = context.lower()
        for trigger in self.research_triggers:
            if re.search(trigger, context_lower):
                # Extract potential research topics
                topics.extend(self._extract_research_topics(context))
                break
        
        # Check recent messages for research requests
        if previous_messages:
            recent_text = " ".join(previous_messages[-3:]).lower()
            for trigger in self.research_triggers:
                if re.search(trigger, recent_text):
                    topics.extend(self._extract_research_topics(recent_text))
                    break
        
        return list(set(topics))  # Remove duplicates
    
    def _extract_research_topics(self, text: str) -> List[str]:
        """Extract potential research topics from text."""
        topics = []
        
        # Pattern matching for research topics
        patterns = [
            r"research\s+(about\s+)?([^.!?]+)",
            r"look\s+up\s+([^.!?]+)",
            r"find\s+information\s+about\s+([^.!?]+)",
            r"latest\s+(on\s+)?([^.!?]+)",
            r"current\s+([^.!?]+)",
            r"recent\s+([^.!?]+)\s+(in|about)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    topic = " ".join(match).strip()
                else:
                    topic = match.strip()
                
                if topic and len(topic) > 3:  # Minimum topic length
                    # Clean up topic
                    topic = re.sub(r'^(about|on|in)\s+', '', topic, flags=re.IGNORECASE)
                    topic = topic.strip(' .,!?')
                    if topic:
                        topics.append(topic)
        
        # If no specific topics found, try to extract key nouns/phrases
        if not topics:
            # Look for capitalized terms that might be topics
            capitalized_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            topics.extend(capitalized_terms[:2])  # Limit to avoid noise
        
        return topics[:3]  # Limit to 3 topics max
    
    def _conduct_research(self, topics: List[str]) -> Dict[str, Any]:
        """Conduct research on the given topics."""
        if not research_tool.is_configured():
            return {
                'status': 'not_configured',
                'message': 'Research tool not configured. ' + research_tool.get_config_instructions()
            }
        
        research_results = {}
        
        for topic in topics[:2]:  # Limit to 2 topics to avoid overwhelming
            try:
                print(f"🔍 Researching: {topic}")
                
                # Get quick research summary
                summary = quick_research_summary(topic, max_sources=3)
                research_results[topic] = {
                    'status': 'success',
                    'summary': summary
                }
                
            except Exception as e:
                research_results[topic] = {
                    'status': 'error',
                    'message': str(e)
                }
        
        return research_results
    
    def generate_response(self, context: str, previous_messages: List[str] = None) -> str:
        """Generate response with optional research enhancement."""
        # Check if research is needed
        research_topics = self._should_research(context, previous_messages)
        
        research_context = ""
        if research_topics and research_tool.is_configured():
            try:
                # Conduct research
                research_results = self._conduct_research(research_topics)
                
                # Add research findings to context
                research_parts = ["=== RESEARCH FINDINGS ==="]
                for topic, result in research_results.items():
                    if result['status'] == 'success':
                        research_parts.append(f"\nTopic: {topic}")
                        research_parts.append(result['summary'])
                    else:
                        research_parts.append(f"\nCould not research '{topic}': {result.get('message', 'Unknown error')}")
                
                research_parts.append("\n=== END RESEARCH ===\n")
                research_context = "\n".join(research_parts)
                
            except Exception as e:
                research_context = f"\n[Research Error: {e}]\n"
        
        # Combine original context with research
        enhanced_context = context
        if research_context:
            enhanced_context = f"{context}\n\n{research_context}"
        
        # Generate response using parent method
        base_response = super().generate_response(enhanced_context, previous_messages)
        
        # Add research indicator if research was performed
        if research_context and not base_response.startswith("[RESEARCH"):
            base_response = f"[RESEARCH ANALYST] {base_response}"
        
        return base_response
    
    def research_topic_manually(self, topic: str) -> str:
        """Manually research a topic and return formatted results."""
        if not research_tool.is_configured():
            return research_tool.get_config_instructions()
        
        try:
            summary = quick_research_summary(topic, max_sources=3)
            return f"Research Results for '{topic}':\n\n{summary}"
        except Exception as e:
            return f"Research failed: {e}"


class SmartDiscussionManager:
    """Enhanced discussion manager that can automatically invoke research."""
    
    def __init__(self, agents: Dict[str, BaseDiscussionAgent]):
        self.agents = agents
        self.research_agent = None
        
        # Try to create a research agent
        try:
            if research_tool.is_configured():
                self.research_agent = ResearchAgent()
                print("✅ Research Agent enabled")
            else:
                print("⚠️  Research Agent disabled - configuration needed")
        except Exception as e:
            print(f"⚠️  Research Agent disabled - {e}")
    
    def should_trigger_research(self, message: str) -> bool:
        """Determine if a message should trigger automatic research."""
        triggers = [
            "research this",
            "look this up", 
            "find information",
            "what are the latest",
            "current statistics",
            "recent data",
            "verify this",
            "is this accurate",
            "according to sources"
        ]
        
        message_lower = message.lower()
        return any(trigger in message_lower for trigger in triggers)
    
    def get_research_enhanced_response(self, agent_type: str, context: str, 
                                     previous_messages: List[str] = None) -> str:
        """Get response from agent, with research enhancement if needed."""
        
        # If research should be triggered and research agent is available
        if (self.should_trigger_research(context) and 
            self.research_agent and 
            agent_type in ["analyst", "synthesizer"]):
            
            # Use research agent instead
            return self.research_agent.generate_response(context, previous_messages)
        
        # Use regular agent
        if agent_type in self.agents:
            return self.agents[agent_type].generate_response(context, previous_messages)
        
        return f"[{agent_type.upper()}] Agent not available"