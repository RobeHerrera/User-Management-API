"""Tests for PUT endpoints of the User Management API."""

import pytest

from src.helpers.assertions import assert_error_response, assert_user_shape
from src.models.user import create_user_payload
from tests.base_test import BaseUserApiTest


@pytest.mark.parametrize("env_prefix", ["dev", "prod"])
class TestPutUserAPI(BaseUserApiTest):

    def test_update_user_returns_200_and_updates_fields(self, unique_email, random_user_payload):
        email = unique_email

        created = self.api.create_user(random_user_payload)
        assert created.status == 201

        update_payload = create_user_payload(email, name="Jane Updated", age=31)
        resp = self.api.update_user(email, update_payload)
        assert resp.status == 200

        data = resp.json()
        assert_user_shape(data)
        assert data["email"] == email
        assert data["name"] == "Jane Updated"
        assert data["age"] == 31

    def test_update_nonexistent_user_returns_404(self, unique_email):
        resp = self.api.update_user(
            unique_email,
            create_user_payload(unique_email, name="Does Not Exist", age=30),
        )
        assert resp.status == 404
        assert_error_response(resp.json())

