"""Multi-provider API configuration for cost optimization."""

import os
from typing import Dict, List, Any

# Provider configurations
PROVIDER_CONFIGS = {
    "google_ai_studio": {
        "name": "Google AI Studio",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/models/",
        "models": {
            "primary": "gemini-1.5-flash",
            "premium": "gemini-1.5-pro",
            "fast": "gemini-1.5-flash-8b"
        },
        "daily_limit": 1500,
        "cost_per_request": 0.0,  # Free tier
        "speed": "medium",
        "quality": "high",
        "use_cases": ["primary_synthesis", "general_discussion"]
    },
    
    "groq": {
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1/",
        "models": {
            "primary": "llama-3.1-70b-versatile",
            "fast": "llama-3.1-8b-instant",
            "premium": "mixtral-8x7b-32768"
        },
        "daily_limit": 6000,
        "cost_per_request": 0.0,  # Currently disabled - pricing changes
        "speed": "very_fast",
        "quality": "high",
        "use_cases": ["debate", "skeptical_analysis", "creative_exploration"],
        "enabled": False
    },
    
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1/",
        "models": {
            "primary": "meta-llama/llama-3.1-8b-instruct:free",
            "fact_check": "google/gemma-2-9b-it:free",
            "backup": "microsoft/phi-3-mini-128k-instruct:free"
        },
        "daily_limit": 50,
        "cost_per_request": 0.0,  # Currently disabled - API changes
        "speed": "medium",
        "quality": "medium",
        "use_cases": ["fact_checking", "verification", "backup"],
        "enabled": False
    },
    
    "cerebras": {
        "name": "Cerebras",
        "base_url": "https://api.cerebras.ai/v1/",
        "models": {
            "primary": "llama3.1-70b",
            "analysis": "llama3.1-8b"
        },
        "daily_limit": 30,
        "cost_per_request": 0.0,  # Currently disabled - API changes
        "speed": "fast",
        "quality": "very_high",
        "use_cases": ["deep_analysis", "research", "complex_reasoning"],
        "enabled": False
    }
}

# Google account rotation setup - EXPANDED FOR MORE ACCOUNTS
GOOGLE_ACCOUNTS = [
    {
        "api_key_env": "GOOGLE_AI_STUDIO_KEY_1",
        "account_name": "primary_account",
        "daily_limit": 1500,
        "is_pro": False
    },
    {
        "api_key_env": "GOOGLE_AI_STUDIO_KEY_2", 
        "account_name": "secondary_account",
        "daily_limit": 1500,
        "is_pro": False
    },
    {
        "api_key_env": "GOOGLE_AI_STUDIO_KEY_3", 
        "account_name": "tertiary_account",
        "daily_limit": 1500,
        "is_pro": False
    },
    {
        "api_key_env": "GOOGLE_AI_STUDIO_KEY_4", 
        "account_name": "quaternary_account",
        "daily_limit": 1500,
        "is_pro": False
    },
    {
        "api_key_env": "GOOGLE_AI_STUDIO_PRO_KEY",
        "account_name": "pro_account", 
        "daily_limit": 1500,  # Pro accounts might have higher limits
        "is_pro": True
    }
]

# Agent-to-provider mapping - ALL USING GOOGLE AI STUDIO FOR NOW
AGENT_PROVIDER_MAPPING = {
    "skeptic": {
        "primary": "google_ai_studio",
        "model": "gemini-1.5-flash",
        "fallback": "google_ai_studio"
    },
    "synthesizer": {
        "primary": "google_ai_studio", 
        "model": "gemini-1.5-pro",
        "fallback": "google_ai_studio"
    },
    "analyst": {
        "primary": "google_ai_studio",
        "model": "gemini-1.5-pro", 
        "fallback": "google_ai_studio"
    },
    "explorer": {
        "primary": "google_ai_studio",
        "model": "gemini-1.5-flash",
        "fallback": "google_ai_studio"
    },
    "fact_checker": {
        "primary": "google_ai_studio",
        "model": "gemini-1.5-flash",
        "fallback": "google_ai_studio"
    }
}

# Usage quotas and limits
QUOTA_LIMITS = {
    "google_ai_studio_total": 7500,  # Up to 5 accounts × 1500 = 7500 total
    "groq": 6000,  # Currently disabled due to pricing changes
    "openrouter": 50,  # Currently disabled due to API changes
    "cerebras": 30,  # Currently disabled due to API changes
    "daily_reset_hour": 0  # UTC hour when quotas reset
}

def get_provider_config(provider_name: str) -> Dict[str, Any]:
    """Get configuration for a specific provider."""
    return PROVIDER_CONFIGS.get(provider_name, {})

def get_agent_provider(agent_type: str) -> Dict[str, str]:
    """Get the optimal provider for an agent type."""
    return AGENT_PROVIDER_MAPPING.get(agent_type, {
        "primary": "google_ai_studio",
        "model": "gemini-1.5-flash",
        "fallback": "groq"
    })

def get_google_accounts() -> List[Dict[str, Any]]:
    """Get all configured Google accounts."""
    available_accounts = []
    for account in GOOGLE_ACCOUNTS:
        api_key = os.getenv(account["api_key_env"])
        if api_key:
            account_copy = account.copy()
            account_copy["api_key"] = api_key
            available_accounts.append(account_copy)
    
    return available_accounts