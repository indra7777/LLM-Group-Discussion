"""Demo agents that work without API keys for testing purposes."""

import random
import time
from typing import List
from .base_agent import BaseDiscussionAgent


class DemoAgent(BaseDiscussionAgent):
    """Demo agent that generates simulated responses without API calls."""
    
    def __init__(self, name: str, role: str, system_message: str, response_templates: List[str]):
        # Initialize without model config to avoid API calls
        super().__init__(name, role, system_message, model_config=None)
        self.response_templates = response_templates
        
    def generate_response(self, context: str, previous_messages: List[str] = None) -> str:
        """Generate a simulated response using templates."""
        # Simulate thinking time
        time.sleep(random.uniform(0.5, 2.0))
        
        # Select a random template and customize it
        template = random.choice(self.response_templates)
        
        # Extract topic from context
        topic = "this topic"
        if "Topic:" in context:
            topic_line = [line for line in context.split('\n') if line.startswith("Topic:")][0]
            topic = topic_line.replace("Topic:", "").strip()
        
        # Customize template with context
        response = template.format(topic=topic, context=context[:100])
        
        return response


class DemoSkepticalAgent(DemoAgent):
    """Demo version of the skeptical agent."""
    
    def __init__(self):
        templates = [
            "[SKEPTIC] I question the assumptions underlying {topic}. What evidence supports this position?",
            "[SKEPTIC] This raises several red flags. Have we considered the potential downsides of {topic}?",
            "[SKEPTIC] I'm not convinced by this argument. What alternative explanations might exist?",
            "[SKEPTIC] The claims about {topic} seem overstated. What data backs this up?",
            "[SKEPTIC] Before accepting this, we should examine the methodology behind these conclusions.",
            "[SKEPTIC] This appears to suffer from confirmation bias. What contradictory evidence exists?"
        ]
        
        super().__init__(
            name="Dr. Skeptic",
            role="Critical Analyst", 
            system_message="Demo skeptical agent",
            response_templates=templates
        )


class DemoSynthesizerAgent(DemoAgent):
    """Demo version of the synthesizer agent."""
    
    def __init__(self):
        templates = [
            "[SYNTHESIZER] I see interesting connections between the points raised about {topic}.",
            "[SYNTHESIZER] Building on the previous discussion, we might find common ground in {topic}.",
            "[SYNTHESIZER] These different perspectives on {topic} can be reconciled if we consider...",
            "[SYNTHESIZER] The various viewpoints about {topic} actually complement each other in several ways.",
            "[SYNTHESIZER] Let me weave together the insights shared about {topic} into a coherent framework.",
            "[SYNTHESIZER] I notice patterns emerging from our discussion of {topic} that suggest..."
        ]
        
        super().__init__(
            name="Dr. Synthesis",
            role="Integrative Thinker",
            system_message="Demo synthesizer agent", 
            response_templates=templates
        )


class DemoAnalyticalAgent(DemoAgent):
    """Demo version of the analytical agent."""
    
    def __init__(self):
        templates = [
            "[ANALYST] The data on {topic} shows significant trends that we should consider.",
            "[ANALYST] According to recent studies, {topic} demonstrates measurable impacts of 23% improvement.",
            "[ANALYST] Statistical analysis reveals that {topic} correlates with three key factors.",
            "[ANALYST] Research indicates that {topic} follows a predictable pattern across different contexts.",
            "[ANALYST] The empirical evidence for {topic} suggests we need longitudinal data to verify.",
            "[ANALYST] Quantitative analysis of {topic} reveals gaps in our current understanding."
        ]
        
        super().__init__(
            name="Dr. Data",
            role="Evidence-Based Researcher",
            system_message="Demo analytical agent",
            response_templates=templates
        )


class DemoExploratoryAgent(DemoAgent):
    """Demo version of the exploratory agent."""
    
    def __init__(self):
        templates = [
            "[EXPLORER] What if we approached {topic} from a completely different angle?",
            "[EXPLORER] Imagine if {topic} could be reimagined using principles from nature...",
            "[EXPLORER] I envision a future where {topic} transforms into something revolutionary.",
            "[EXPLORER] Consider this wild possibility: what if {topic} actually works in reverse?",
            "[EXPLORER] Let's think outside the box - could {topic} be the key to solving unexpected problems?",
            "[EXPLORER] Here's an unconventional idea about {topic} inspired by quantum mechanics..."
        ]
        
        super().__init__(
            name="Dr. Discovery", 
            role="Creative Visionary",
            system_message="Demo exploratory agent",
            response_templates=templates
        )


class DemoAgentFactory:
    """Factory for creating demo agents."""
    
    @staticmethod
    def create_agent(agent_type: str):
        """Create a demo agent of the specified type."""
        agent_classes = {
            "skeptic": DemoSkepticalAgent,
            "synthesizer": DemoSynthesizerAgent,
            "analyst": DemoAnalyticalAgent, 
            "explorer": DemoExploratoryAgent
        }
        
        if agent_type not in agent_classes:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        return agent_classes[agent_type]()
    
    @staticmethod
    def create_all_agents():
        """Create all demo agents."""
        return {
            "skeptic": DemoAgentFactory.create_agent("skeptic"),
            "synthesizer": DemoAgentFactory.create_agent("synthesizer"),
            "analyst": DemoAgentFactory.create_agent("analyst"),
            "explorer": DemoAgentFactory.create_agent("explorer")
        }