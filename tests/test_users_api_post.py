"""Tests for POST endpoints of the User Management API."""

import pytest

from src.helpers.assertions import assert_error_response, assert_user_shape
from src.models.user import create_user_payload
from tests.base_test import AuthenticatedUserApiTest


@pytest.mark.parametrize("env_prefix", ["dev", "prod"])
class TestPostUserAPI(AuthenticatedUserApiTest):
    
    def test_create_user_invalid_email_format_returns_400(self):
        """POST with invalid email format should return 400."""
        payload = create_user_payload("invalid-email-no-at", name="John", age=30)
        resp = self.api.create_user(payload)
        assert resp.status == 400
        assert_error_response(resp.json())

    def test_create_duplicate_email_returns_409(self, unique_email, random_user_payload):
        email = unique_email

        first = self.api.create_user(random_user_payload)
        assert first.status == 201

        second = self.api.create_user(
            create_user_payload(email, name="Other Name", age=40)
        )
        assert second.status == 409
        assert_error_response(second.json())

    def test_create_user_returns_201_and_valid_shape(self, unique_email, random_user_payload):
        resp = self.api.create_user(random_user_payload)
        assert resp.status == 201
        data = resp.json()
        assert_user_shape(data)
        assert data["email"] == unique_email
        assert data["name"] == random_user_payload["name"]
        assert data["age"] == random_user_payload["age"]

    def test_create_validation_missing_required_fields_returns_400(self, unique_email):
        resp = self.api.create_user({"email": unique_email, "age": 30})
        assert resp.status == 400
        assert_error_response(resp.json())

    def test_create_user_with_all_valid_fields(self, unique_email):
        """Create user with all required fields populated."""
        payload = create_user_payload(unique_email, name="John Smith", age=35)
        resp = self.api.create_user(payload)
        assert resp.status == 201
        data = resp.json()
        assert data["email"] == unique_email
        assert data["name"] == "John Smith"
        assert data["age"] == 35

    def test_create_user_missing_name_returns_400(self, unique_email):
        """POST without name field should return 400."""
        payload = {"email": unique_email, "age": 30}
        resp = self.api.create_user(payload)
        assert resp.status == 400
        assert_error_response(resp.json())

    def test_create_user_missing_age_returns_400(self, unique_email):
        """POST without age field should return 400."""
        payload = {"email": unique_email, "name": "John Doe"}
        resp = self.api.create_user(payload)
        assert resp.status == 400
        assert_error_response(resp.json())

    def test_create_user_invalid_age_negative_returns_400(self, unique_email):
        """POST with negative age should return 400."""
        payload = create_user_payload(unique_email, name="John", age=-5)
        resp = self.api.create_user(payload)
        assert resp.status == 400
        assert_error_response(resp.json())

    def test_create_user_invalid_age_too_high_returns_400(self, unique_email):
        """POST with unrealistic age (>150) should return 400."""
        payload = create_user_payload(unique_email, name="John", age=200)
        resp = self.api.create_user(payload)
        assert resp.status == 400
        assert_error_response(resp.json())

    def test_create_user_empty_name_returns_400(self, unique_email):
        """POST with empty name should return 400."""
        payload = create_user_payload(unique_email, name="", age=30)
        resp = self.api.create_user(payload)
        assert resp.status == 400
        assert_error_response(resp.json())

    # ---- Age Validation (1-150 range) ----
    def test_create_user_age_minimum_valid_returns_201(self, unique_email):
        """POST with age=1 (minimum valid) should succeed."""
        payload = create_user_payload(unique_email, name="Newborn", age=1)
        resp = self.api.create_user(payload)
        assert resp.status == 201
        assert resp.json()["age"] == 1

    def test_create_user_age_maximum_valid_returns_201(self, unique_email):
        """POST with age=150 (maximum valid) should succeed."""
        payload = create_user_payload(unique_email, name="Elderly", age=150)
        resp = self.api.create_user(payload)
        assert resp.status == 201
        assert resp.json()["age"] == 150

    def test_create_user_age_zero_returns_400(self, unique_email):
        """POST with age=0 should return 400."""
        payload = create_user_payload(unique_email, name="Invalid", age=0)
        resp = self.api.create_user(payload)
        assert resp.status == 400
        assert_error_response(resp.json())

    def test_create_user_age_151_returns_400(self, unique_email):
        """POST with age=151 should return 400."""
        payload = create_user_payload(unique_email, name="Invalid", age=151)
        resp = self.api.create_user(payload)
        assert resp.status == 400
        assert_error_response(resp.json())

