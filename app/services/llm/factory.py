"""
LLM provider factory.
"""

import logging
from typing import Dict, List, Optional, Type

from app.config import settings
from app.models.schemas import PlaybookFile
from app.services.llm.base import LLMProvider
from app.services.llm.openai_provider import OpenAIProvider
from app.services.llm.ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """
    Factory for creating and managing LLM providers.
    """
    
    def __init__(self):
        """Initialize the LLM provider factory."""
        self.providers: Dict[str, Type[LLMProvider]] = {
            "openai": OpenAIProvider,
            "ollama": OllamaProvider,
        }
        self.preferred_provider = settings.PREFERRED_LLM_PROVIDER.lower()
        self._active_provider: Optional[LLMProvider] = None
    
    def get_provider(self) -> LLMProvider:
        """
        Get an LLM provider instance.
        
        Returns:
            An instance of an LLM provider
            
        Raises:
            ValueError: If no provider is available
        """
        # If we already have an active provider, return it
        if self._active_provider is not None:
            return self._active_provider
        
        # Try to use the preferred provider first
        if self.preferred_provider in self.providers:
            provider_class = self.providers[self.preferred_provider]
            provider = provider_class()
            
            if provider.is_available():
                logger.info(f"Using preferred LLM provider: {provider.get_provider_name()} with model: {provider.get_model_name()}")
                self._active_provider = provider
                return provider
            else:
                logger.warning(f"Preferred LLM provider '{self.preferred_provider}' is not available")
        
        # Try all providers in order
        for provider_name, provider_class in self.providers.items():
            if provider_name == self.preferred_provider:
                continue  # Skip the preferred provider as we already tried it
            
            provider = provider_class()
            if provider.is_available():
                logger.info(f"Using fallback LLM provider: {provider.get_provider_name()} with model: {provider.get_model_name()}")
                self._active_provider = provider
                return provider
        
        # No provider is available
        raise ValueError("No LLM provider is available. Please check your configuration.")
    
    def generate_ansible_playbook(self, description: str, additional_context: Optional[str] = None) -> List[PlaybookFile]:
        """
        Generate an Ansible playbook using the available LLM provider.
        
        Args:
            description: Natural language description of the Ansible task
            additional_context: Additional context or requirements for the playbook
            
        Returns:
            List of PlaybookFile objects representing the generated playbook files
            
        Raises:
            ValueError: If no provider is available
        """
        provider = self.get_provider()
        return provider.generate_ansible_playbook(description, additional_context)
    
    def get_available_providers(self) -> List[str]:
        """
        Get a list of available LLM providers.
        
        Returns:
            List of available provider names
        """
        available_providers = []
        
        for provider_name, provider_class in self.providers.items():
            provider = provider_class()
            if provider.is_available():
                available_providers.append(provider_name)
        
        return available_providers
    
    def reset_provider(self) -> None:
        """Reset the active provider."""
        self._active_provider = None
