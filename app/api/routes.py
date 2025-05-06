import logging
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import ValidationError

from app.models.schemas import (
    ErrorResponse,
    PlaybookFile,
    PlaybookRequest,
    PlaybookResponse,
    ValidationResult,
)
from app.services.ansible_service import AnsibleService
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=PlaybookResponse)
async def generate_playbook(request: PlaybookRequest):
    """
    Generate an Ansible playbook from a natural language description.
    """
    try:
        # Initialize services
        openai_service = OpenAIService()
        ansible_service = AnsibleService()
        
        # Generate a unique ID for the playbook
        playbook_id = ansible_service.generate_playbook_id()
        
        # Generate the playbook files
        playbook_files = openai_service.generate_ansible_playbook(
            request.description,
            request.additional_context
        )
        
        # Validate the playbook
        validation_result = ansible_service.validate_playbook(playbook_files)
        
        # Save the playbook files
        ansible_service.save_playbook(playbook_id, playbook_files)
        
        # Create the download URL
        download_url = f"/api/download/{playbook_id}"
        
        # Return the response
        return PlaybookResponse(
            playbook_id=playbook_id,
            files=playbook_files,
            validation=validation_result,
            download_url=download_url
        )
        
    except Exception as e:
        logger.error(f"Error generating playbook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                detail=f"Failed to generate playbook: {str(e)}",
                code="GENERATION_ERROR"
            ).dict()
        )


@router.get("/download/{playbook_id}")
async def download_playbook(playbook_id: str):
    """
    Download a generated Ansible playbook as a ZIP archive.
    """
    try:
        # Initialize the Ansible service
        ansible_service = AnsibleService()
        
        # Check if the playbook exists
        playbook_path = ansible_service.get_playbook_path(playbook_id)
        if not playbook_path:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    detail=f"Playbook with ID {playbook_id} not found",
                    code="PLAYBOOK_NOT_FOUND"
                ).dict()
            )
        
        # Create a ZIP archive of the playbook
        archive_path = ansible_service.create_playbook_archive(playbook_id)
        if not archive_path:
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    detail=f"Failed to create archive for playbook {playbook_id}",
                    code="ARCHIVE_CREATION_ERROR"
                ).dict()
            )
        
        # Return the ZIP file
        return FileResponse(
            path=archive_path,
            filename=f"ansible-playbook-{playbook_id}.zip",
            media_type="application/zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading playbook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                detail=f"Failed to download playbook: {str(e)}",
                code="DOWNLOAD_ERROR"
            ).dict()
        )


@router.post("/validate", response_model=ValidationResult)
async def validate_playbook(files: List[UploadFile] = File(...)):
    """
    Validate an uploaded Ansible playbook.
    """
    try:
        # Initialize the Ansible service
        ansible_service = AnsibleService()
        
        # Convert uploaded files to PlaybookFile objects
        playbook_files = []
        for file in files:
            content = await file.read()
            file_content = content.decode("utf-8")
            
            # Extract path from filename (e.g., "roles/example/tasks/main.yml")
            filename = file.filename
            if "/" in filename:
                path = str(Path(filename).parent)
                filename = Path(filename).name
            else:
                path = "."
            
            playbook_file = PlaybookFile(
                filename=filename,
                content=file_content,
                path=path
            )
            playbook_files.append(playbook_file)
        
        # Validate the playbook
        validation_result = ansible_service.validate_playbook(playbook_files)
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Error validating playbook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                detail=f"Failed to validate playbook: {str(e)}",
                code="VALIDATION_ERROR"
            ).dict()
        )
