import json
import logging
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.config import settings
from app.models.schemas import PlaybookFile, ValidationResult

logger = logging.getLogger(__name__)


class AnsibleService:
    """Service for Ansible operations and validation."""
    
    def __init__(self):
        """Initialize the Ansible service."""
        self.output_dir = settings.get_ansible_output_path()
    
    def validate_playbook(self, playbook_files: List[PlaybookFile]) -> ValidationResult:
        """
        Validate an Ansible playbook using ansible-lint.
        
        Args:
            playbook_files: List of PlaybookFile objects representing the playbook
            
        Returns:
            ValidationResult object with validation status and messages
        """
        # Create a temporary directory to store the playbook files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write the playbook files to the temporary directory
            main_playbook_path = None
            for playbook_file in playbook_files:
                file_path = temp_path / playbook_file.path / playbook_file.filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(playbook_file.content)
                
                # Identify the main playbook file (usually site.yml or playbook.yml)
                if playbook_file.filename in ["site.yml", "playbook.yml", "main.yml"] and playbook_file.path == ".":
                    main_playbook_path = file_path
            
            # If no main playbook file was found, use the first YAML file
            if not main_playbook_path:
                for playbook_file in playbook_files:
                    if playbook_file.filename.endswith((".yml", ".yaml")):
                        main_playbook_path = temp_path / playbook_file.path / playbook_file.filename
                        break
            
            if not main_playbook_path:
                return ValidationResult(
                    is_valid=False,
                    messages=["No playbook YAML file found in the generated files."]
                )
            
            # Run ansible-lint
            try:
                result = subprocess.run(
                    ["ansible-lint", str(main_playbook_path), "-p"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                # Parse the output
                if result.returncode == 0:
                    return ValidationResult(
                        is_valid=True,
                        messages=["Playbook validation successful."]
                    )
                else:
                    # Extract error messages
                    error_lines = result.stdout.splitlines() + result.stderr.splitlines()
                    filtered_errors = [line for line in error_lines if line.strip()]
                    
                    return ValidationResult(
                        is_valid=False,
                        messages=filtered_errors
                    )
                    
            except subprocess.SubprocessError as e:
                logger.error(f"Error running ansible-lint: {str(e)}")
                return ValidationResult(
                    is_valid=False,
                    messages=[f"Error running ansible-lint: {str(e)}"]
                )
            except Exception as e:
                logger.error(f"Unexpected error during playbook validation: {str(e)}")
                return ValidationResult(
                    is_valid=False,
                    messages=[f"Unexpected error during validation: {str(e)}"]
                )
    
    def save_playbook(self, playbook_id: str, playbook_files: List[PlaybookFile]) -> Path:
        """
        Save the playbook files to the output directory.
        
        Args:
            playbook_id: Unique identifier for the playbook
            playbook_files: List of PlaybookFile objects representing the playbook
            
        Returns:
            Path to the saved playbook directory
        """
        # Create a directory for the playbook
        playbook_dir = self.output_dir / playbook_id
        playbook_dir.mkdir(parents=True, exist_ok=True)
        
        # Write the playbook files
        for playbook_file in playbook_files:
            file_path = playbook_dir / playbook_file.path / playbook_file.filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(playbook_file.content)
        
        return playbook_dir
    
    def create_playbook_archive(self, playbook_id: str) -> Optional[Path]:
        """
        Create a ZIP archive of the playbook files.
        
        Args:
            playbook_id: Unique identifier for the playbook
            
        Returns:
            Path to the created archive, or None if the playbook doesn't exist
        """
        playbook_dir = self.output_dir / playbook_id
        if not playbook_dir.exists():
            return None
        
        # Create a ZIP archive
        archive_path = self.output_dir / f"{playbook_id}.zip"
        shutil.make_archive(
            str(archive_path.with_suffix("")),  # Remove .zip extension for make_archive
            "zip",
            root_dir=str(playbook_dir),
            base_dir="."
        )
        
        return archive_path
    
    def get_playbook_path(self, playbook_id: str) -> Optional[Path]:
        """
        Get the path to a saved playbook.
        
        Args:
            playbook_id: Unique identifier for the playbook
            
        Returns:
            Path to the playbook directory, or None if it doesn't exist
        """
        playbook_dir = self.output_dir / playbook_id
        return playbook_dir if playbook_dir.exists() else None
    
    def generate_playbook_id(self) -> str:
        """
        Generate a unique identifier for a playbook.
        
        Returns:
            Unique playbook ID
        """
        return str(uuid.uuid4())
