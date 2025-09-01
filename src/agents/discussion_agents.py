"""Specialized agent implementations for the multi-agent discussion system."""

from typing import Dict, List, Any
from .base_agent import BaseDiscussionAgent
from config.agent_config import AGENT_CONFIGS, MODEL_CONFIG


class SkepticalAgent(BaseDiscussionAgent):
    """Agent focused on critical analysis and questioning assumptions."""
    
    def __init__(self, model_config: Dict[str, Any] = None, multi_provider_client=None):
        config = AGENT_CONFIGS["skeptic"]
        if model_config is None:
            model_config = {
                "model": MODEL_CONFIG["primary_model"],
                "temperature": config["temperature"],
                "max_tokens": config["max_tokens"]
            }
        
        super().__init__(
            name=config["name"],
            role=config["role"], 
            system_message=config["system_message"],
            agent_type="skeptic",
            model_config=model_config,
            multi_provider_client=multi_provider_client
        )
    
    def generate_response(self, context: str, previous_messages: List[str] = None) -> str:
        """Generate a skeptical analysis of the current discussion."""
        base_response = super().generate_response(context, previous_messages)
        
        # Ensure response starts with role identifier
        if not base_response.startswith("[SKEPTIC]"):
            base_response = f"[SKEPTIC] {base_response}"
        
        return base_response


class SynthesizerAgent(BaseDiscussionAgent):
    """Agent focused on finding connections and building consensus."""
    
    def __init__(self, model_config: Dict[str, Any] = None, multi_provider_client=None):
        config = AGENT_CONFIGS["synthesizer"]
        if model_config is None:
            model_config = {
                "model": MODEL_CONFIG["premium_model"],  # Use better model for synthesis
                "temperature": config["temperature"],
                "max_tokens": config["max_tokens"]
            }
        
        super().__init__(
            name=config["name"],
            role=config["role"],
            system_message=config["system_message"],
            agent_type="synthesizer",
            model_config=model_config,
            multi_provider_client=multi_provider_client
        )
    
    def generate_response(self, context: str, previous_messages: List[str] = None) -> str:
        """Generate a synthesizing response that builds on previous contributions."""
        base_response = super().generate_response(context, previous_messages)
        
        if not base_response.startswith("[SYNTHESIZER]"):
            base_response = f"[SYNTHESIZER] {base_response}"
        
        return base_response


class AnalyticalAgent(BaseDiscussionAgent):
    """Agent focused on data-driven analysis and fact-checking."""
    
    def __init__(self, model_config: Dict[str, Any] = None, multi_provider_client=None):
        config = AGENT_CONFIGS["analyst"]
        if model_config is None:
            model_config = {
                "model": MODEL_CONFIG["primary_model"],
                "temperature": config["temperature"],
                "max_tokens": config["max_tokens"]
            }
        
        super().__init__(
            name=config["name"],
            role=config["role"],
            system_message=config["system_message"],
            agent_type="analyst",
            model_config=model_config,
            multi_provider_client=multi_provider_client
        )
    
    def generate_response(self, context: str, previous_messages: List[str] = None) -> str:
        """Generate an analytical, data-focused response."""
        base_response = super().generate_response(context, previous_messages)
        
        if not base_response.startswith("[ANALYST]"):
            base_response = f"[ANALYST] {base_response}"
        
        return base_response


class ExploratoryAgent(BaseDiscussionAgent):
    """Agent focused on creative thinking and novel perspectives."""
    
    def __init__(self, model_config: Dict[str, Any] = None, multi_provider_client=None):
        config = AGENT_CONFIGS["explorer"]
        if model_config is None:
            model_config = {
                "model": MODEL_CONFIG["primary_model"],
                "temperature": config["temperature"],  # Higher temperature for creativity
                "max_tokens": config["max_tokens"]
            }
        
        super().__init__(
            name=config["name"],
            role=config["role"],
            system_message=config["system_message"],
            agent_type="explorer",
            model_config=model_config,
            multi_provider_client=multi_provider_client
        )
    
    def generate_response(self, context: str, previous_messages: List[str] = None) -> str:
        """Generate a creative, exploratory response."""
        base_response = super().generate_response(context, previous_messages)
        
        if not base_response.startswith("[EXPLORER]"):
            base_response = f"[EXPLORER] {base_response}"
        
        return base_response


class AgentFactory:
    """Factory class for creating discussion agents."""
    
    @staticmethod
    def create_agent(agent_type: str, model_config: Dict[str, Any] = None, 
                    multi_provider_client=None) -> BaseDiscussionAgent:
        """Create an agent of the specified type."""
        agent_classes = {
            "skeptic": SkepticalAgent,
            "synthesizer": SynthesizerAgent, 
            "analyst": AnalyticalAgent,
            "explorer": ExploratoryAgent
        }
        
        if agent_type not in agent_classes:
            raise ValueError(f"Unknown agent type: {agent_type}. Available types: {list(agent_classes.keys())}")
        
        return agent_classes[agent_type](model_config, multi_provider_client)
    
    @staticmethod
    def create_all_agents(model_config: Dict[str, Any] = None, 
                         multi_provider_client=None) -> Dict[str, BaseDiscussionAgent]:
        """Create all four standard discussion agents."""
        return {
            "skeptic": AgentFactory.create_agent("skeptic", model_config, multi_provider_client),
            "synthesizer": AgentFactory.create_agent("synthesizer", model_config, multi_provider_client),
            "analyst": AgentFactory.create_agent("analyst", model_config, multi_provider_client),
            "explorer": AgentFactory.create_agent("explorer", model_config, multi_provider_client)
        }