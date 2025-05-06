import logging
from pathlib import Path

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.config import settings
from app.models.schemas import PlaybookRequest
from app.services.ansible_service import AnsibleService
from app.services.openai_service import OpenAIService

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create the FastAPI app
app = FastAPI(
    title="Ansible Playbook Generator",
    description="Generate Ansible playbooks from natural language descriptions",
    version="0.1.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent / "static"),
    name="static",
)

# Set up Jinja2 templates
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Render the main page.
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    description: str = Form(...),
    additional_context: str = Form(None),
):
    """
    Generate an Ansible playbook and display the results.
    """
    try:
        # Create the request model
        playbook_request = PlaybookRequest(
            description=description,
            additional_context=additional_context,
        )
        
        # Initialize services
        openai_service = OpenAIService()
        ansible_service = AnsibleService()
        
        # Generate a unique ID for the playbook
        playbook_id = ansible_service.generate_playbook_id()
        
        # Generate the playbook files
        playbook_files = openai_service.generate_ansible_playbook(
            playbook_request.description,
            playbook_request.additional_context
        )
        
        # Validate the playbook
        validation_result = ansible_service.validate_playbook(playbook_files)
        
        # Save the playbook files
        ansible_service.save_playbook(playbook_id, playbook_files)
        
        # Create the download URL
        download_url = f"/api/download/{playbook_id}"
        
        # Render the result page
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "playbook_id": playbook_id,
                "files": playbook_files,
                "validation": validation_result,
                "download_url": download_url,
                "description": description,
            }
        )
        
    except Exception as e:
        logging.error(f"Error generating playbook: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": str(e),
            },
            status_code=500,
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
    )
