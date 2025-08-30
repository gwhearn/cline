"""
Base class for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.schemas import PlaybookFile


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    This class defines the interface that all LLM providers must implement.
    """
    
    @abstractmethod
    def generate_ansible_playbook(self, description: str, additional_context: Optional[str] = None) -> List[PlaybookFile]:
        """
        Generate an Ansible playbook from a natural language description.
        
        Args:
            description: Natural language description of the Ansible task
            additional_context: Additional context or requirements for the playbook
            
        Returns:
            List of PlaybookFile objects representing the generated playbook files
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of the LLM provider.
        
        Returns:
            Name of the LLM provider
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the model being used.
        
        Returns:
            Name of the model
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the LLM provider is available.
        
        Returns:
            True if the provider is available, False otherwise
        """
        pass
