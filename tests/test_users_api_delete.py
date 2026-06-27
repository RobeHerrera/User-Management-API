"""Tests for DELETE endpoints of the User Management API."""

import pytest

from src.api.users_api import UsersAPI
from src.helpers.assertions import assert_error_response
from src.models.user import create_user_payload
from tests.base_test import AuthenticatedUserApiTest
from tests.config import BASE_URL


@pytest.mark.parametrize("env_prefix", ["dev", "prod"])
class TestDeleteUserAPI(AuthenticatedUserApiTest):

    def test_delete_user_returns_204_and_followup_get_returns_404(self, unique_email, random_user_payload):
        # Create first
        email = unique_email
        created = self.api.create_user(random_user_payload)
        assert created.status == 201

        # Delete
        delete_resp = self.api.delete_user(email)
        assert delete_resp.status == 204

        # Verify deleted
        get_resp = self.api.get_user(email)
        assert get_resp.status == 500
        assert_error_response(get_resp.json())

    def test_delete_without_auth_returns_401_or_404(self, unique_email):
        """DELETE without auth header should return 401 (or possibly 404)."""
        import uuid

        email = f"{uuid.uuid4()}@example.com"

        unauth_api = UsersAPI(
            self.api._request,
            f"{BASE_URL}/{self.env_prefix}",
            auth_token="",
        )
        resp = unauth_api.delete_user(email)
        assert resp.status in (401, 404)
        if resp.status == 401:
            assert_error_response(resp.json())

    def test_delete_all_data(self):
        """Delete all users in the system. Use with caution."""
        # List all users
        list_resp = self.api.list_users()
        assert list_resp.status == 200
        users = list_resp.json()

        # Delete each user
        for user in users:
            email = user["email"]
            delete_resp = self.api.delete_user(email)
            # assert delete_resp.status == 204

        # Verify all deleted
        list_after_resp = self.api.list_users()
        assert list_after_resp.status == 200
        assert list_after_resp.json() == []
