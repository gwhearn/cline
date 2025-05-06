#!/usr/bin/env python3
"""
Run script for the Ansible Playbook Generator application.
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="debug" if reload else "info",
    )
    
    print(f"Ansible Playbook Generator running at http://{host}:{port}")
