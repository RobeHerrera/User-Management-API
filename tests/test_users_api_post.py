"""Tests for POST endpoints of the User Management API."""

import pytest

from src.helpers.assertions import assert_error_response, assert_user_shape
from src.models.user import create_user_payload
from tests.base_test import AuthenticatedUserApiTest


@pytest.mark.parametrize("env_prefix", ["dev", "prod"])
class TestPostUserAPI(AuthenticatedUserApiTest):

    def test_create_user_returns_201_and_valid_shape(self, unique_email, random_user_payload):
        resp = self.api.create_user(random_user_payload)
        assert resp.status == 201
        data = resp.json()
        assert_user_shape(data)
        assert data["email"] == unique_email
        assert data["name"] == random_user_payload["name"]
        assert data["age"] == random_user_payload["age"]

    def test_create_duplicate_email_returns_409(self, unique_email, random_user_payload):
        email = unique_email

        first = self.api.create_user(random_user_payload)
        assert first.status == 201

        second = self.api.create_user(
            create_user_payload(email, name="Other Name", age=40)
        )
        assert second.status == 409
        assert_error_response(second.json())

    def test_create_validation_missing_required_fields_returns_400(self, unique_email):
        resp = self.api.create_user({"email": unique_email, "age": 30})
        assert resp.status == 400
        assert_error_response(resp.json())

