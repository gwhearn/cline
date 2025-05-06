import json
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.models.schemas import PlaybookFile, ValidationResult


# Create a test client
client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_page():
    """Test the index page loads correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Generate Ansible Playbooks from Natural Language" in response.text


@patch("app.services.openai_service.OpenAIService")
@patch("app.services.ansible_service.AnsibleService")
def test_generate_playbook_api(mock_ansible_service, mock_openai_service):
    """Test the generate playbook API endpoint."""
    # Mock the OpenAI service
    mock_openai_instance = mock_openai_service.return_value
    mock_openai_instance.generate_ansible_playbook.return_value = [
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
    
    # Mock the Ansible service
    mock_ansible_instance = mock_ansible_service.return_value
    mock_ansible_instance.generate_playbook_id.return_value = "test-id-123"
    mock_ansible_instance.validate_playbook.return_value = ValidationResult(
        is_valid=True,
        messages=["Playbook validation successful."]
    )
    mock_ansible_instance.save_playbook.return_value = None
    
    # Make the request
    response = client.post(
        "/api/generate",
        json={
            "description": "Install Nginx on Ubuntu servers",
            "additional_context": "Target systems are Ubuntu 22.04"
        }
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["playbook_id"] == "test-id-123"
    assert len(data["files"]) == 2
    assert data["validation"]["is_valid"] is True
    assert data["download_url"] == "/api/download/test-id-123"
    
    # Verify the mocks were called correctly
    mock_openai_instance.generate_ansible_playbook.assert_called_once_with(
        "Install Nginx on Ubuntu servers",
        "Target systems are Ubuntu 22.04"
    )
    mock_ansible_instance.validate_playbook.assert_called_once()
    mock_ansible_instance.save_playbook.assert_called_once_with("test-id-123", mock_openai_instance.generate_ansible_playbook.return_value)


@patch("app.services.ansible_service.AnsibleService")
def test_download_playbook_api(mock_ansible_service):
    """Test the download playbook API endpoint."""
    # Mock the Ansible service
    mock_ansible_instance = mock_ansible_service.return_value
    mock_ansible_instance.get_playbook_path.return_value = True
    
    # Create a temporary file for the test
    test_file_path = os.path.join(os.path.dirname(__file__), "test_archive.zip")
    with open(test_file_path, "wb") as f:
        f.write(b"test content")
    
    # Mock the create_playbook_archive method
    mock_ansible_instance.create_playbook_archive.return_value = test_file_path
    
    try:
        # Make the request
        response = client.get("/api/download/test-id-123")
        
        # Check the response
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert response.headers["content-disposition"] == 'attachment; filename="ansible-playbook-test-id-123.zip"'
        
        # Verify the mocks were called correctly
        mock_ansible_instance.get_playbook_path.assert_called_once_with("test-id-123")
        mock_ansible_instance.create_playbook_archive.assert_called_once_with("test-id-123")
    
    finally:
        # Clean up the test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)


@patch("app.services.ansible_service.AnsibleService")
def test_download_playbook_not_found(mock_ansible_service):
    """Test the download playbook API endpoint when the playbook is not found."""
    # Mock the Ansible service
    mock_ansible_instance = mock_ansible_service.return_value
    mock_ansible_instance.get_playbook_path.return_value = None
    
    # Make the request
    response = client.get("/api/download/nonexistent-id")
    
    # Check the response
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]["detail"]
    
    # Verify the mocks were called correctly
    mock_ansible_instance.get_playbook_path.assert_called_once_with("nonexistent-id")
    mock_ansible_instance.create_playbook_archive.assert_not_called()
