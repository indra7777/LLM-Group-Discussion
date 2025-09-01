"""Multi-provider API client with intelligent routing and quota management."""

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests library not available. Multi-provider functionality disabled.")

import time
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from config.provider_config import (
    PROVIDER_CONFIGS, AGENT_PROVIDER_MAPPING, 
    QUOTA_LIMITS, get_google_accounts
)


@dataclass
class UsageStats:
    """Track API usage statistics."""
    provider: str
    requests_made: int = 0
    requests_failed: int = 0
    last_reset: datetime = field(default_factory=datetime.now)
    total_cost: float = 0.0
    
    def reset_daily(self):
        """Reset daily counters."""
        self.requests_made = 0
        self.requests_failed = 0
        self.last_reset = datetime.now()


class MultiProviderClient:
    """Client that manages multiple API providers with intelligent routing."""
    
    def __init__(self):
        if not REQUESTS_AVAILABLE:
            raise Exception("Requests library required for multi-provider functionality")
        
        self.usage_stats = {}
        self.google_account_index = 0
        self.google_accounts = get_google_accounts()
        
        # Initialize usage stats for all providers
        for provider in PROVIDER_CONFIGS.keys():
            self.usage_stats[provider] = UsageStats(provider)
    
    def _check_daily_reset(self):
        """Check if daily quotas should be reset."""
        now = datetime.now()
        reset_hour = QUOTA_LIMITS.get("daily_reset_hour", 0)
        
        for stats in self.usage_stats.values():
            last_reset = stats.last_reset
            reset_time = datetime(now.year, now.month, now.day, reset_hour)
            
            # If it's past reset time and we haven't reset today
            if now >= reset_time and last_reset < reset_time:
                stats.reset_daily()
    
    def _get_google_api_key(self) -> Optional[str]:
        """Get Google API key with account rotation."""
        if not self.google_accounts:
            return os.getenv("GOOGLE_AI_STUDIO_KEY", os.getenv("GOOGLE_API_KEY"))
        
        # Rotate through accounts
        account = self.google_accounts[self.google_account_index]
        self.google_account_index = (self.google_account_index + 1) % len(self.google_accounts)
        
        return account.get("api_key")
    
    def _can_use_provider(self, provider_name: str) -> bool:
        """Check if provider is available and within quota."""
        self._check_daily_reset()
        
        provider_config = PROVIDER_CONFIGS.get(provider_name)
        if not provider_config:
            return False
        
        # Check if provider is enabled
        if not provider_config.get("enabled", True):
            return False
        
        usage = self.usage_stats.get(provider_name)
        if not usage:
            return False
        
        # Check quota limits
        daily_limit = provider_config.get("daily_limit", float('inf'))
        if usage.requests_made >= daily_limit:
            return False
        
        # Check if API key is available
        if provider_name == "google_ai_studio":
            return self._get_google_api_key() is not None
        elif provider_name == "groq":
            return os.getenv("GROQ_API_KEY") is not None
        elif provider_name == "openrouter":
            return os.getenv("OPENROUTER_API_KEY") is not None
        elif provider_name == "cerebras":
            return os.getenv("CEREBRAS_API_KEY") is not None
        
        return False
    
    def _make_google_request(self, model: str, messages: List[Dict], **kwargs) -> Dict:
        """Make request to Google AI Studio."""
        api_key = self._get_google_api_key()
        if not api_key:
            raise Exception("Google AI Studio API key not found")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        # Convert messages to Google format
        contents = []
        for msg in messages:
            if msg.get("role") == "user":
                contents.append({"parts": [{"text": msg["content"]}]})
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 500)
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(
            f"{url}?key={api_key}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Extract text from Google response
        candidates = result.get("candidates", [])
        if candidates and "content" in candidates[0]:
            text = candidates[0]["content"]["parts"][0]["text"]
            return {"choices": [{"message": {"content": text}}]}
        
        raise Exception("No response content from Google AI Studio")
    
    def _make_openai_compatible_request(self, provider_name: str, model: str, 
                                      messages: List[Dict], **kwargs) -> Dict:
        """Make request to OpenAI-compatible providers (Groq, OpenRouter, Cerebras)."""
        provider_config = PROVIDER_CONFIGS[provider_name]
        
        # Get API key
        if provider_name == "groq":
            api_key = os.getenv("GROQ_API_KEY")
        elif provider_name == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY")
        elif provider_name == "cerebras":
            api_key = os.getenv("CEREBRAS_API_KEY")
        else:
            raise Exception(f"Unknown provider: {provider_name}")
        
        if not api_key:
            raise Exception(f"{provider_name} API key not found")
        
        url = f"{provider_config['base_url']}chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 500)
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Add provider-specific headers
        if provider_name == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/your-repo/llm-gd"
            headers["X-Title"] = "Multi-Agent Discussion System"
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    def generate_response(self, agent_type: str, messages: List[Dict], 
                         **kwargs) -> Tuple[str, str]:
        """Generate response using the optimal provider for the agent type."""
        self._check_daily_reset()
        
        # Get provider configuration for this agent
        agent_config = AGENT_PROVIDER_MAPPING.get(agent_type, {})
        primary_provider = agent_config.get("primary", "google_ai_studio")
        fallback_provider = agent_config.get("fallback", "google_ai_studio")
        model = agent_config.get("model", "gemini-1.5-flash")
        
        # Try primary provider first
        providers_to_try = [primary_provider, fallback_provider]
        
        for provider_name in providers_to_try:
            if not self._can_use_provider(provider_name):
                continue
            
            try:
                # Update usage stats
                usage = self.usage_stats[provider_name]
                usage.requests_made += 1
                
                # Make the request
                if provider_name == "google_ai_studio":
                    # Use Google-specific model
                    google_model = PROVIDER_CONFIGS[provider_name]["models"].get("primary", model)
                    result = self._make_google_request(google_model, messages, **kwargs)
                else:
                    # Use provider-specific model
                    provider_model = PROVIDER_CONFIGS[provider_name]["models"].get("primary", model)
                    result = self._make_openai_compatible_request(
                        provider_name, provider_model, messages, **kwargs
                    )
                
                # Extract response text
                response_text = result["choices"][0]["message"]["content"]
                
                return response_text, provider_name
                
            except Exception as e:
                print(f"Error with {provider_name}: {e}")
                usage.requests_failed += 1
                continue
        
        # If all providers failed, return error
        raise Exception("All API providers failed or quota exceeded")
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get current usage summary across all providers."""
        self._check_daily_reset()
        
        summary = {
            "total_requests": sum(stats.requests_made for stats in self.usage_stats.values()),
            "total_failures": sum(stats.requests_failed for stats in self.usage_stats.values()),
            "providers": {}
        }
        
        for provider_name, stats in self.usage_stats.items():
            provider_config = PROVIDER_CONFIGS.get(provider_name, {})
            daily_limit = provider_config.get("daily_limit", 0)
            
            summary["providers"][provider_name] = {
                "requests_made": stats.requests_made,
                "requests_failed": stats.requests_failed,
                "daily_limit": daily_limit,
                "remaining": max(0, daily_limit - stats.requests_made),
                "success_rate": (
                    (stats.requests_made - stats.requests_failed) / max(1, stats.requests_made) * 100
                ),
                "available": self._can_use_provider(provider_name)
            }
        
        return summary
    
    def get_cost_estimate(self) -> Dict[str, float]:
        """Get cost estimates (should be $0 with free tiers)."""
        total_cost = 0.0
        provider_costs = {}
        
        for provider_name, stats in self.usage_stats.items():
            provider_config = PROVIDER_CONFIGS.get(provider_name, {})
            cost_per_request = provider_config.get("cost_per_request", 0.0)
            provider_cost = stats.requests_made * cost_per_request
            
            provider_costs[provider_name] = provider_cost
            total_cost += provider_cost
        
        return {
            "total_daily_cost": total_cost,
            "providers": provider_costs,
            "monthly_estimate": total_cost * 30
        }