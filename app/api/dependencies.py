from typing import Generator

from app.services.ansible_service import AnsibleService
from app.services.openai_service import OpenAIService


def get_openai_service() -> Generator[OpenAIService, None, None]:
    """
    Dependency for getting an OpenAI service instance.
    """
    service = OpenAIService()
    try:
        yield service
    finally:
        # Clean up any resources if needed
        pass


def get_ansible_service() -> Generator[AnsibleService, None, None]:
    """
    Dependency for getting an Ansible service instance.
    """
    service = AnsibleService()
    try:
        yield service
    finally:
        # Clean up any resources if needed
        pass
