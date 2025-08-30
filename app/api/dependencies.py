from typing import Generator

from app.services.ansible_service import AnsibleService
from app.services.llm.factory import LLMProviderFactory


def get_llm_factory() -> Generator[LLMProviderFactory, None, None]:
    """
    Dependency for getting an LLM provider factory instance.
    """
    factory = LLMProviderFactory()
    try:
        yield factory
    finally:
        # Clean up any resources if needed
        factory.reset_provider()


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
