from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class PlaybookRequest(BaseModel):
    """Request model for generating an Ansible playbook."""
    
    description: str = Field(
        ...,
        description="Natural language description of the Ansible task to perform",
        min_length=10
    )
    
    additional_context: Optional[str] = Field(
        None,
        description="Additional context or requirements for the playbook"
    )


class ValidationResult(BaseModel):
    """Model for ansible-lint validation results."""
    
    is_valid: bool = Field(
        ...,
        description="Whether the playbook is valid according to ansible-lint"
    )
    
    messages: List[str] = Field(
        default_factory=list,
        description="Validation messages, including errors and warnings"
    )


class PlaybookFile(BaseModel):
    """Model representing an Ansible playbook file."""
    
    filename: str = Field(
        ...,
        description="Name of the file"
    )
    
    content: str = Field(
        ...,
        description="Content of the file"
    )
    
    path: str = Field(
        ...,
        description="Relative path within the playbook structure"
    )


class PlaybookResponse(BaseModel):
    """Response model for a generated Ansible playbook."""
    
    playbook_id: str = Field(
        ...,
        description="Unique identifier for the generated playbook"
    )
    
    files: List[PlaybookFile] = Field(
        ...,
        description="List of files in the playbook"
    )
    
    validation: ValidationResult = Field(
        ...,
        description="Validation results for the playbook"
    )
    
    download_url: Optional[str] = Field(
        None,
        description="URL to download the playbook"
    )


class ErrorResponse(BaseModel):
    """Model for error responses."""
    
    detail: str = Field(
        ...,
        description="Error message"
    )
    
    code: str = Field(
        ...,
        description="Error code"
    )
