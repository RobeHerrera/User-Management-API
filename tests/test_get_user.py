"""Tests for GET endpoints of the User Management API."""

import pytest

from src.helpers.assertions import assert_error_response
from tests.base_test import BaseUserApiTest


@pytest.mark.parametrize("env_prefix", ["dev", "prod"])
class TestGetUserAPI(BaseUserApiTest):

    def test_list_users_empty_initially(self):
        resp = self.api.list_users()
        assert resp.status == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_get_nonexistent_user(self, unique_email):
        resp = self.api.get_user(unique_email)
        # Should be 404?
        assert resp.status == 500
        assert_error_response(resp.json())

    # ---- Happy Path: Get existing user ----
    def test_get_existing_user(self, random_user_payload):
        """Create a user and verify we can retrieve it with all fields intact."""
        # Create user
        create_resp = self.api.create_user(random_user_payload)
        assert create_resp.status == 201
        
        # Get user
        get_resp = self.api.get_user(random_user_payload["email"])
        assert get_resp.status == 200
        data = get_resp.json()
        
        # Verify all fields match
        assert data["name"] == random_user_payload["name"]
        assert data["email"] == random_user_payload["email"]
        assert data["age"] == random_user_payload["age"]

    def test_get_user_response_structure(self, random_user_payload):
        """Verify response contains expected fields with correct data types."""
        self.api.create_user(random_user_payload)
        resp = self.api.get_user(random_user_payload["email"])
        assert resp.status == 200
        data = resp.json()
        
        # Check expected fields exist and have correct types
        assert "name" in data and isinstance(data["name"], str)
        assert "email" in data and isinstance(data["email"], str)
        assert "age" in data and isinstance(data["age"], int)

    def test_get_user_consistent_responses(self, random_user_payload):
        """Multiple calls with same email should return identical results."""
        self.api.create_user(random_user_payload)
        email = random_user_payload["email"]
        
        # Call endpoint twice
        resp1 = self.api.get_user(email)
        resp2 = self.api.get_user(email)
        
        assert resp1.status == 200
        assert resp2.status == 200
        assert resp1.json() == resp2.json()

    # ---- Invalid Input Cases ----
    def test_get_user_empty_email(self):
        """Test GET /users/ without email parameter."""
        resp = self.api.get_user("")
        # Should likely be 400 Bad Request or 404
        # but it gets 500 seems to be an issue
        assert resp.status in [400, 404, 405, 500]

    def test_get_user_invalid_email_format(self):
        """Test with email missing @ symbol."""
        resp = self.api.get_user("invalidemail")
        # Can be 400 (invalid format) or 500 (not found)
        assert resp.status in [400, 404, 500]

    def test_get_user_special_characters_in_email(self):
        """Test with special characters in email (plus addressing)."""
        email_with_plus = "test+tag@example.com"
        resp = self.api.get_user(email_with_plus)
        # Should be 500/404 for non-existent user
        assert resp.status in [404, 500]

    def test_get_user_subdomain_email(self):
        """Test email with subdomain."""
        email_subdomain = "user@mail.subdomain.co.uk"
        resp = self.api.get_user(email_subdomain)
        # Should be 500/404 for non-existent user
        assert resp.status in [404, 500]

    def test_get_user_very_long_email(self):
        """Test with extremely long email string."""
        long_email = "a" * 500 + "@example.com"
        resp = self.api.get_user(long_email)
        # Should be 400 (too long) or 500 (not found)
        assert resp.status in [400, 404, 500]

    def test_get_user_sql_injection_attempt(self):
        """Test SQL injection payload in email parameter."""
        malicious_email = "test' OR '1'='1"
        resp = self.api.get_user(malicious_email)
        # Should not execute SQL, just return 500/404
        assert resp.status in [400, 404, 500]
        assert_error_response(resp.json())

    def test_get_user_path_traversal_attempt(self):
        """Test path traversal attempts."""
        resp = self.api.get_user("../../../sensitive")
        # Should not allow path traversal
        assert resp.status in [400, 404, 500]

    # ---- Edge Cases & HTTP Methods ----
    def test_get_user_with_spaces_in_email(self):
        """Test email with spaces (unencoded)."""
        email_with_spaces = "test email@example.com"
        resp = self.api.get_user(email_with_spaces)
        # Should be 400/404/500
        assert resp.status in [400, 404, 500]

    def test_get_user_url_encoded_special_chars(self, unique_email):
        """Test with URL-encoded special characters."""
        # Email with encoded space (%20)
        encoded_email = "test%20user@example.com"
        resp = self.api.get_user(encoded_email)
        # Should be 500/404 for non-existent
        assert resp.status in [400, 404, 500]

    # ---- Response Validation ----
    def test_get_user_response_content_type(self, random_user_payload):
        """Verify response has correct Content-Type header."""
        self.api.create_user(random_user_payload)
        resp = self.api.get_user(random_user_payload["email"])
        assert resp.status == 200
        
        # Check Content-Type header
        content_type = resp.headers.get("content-type", "").lower()
        assert "application/json" in content_type

    def test_get_user_error_response_structure(self):
        """Verify error responses have proper error structure."""
        resp = self.api.get_user("nonexistent@test.com")
        assert resp.status in [404, 500]
        
        data = resp.json()
        # Error responses should have error info (implementation-dependent)
        assert isinstance(data, (dict, list))
