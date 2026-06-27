"""Shared base classes for API test suites."""

import pytest

from src.api.users_api import UsersAPI
from tests.config import AUTH_TOKEN, BASE_URL


class BaseUserApiTest:
    """Provide a reusable API client setup for environment-parametrized tests."""

    @pytest.fixture(autouse=True)
    def _setup_api(self, request_context, env_prefix):
        self.env_prefix = env_prefix
        self.api = UsersAPI(request_context, f"{BASE_URL}/{env_prefix}")


class AuthenticatedUserApiTest(BaseUserApiTest):
    """Same setup as BaseUserApiTest, but with authentication enabled."""

    @pytest.fixture(autouse=True)
    def _setup_api(self, request_context, env_prefix):
        self.env_prefix = env_prefix
        self.api = UsersAPI(
            request_context,
            f"{BASE_URL}/{env_prefix}",
            auth_token=AUTH_TOKEN,
        )
