"""
Ollama provider implementation.
"""

import json
import logging
import httpx
from typing import List, Optional, Dict, Any

from pydantic import ValidationError

from app.config import settings
from app.models.schemas import PlaybookFile
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """
    Ollama provider implementation.
    
    This provider uses the Ollama API to generate Ansible playbooks using locally hosted models.
    """
    
    def __init__(self):
        """Initialize the Ollama provider."""
        self.api_base = settings.OLLAMA_API_BASE
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
    
    def generate_ansible_playbook(self, description: str, additional_context: Optional[str] = None) -> List[PlaybookFile]:
        """
        Generate an Ansible playbook from a natural language description using Ollama.
        
        Args:
            description: Natural language description of the Ansible task
            additional_context: Additional context or requirements for the playbook
            
        Returns:
            List of PlaybookFile objects representing the generated playbook files
        """
        try:
            # Construct the prompt
            prompt = self._construct_prompt(description, additional_context)
            system_prompt = self._get_system_prompt()
            
            # Prepare the request payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "top_p": 1.0,
                    "num_predict": 4000,
                }
            }
            
            # Call the Ollama API
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.api_base}/api/generate", json=payload)
                response.raise_for_status()
                result = response.json()
            
            # Extract and parse the response
            content = result.get("response", "")
            return self._parse_response(content)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when calling Ollama API: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"Ollama API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Error making request to Ollama API: {str(e)}")
            raise ValueError(f"Failed to connect to Ollama API: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating Ansible playbook with Ollama: {str(e)}")
            raise
    
    def get_provider_name(self) -> str:
        """
        Get the name of the LLM provider.
        
        Returns:
            Name of the LLM provider
        """
        return "Ollama"
    
    def get_model_name(self) -> str:
        """
        Get the name of the model being used.
        
        Returns:
            Name of the model
        """
        return self.model
    
    def is_available(self) -> bool:
        """
        Check if the Ollama provider is available.
        
        Returns:
            True if the provider is available, False otherwise
        """
        if not self.api_base:
            logger.warning("Ollama API base URL is not set")
            return False
        
        try:
            # Make a simple API call to check if Ollama is running
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.api_base}/api/tags")
                response.raise_for_status()
                
                # Check if the specified model is available
                models = response.json().get("models", [])
                model_names = [model.get("name") for model in models]
                
                if self.model not in model_names:
                    logger.warning(f"Ollama model '{self.model}' is not available. Available models: {', '.join(model_names)}")
                    return False
                
                return True
        except Exception as e:
            logger.warning(f"Ollama provider is not available: {str(e)}")
            return False
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Ollama API."""
        return """
        You are an expert Ansible playbook generator. Your task is to create complete, valid Ansible playbooks based on natural language descriptions.
        
        Follow these guidelines:
        1. Create all necessary files for a complete Ansible playbook, including main playbook YAML, roles, tasks, handlers, templates, etc.
        2. Use best practices for Ansible playbook structure and organization.
        3. Include comments to explain complex tasks or configurations.
        4. Ensure the playbook is idempotent and follows Ansible lint rules.
        5. Return your response in a structured JSON format with each file as a separate object.
        
        Your response must be a valid JSON array where each object has the following properties:
        - filename: The name of the file
        - content: The complete content of the file
        - path: The relative path within the playbook structure
        
        Example response format:
        [
            {
                "filename": "site.yml",
                "content": "---\\n# Main playbook\\n- name: Example playbook\\n  hosts: all\\n  roles:\\n    - example_role",
                "path": "."
            },
            {
                "filename": "tasks.yml",
                "content": "---\\n- name: Install package\\n  apt:\\n    name: nginx\\n    state: present",
                "path": "roles/example_role/tasks"
            }
        ]
        """
    
    def _construct_prompt(self, description: str, additional_context: Optional[str] = None) -> str:
        """
        Construct the prompt for the Ollama API.
        
        Args:
            description: Natural language description of the Ansible task
            additional_context: Additional context or requirements for the playbook
            
        Returns:
            Formatted prompt string
        """
        prompt = f"Generate a complete Ansible playbook for the following task:\n\n{description}\n\n"
        
        if additional_context:
            prompt += f"Additional context:\n{additional_context}\n\n"
        
        prompt += """
        Please provide all necessary files for a complete Ansible playbook, including:
        1. Main playbook YAML file
        2. Any roles, tasks, handlers, templates, variables, etc.
        3. README.md with usage instructions
        
        Ensure the playbook follows Ansible best practices and is properly structured.
        
        Your response must be a valid JSON array where each object has the following properties:
        - filename: The name of the file
        - content: The complete content of the file
        - path: The relative path within the playbook structure
        """
        
        return prompt
    
    def _parse_response(self, content: str) -> List[PlaybookFile]:
        """
        Parse the Ollama API response into PlaybookFile objects.
        
        Args:
            content: Response content from the Ollama API
            
        Returns:
            List of PlaybookFile objects
        """
        try:
            # Extract JSON from the response
            # Sometimes the API might return markdown-formatted JSON
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].strip()
            else:
                json_str = content.strip()
            
            # Parse the JSON
            files_data = json.loads(json_str)
            
            # Convert to PlaybookFile objects
            playbook_files = []
            for file_data in files_data:
                playbook_file = PlaybookFile(
                    filename=file_data["filename"],
                    content=file_data["content"],
                    path=file_data["path"]
                )
                playbook_files.append(playbook_file)
            
            return playbook_files
            
        except (json.JSONDecodeError, ValidationError, KeyError) as e:
            logger.error(f"Error parsing Ollama response: {str(e)}")
            logger.debug(f"Raw response content: {content}")
            raise ValueError(f"Failed to parse Ollama response: {str(e)}")
