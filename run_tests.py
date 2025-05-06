#!/usr/bin/env python3
"""
Run tests for the Ansible Playbook Generator application.
"""

import os
import sys
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Set test environment variables
    os.environ["APP_ENV"] = "test"
    
    # Get command line arguments
    args = sys.argv[1:] or ["tests/"]
    
    # Run the tests
    sys.exit(pytest.main(args))
