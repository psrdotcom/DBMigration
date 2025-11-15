"""
Base agent class with LLM integration.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    AZURE_OPENAI = "azure_openai"


class BaseAgent(ABC):
    """Base class for all agents with LLM capabilities."""
    
    def __init__(self, name: str, provider: LLMProvider = None, model: str = None):
        self.name = name
        self.provider = provider or self._get_default_provider()
        self.model = model or self._get_default_model()
        self.llm_client = self._initialize_llm()
    
    def _get_default_provider(self) -> LLMProvider:
        """Get default LLM provider from environment."""
        provider_str = os.getenv('LLM_PROVIDER', 'openai').lower()
        try:
            return LLMProvider(provider_str)
        except ValueError:
            logger.warning(f"Unknown provider {provider_str}, defaulting to OpenAI")
            return LLMProvider.OPENAI
    
    def _get_default_model(self) -> str:
        """Get default model based on provider."""
        provider_models = {
            LLMProvider.OPENAI: os.getenv('OPENAI_MODEL', 'gpt-4'),
            LLMProvider.ANTHROPIC: os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229'),
            LLMProvider.OLLAMA: os.getenv('OLLAMA_MODEL', 'llama2'),
            LLMProvider.AZURE_OPENAI: os.getenv('AZURE_OPENAI_MODEL', 'gpt-4'),
        }
        return provider_models.get(self.provider, 'gpt-4')
    
    def _initialize_llm(self):
        """Initialize LLM client based on provider."""
        try:
            if self.provider == LLMProvider.OPENAI:
                from openai import OpenAI
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    logger.warning("OPENAI_API_KEY not set, LLM features will be disabled")
                    return None
                return OpenAI(api_key=api_key)
            
            elif self.provider == LLMProvider.ANTHROPIC:
                from anthropic import Anthropic
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if not api_key:
                    logger.warning("ANTHROPIC_API_KEY not set, LLM features will be disabled")
                    return None
                return Anthropic(api_key=api_key)
            
            elif self.provider == LLMProvider.OLLAMA:
                from openai import OpenAI
                base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1')
                return OpenAI(base_url=base_url, api_key='ollama')
            
            elif self.provider == LLMProvider.AZURE_OPENAI:
                from openai import AzureOpenAI
                return AzureOpenAI(
                    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                    api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'),
                    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
                )
            
            return None
        except ImportError as e:
            logger.warning(f"LLM library not installed for {self.provider.value}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            return None
    
    def call_llm(self, prompt: str, system_prompt: Optional[str] = None, 
                 temperature: float = 0.3, max_tokens: int = 2000) -> Optional[str]:
        """
        Call LLM with a prompt.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLM response or None if LLM is unavailable
        """
        if not self.llm_client:
            logger.warning("LLM client not available, returning None")
            return None
        
        try:
            if self.provider == LLMProvider.ANTHROPIC:
                messages = []
                if system_prompt:
                    messages.append({"role": "user", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self.llm_client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=messages
                )
                return response.content[0].text if response.content else None
            
            else:  # OpenAI, Ollama, Azure OpenAI
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self.llm_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content if response.choices else None
        
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return None
    
    @abstractmethod
    def can_handle(self, task: Dict[str, Any]) -> bool:
        """
        Check if this agent can handle the given task.
        
        Args:
            task: Task description dictionary
            
        Returns:
            True if agent can handle the task
        """
        pass
    
    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the task.
        
        Args:
            task: Task description dictionary
            
        Returns:
            Result dictionary with status and data
        """
        pass
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this agent provides."""
        return []

