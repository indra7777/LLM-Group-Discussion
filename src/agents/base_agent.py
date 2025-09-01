"""Base agent class for the multi-agent discussion system."""

from typing import Dict, List, Optional, Any
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables directly.")

OpenAIModel = None

try:
    # Try new autogen structure first  
    from autogen_agentchat.agents import AssistantAgent
    from autogen_ext.models.openai import OpenAIChatCompletionClient as OpenAIModel
    AUTOGEN_NEW = True
    ConversableAgent = AssistantAgent
except ImportError:
    try:
        # Try alternative new structure
        from autogen_agentchat import ConversableAgent
        from autogen_ext.models import OpenAIModel
        AUTOGEN_NEW = True
    except ImportError:
        try:
            # Fallback to old structure
            from autogen import ConversableAgent
            AUTOGEN_NEW = False
        except ImportError:
            try:
                # Try pyautogen
                import pyautogen as autogen
                ConversableAgent = autogen.ConversableAgent
                AUTOGEN_NEW = False
            except ImportError:
                print("Warning: AutoGen not installed. Please install autogen-agentchat or pyautogen.")
                ConversableAgent = None


class BaseDiscussionAgent:
    """Base class for all discussion agents in the system."""
    
    def __init__(self, 
                 name: str,
                 role: str, 
                 system_message: str,
                 agent_type: str = "general",
                 model_config: Dict[str, Any] = None,
                 multi_provider_client = None):
        self.name = name
        self.role = role
        self.system_message = system_message
        self.agent_type = agent_type
        self.conversation_history = []
        self.multi_provider_client = multi_provider_client
        
        # Default model configuration
        if model_config is None:
            model_config = {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "temperature": 0.7,
                "max_tokens": 500
            }
        
        self.model_config = model_config
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Optional[Any]:
        """Create the underlying AutoGen agent."""
        if ConversableAgent is None:
            return None
            
        try:
            if AUTOGEN_NEW and OpenAIModel is not None:
                # New autogen structure
                model = OpenAIModel(
                    model=self.model_config["model"],
                    api_key=self.model_config["api_key"]
                )
                
                agent = ConversableAgent(
                    name=self.name,
                    model_client=model,
                    system_message=self.system_message
                )
            else:
                # Old autogen structure
                agent = ConversableAgent(
                    name=self.name,
                    system_message=self.system_message,
                    llm_config={
                        "config_list": [{
                            "model": self.model_config["model"],
                            "api_key": self.model_config["api_key"],
                            "temperature": self.model_config.get("temperature", 0.7),
                            "max_tokens": self.model_config.get("max_tokens", 500)
                        }]
                    },
                    human_input_mode="NEVER",
                    max_consecutive_auto_reply=1
                )
            
            return agent
            
        except Exception as e:
            print(f"Warning: Could not create AutoGen agent for {self.name}: {e}")
            return None
    
    def generate_response(self, context: str, previous_messages: List[str] = None) -> str:
        """Generate a response based on the current context and conversation history."""
        # Try multi-provider client first
        if self.multi_provider_client:
            try:
                return self._generate_with_multi_provider(context, previous_messages)
            except Exception as e:
                print(f"Multi-provider failed for {self.name}: {e}")
                # Fall through to AutoGen backup
        
        # Fallback to AutoGen
        if self.agent is None:
            # Final fallback: simple response
            return f"[{self.role.upper()}] I need to respond to: {context[:100]}..."
        
        try:
            if previous_messages:
                full_context = f"Discussion context: {context}\n\nPrevious messages:\n"
                full_context += "\n".join(previous_messages[-3:])  # Last 3 messages for context
            else:
                full_context = f"Discussion context: {context}"
            
            if AUTOGEN_NEW:
                # New autogen API
                response = self.agent.generate_reply([{"content": full_context, "role": "user"}])
                return response.content if hasattr(response, 'content') else str(response)
            else:
                # Old autogen API  
                response = self.agent.generate_reply([{"content": full_context, "role": "user"}])
                return response if isinstance(response, str) else str(response)
                
        except Exception as e:
            print(f"Error generating response for {self.name}: {e}")
            return f"[{self.role.upper()}] I'm having technical difficulties. Please try again."
    
    def _generate_with_multi_provider(self, context: str, previous_messages: List[str] = None) -> str:
        """Generate response using the multi-provider client."""
        # Prepare messages for the API
        messages = [
            {"role": "system", "content": self.system_message}
        ]
        
        if previous_messages:
            full_context = f"Discussion context: {context}\n\nPrevious messages:\n"
            full_context += "\n".join(previous_messages[-3:])
        else:
            full_context = f"Discussion context: {context}"
        
        messages.append({"role": "user", "content": full_context})
        
        # Generate response using multi-provider
        response_text, provider_used = self.multi_provider_client.generate_response(
            agent_type=self.agent_type,
            messages=messages,
            temperature=self.model_config.get("temperature", 0.7),
            max_tokens=self.model_config.get("max_tokens", 500)
        )
        
        # Add provider info for debugging (can be removed in production)
        # print(f"  {self.name} used {provider_used}")
        
        return response_text
    
    def add_to_history(self, message: str, is_own_message: bool = False):
        """Add a message to the agent's conversation history."""
        self.conversation_history.append({
            "message": message,
            "is_own": is_own_message,
            "agent": self.name if is_own_message else "other"
        })
    
    def get_summary(self) -> str:
        """Get a summary of the agent's perspective on the discussion."""
        if not self.conversation_history:
            return f"{self.name} has not participated in the discussion yet."
        
        recent_messages = [msg["message"] for msg in self.conversation_history[-5:]]
        return f"{self.name} ({self.role}) has contributed {len([m for m in self.conversation_history if m['is_own']])} messages."
    
    def reset_history(self):
        """Clear the conversation history."""
        self.conversation_history = []