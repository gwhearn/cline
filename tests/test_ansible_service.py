import os
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from app.services.ansible_service import AnsibleService
from app.models.schemas import PlaybookFile, ValidationResult


@pytest.fixture
def ansible_service():
    """Create an AnsibleService instance for testing."""
    service = AnsibleService()
    # Override the output directory to use a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        service.output_dir = Path(temp_dir)
        yield service


def test_generate_playbook_id(ansible_service):
    """Test generating a unique playbook ID."""
    playbook_id = ansible_service.generate_playbook_id()
    assert isinstance(playbook_id, str)
    assert len(playbook_id) > 0


def test_save_playbook(ansible_service):
    """Test saving a playbook to the output directory."""
    # Create test playbook files
    playbook_files = [
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
    
    # Save the playbook
    playbook_id = "test-playbook-id"
    playbook_dir = ansible_service.save_playbook(playbook_id, playbook_files)
    
    # Check that the playbook directory was created
    assert playbook_dir.exists()
    assert playbook_dir.is_dir()
    
    # Check that the playbook files were created
    site_yml_path = playbook_dir / "site.yml"
    assert site_yml_path.exists()
    assert site_yml_path.is_file()
    assert site_yml_path.read_text() == playbook_files[0].content
    
    tasks_dir = playbook_dir / "roles/example_role/tasks"
    assert tasks_dir.exists()
    assert tasks_dir.is_dir()
    
    tasks_yml_path = tasks_dir / "tasks.yml"
    assert tasks_yml_path.exists()
    assert tasks_yml_path.is_file()
    assert tasks_yml_path.read_text() == playbook_files[1].content


@patch("subprocess.run")
def test_validate_playbook_success(mock_run, ansible_service):
    """Test validating a playbook with successful validation."""
    # Mock the subprocess.run function
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = "Playbook validation successful."
    mock_process.stderr = ""
    mock_run.return_value = mock_process
    
    # Create test playbook files
    playbook_files = [
        PlaybookFile(
            filename="site.yml",
            content="---\n# Main playbook\n- name: Example playbook\n  hosts: all\n  roles:\n    - example_role",
            path="."
        )
    ]
    
    # Validate the playbook
    validation_result = ansible_service.validate_playbook(playbook_files)
    
    # Check the validation result
    assert validation_result.is_valid is True
    assert len(validation_result.messages) == 1
    assert validation_result.messages[0] == "Playbook validation successful."
    
    # Verify the mock was called correctly
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0][0] == "ansible-lint"
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True
    assert kwargs["check"] is False


@patch("subprocess.run")
def test_validate_playbook_failure(mock_run, ansible_service):
    """Test validating a playbook with validation errors."""
    # Mock the subprocess.run function
    mock_process = MagicMock()
    mock_process.returncode = 1
    mock_process.stdout = "Error: Syntax error in playbook"
    mock_process.stderr = ""
    mock_run.return_value = mock_process
    
    # Create test playbook files
    playbook_files = [
        PlaybookFile(
            filename="site.yml",
            content="---\n# Invalid playbook\n- name: Example playbook\n  hosts: all\n  invalid_key: value",
            path="."
        )
    ]
    
    # Validate the playbook
    validation_result = ansible_service.validate_playbook(playbook_files)
    
    # Check the validation result
    assert validation_result.is_valid is False
    assert len(validation_result.messages) == 1
    assert validation_result.messages[0] == "Error: Syntax error in playbook"


def test_create_playbook_archive(ansible_service):
    """Test creating a ZIP archive of a playbook."""
    # Create a test playbook directory
    playbook_id = "test-archive-id"
    playbook_dir = ansible_service.output_dir / playbook_id
    playbook_dir.mkdir(parents=True)
    
    # Create a test file in the playbook directory
    test_file = playbook_dir / "test.yml"
    test_file.write_text("Test content")
    
    # Create the archive
    archive_path = ansible_service.create_playbook_archive(playbook_id)
    
    # Check that the archive was created
    assert archive_path.exists()
    assert archive_path.is_file()
    assert archive_path.suffix == ".zip"


def test_get_playbook_path_exists(ansible_service):
    """Test getting the path to an existing playbook."""
    # Create a test playbook directory
    playbook_id = "test-path-id"
    playbook_dir = ansible_service.output_dir / playbook_id
    playbook_dir.mkdir(parents=True)
    
    # Get the playbook path
    path = ansible_service.get_playbook_path(playbook_id)
    
    # Check that the path is correct
    assert path == playbook_dir


def test_get_playbook_path_not_exists(ansible_service):
    """Test getting the path to a non-existent playbook."""
    # Get the playbook path for a non-existent playbook
    path = ansible_service.get_playbook_path("nonexistent-id")
    
    # Check that the path is None
    assert path is None
