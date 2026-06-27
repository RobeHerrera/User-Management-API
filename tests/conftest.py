"""Shared fixtures for the User Management API test suite."""

import random
import uuid

import pytest
from playwright.sync_api import APIRequestContext

from src.models.user import create_user_payload
from tests.config import BASE_URL


@pytest.fixture(scope="session")
def request_context(playwright) -> APIRequestContext:
    """Playwright API request context (no browser needed)."""
    return playwright.request.new_context()


@pytest.fixture
def unique_email() -> str:
    """Generate a unique email for each test."""
    return f"{uuid.uuid4()}@example.com"


@pytest.fixture
def random_user_payload(unique_email: str) -> dict:
    """Generate a realistic random user payload for each test."""
    first_names = ["Alice", "Bob", "Catherine", "Daniel", "Emma", "Frank"]
    last_names = ["Johnson", "Smith", "Brown", "Davis", "Wilson", "Taylor"]
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    age = random.randint(0, 100)
    return create_user_payload(unique_email, name=name, age=age)