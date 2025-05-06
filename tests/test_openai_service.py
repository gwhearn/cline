import json
import pytest
from unittest.mock import patch, MagicMock

from app.services.openai_service import OpenAIService
from app.models.schemas import PlaybookFile


@pytest.fixture
def openai_service():
    """Create an OpenAIService instance for testing."""
    with patch("app.services.openai_service.OpenAI") as mock_openai:
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Create the service
        service = OpenAIService()
        
        # Set the mocked client
        service.client = mock_client
        
        yield service


def test_get_system_prompt(openai_service):
    """Test getting the system prompt."""
    prompt = openai_service._get_system_prompt()
    assert isinstance(prompt, str)
    assert "expert Ansible playbook generator" in prompt
    assert "valid JSON array" in prompt


def test_construct_prompt(openai_service):
    """Test constructing the prompt for the OpenAI API."""
    # Test with description only
    description = "Install Nginx on Ubuntu servers"
    prompt = openai_service._construct_prompt(description)
    
    assert isinstance(prompt, str)
    assert description in prompt
    assert "Generate a complete Ansible playbook" in prompt
    
    # Test with description and additional context
    additional_context = "Target systems are Ubuntu 22.04"
    prompt = openai_service._construct_prompt(description, additional_context)
    
    assert isinstance(prompt, str)
    assert description in prompt
    assert additional_context in prompt
    assert "Additional context" in prompt


@patch("app.services.openai_service.OpenAIService._parse_response")
def test_generate_ansible_playbook(mock_parse_response, openai_service):
    """Test generating an Ansible playbook."""
    # Mock the OpenAI API response
    mock_message = MagicMock()
    mock_message.content = "Mock response content"
    
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    openai_service.client.chat.completions.create.return_value = mock_response
    
    # Mock the parse_response method
    expected_files = [
        PlaybookFile(
            filename="site.yml",
            content="---\n# Main playbook\n- name: Example playbook\n  hosts: all\n  roles:\n    - example_role",
            path="."
        ),
        PlaybookFile(
            filename="tasks.yml",
            content="---\n- name: Install package\n  apt:\n    name: nginx\n    state: present",
            path="roles/example_role/tasks"
        )
    ]
    mock_parse_response.return_value = expected_files
    
    # Generate the playbook
    description = "Install Nginx on Ubuntu servers"
    additional_context = "Target systems are Ubuntu 22.04"
    files = openai_service.generate_ansible_playbook(description, additional_context)
    
    # Check the result
    assert files == expected_files
    
    # Verify the mocks were called correctly
    openai_service.client.chat.completions.create.assert_called_once()
    args, kwargs = openai_service.client.chat.completions.create.call_args
    
    assert kwargs["model"] == openai_service.model
    assert len(kwargs["messages"]) == 2
    assert kwargs["messages"][0]["role"] == "system"
    assert kwargs["messages"][1]["role"] == "user"
    
    mock_parse_response.assert_called_once_with("Mock response content")


def test_parse_response_json(openai_service):
    """Test parsing a JSON response from the OpenAI API."""
    # Create a test response
    response_json = [
        {
            "filename": "site.yml",
            "content": "---\n# Main playbook\n- name: Example playbook\n  hosts: all\n  roles:\n    - example_role",
            "path": "."
        },
        {
            "filename": "tasks.yml",
            "content": "---\n- name: Install package\n  apt:\n    name: nginx\n    state: present",
            "path": "roles/example_role/tasks"
        }
    ]
    response_content = json.dumps(response_json)
    
    # Parse the response
    files = openai_service._parse_response(response_content)
    
    # Check the result
    assert len(files) == 2
    assert files[0].filename == "site.yml"
    assert files[0].content == "---\n# Main playbook\n- name: Example playbook\n  hosts: all\n  roles:\n    - example_role"
    assert files[0].path == "."
    assert files[1].filename == "tasks.yml"
    assert files[1].content == "---\n- name: Install package\n  apt:\n    name: nginx\n    state: present"
    assert files[1].path == "roles/example_role/tasks"


def test_parse_response_markdown_json(openai_service):
    """Test parsing a markdown-formatted JSON response from the OpenAI API."""
    # Create a test response with markdown formatting
    response_json = [
        {
            "filename": "site.yml",
            "content": "---\n# Main playbook\n- name: Example playbook\n  hosts: all\n  roles:\n    - example_role",
            "path": "."
        },
        {
            "filename": "tasks.yml",
            "content": "---\n- name: Install package\n  apt:\n    name: nginx\n    state: present",
            "path": "roles/example_role/tasks"
        }
    ]
    response_content = f"```json\n{json.dumps(response_json)}\n```"
    
    # Parse the response
    files = openai_service._parse_response(response_content)
    
    # Check the result
    assert len(files) == 2
    assert files[0].filename == "site.yml"
    assert files[0].path == "."
    assert files[1].filename == "tasks.yml"
    assert files[1].path == "roles/example_role/tasks"


def test_parse_response_error(openai_service):
    """Test parsing an invalid response from the OpenAI API."""
    # Create an invalid response
    response_content = "This is not valid JSON"
    
    # Parse the response (should raise an exception)
    with pytest.raises(ValueError):
        openai_service._parse_response(response_content)
