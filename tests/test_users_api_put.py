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

    def test_update_user_partial_fields_only_name(self, random_user_payload):
        """Update only the name field of existing user."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        update_payload = create_user_payload(email, name="New Name", age=random_user_payload["age"])
        resp = self.api.update_user(email, update_payload)
        assert resp.status == 200
        data = resp.json()
        assert data["name"] == "New Name"
        assert data["age"] == random_user_payload["age"]

    def test_update_user_partial_fields_only_age(self, random_user_payload):
        """Update only the age field of existing user."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        update_payload = create_user_payload(email, name=random_user_payload["name"], age=45)
        resp = self.api.update_user(email, update_payload)
        assert resp.status == 200
        data = resp.json()
        assert data["name"] == random_user_payload["name"]
        assert data["age"] == 45

    def test_update_user_missing_name_returns_400(self, random_user_payload):
        """Update without name field should return 400."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        update_payload = {"email": email, "age": 40}
        resp = self.api.update_user(email, update_payload)
        assert resp.status == 400
        assert_error_response(resp.json())

    def test_update_user_missing_age_returns_400(self, random_user_payload):
        """Update without age field should return 400."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        update_payload = {"email": email, "name": "Updated"}
        resp = self.api.update_user(email, update_payload)
        assert resp.status == 400
        assert_error_response(resp.json())

    def test_update_user_invalid_age_negative_returns_400(self, random_user_payload):
        """Update with negative age should return 400."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        update_payload = create_user_payload(email, name="Updated", age=-10)
        resp = self.api.update_user(email, update_payload)
        assert resp.status == 400
        assert_error_response(resp.json())

    def test_update_user_invalid_age_too_high_returns_400(self, random_user_payload):
        """Update with unrealistic age should return 400."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        update_payload = create_user_payload(email, name="Updated", age=200)
        resp = self.api.update_user(email, update_payload)
        assert resp.status == 400
        assert_error_response(resp.json())

    def test_update_user_empty_name_returns_400(self, random_user_payload):
        """Update with empty name should return 400."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        update_payload = create_user_payload(email, name="", age=30)
        resp = self.api.update_user(email, update_payload)
        assert resp.status == 400
        assert_error_response(resp.json())

    # ---- Age Validation (1-150 range) ----
    def test_update_user_age_minimum_valid_returns_200(self, random_user_payload):
        """UPDATE with age=1 (minimum valid) should succeed."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        update_payload = create_user_payload(email, name="Updated", age=1)
        resp = self.api.update_user(email, update_payload)
        assert resp.status == 200
        assert resp.json()["age"] == 1

    def test_update_user_age_maximum_valid_returns_200(self, random_user_payload):
        """UPDATE with age=150 (maximum valid) should succeed."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        update_payload = create_user_payload(email, name="Updated", age=150)
        resp = self.api.update_user(email, update_payload)
        assert resp.status == 200
        assert resp.json()["age"] == 150

    def test_update_user_age_zero_returns_400(self, random_user_payload):
        """UPDATE with age=0 should return 400."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        update_payload = create_user_payload(email, name="Updated", age=0)
        resp = self.api.update_user(email, update_payload)
        assert resp.status == 400
        assert_error_response(resp.json())

    def test_update_user_age_151_returns_400(self, random_user_payload):
        """UPDATE with age=151 should return 400."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        update_payload = create_user_payload(email, name="Updated", age=151)
        resp = self.api.update_user(email, update_payload)
        assert resp.status == 400
        assert_error_response(resp.json())

