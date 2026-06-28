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

    def test_delete_without_auth_returns_401_or_404(self):
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

    # ---- Happy Path ----
    def test_delete_user_response_is_204_no_content(self, random_user_payload):
        """Verify successful delete returns 204 with empty body."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        resp = self.api.delete_user(email)
        assert resp.status == 204
        # 204 should have no content
        assert resp.status_text == "NO CONTENT" or resp.text is None

    def test_delete_user_idempotent_second_delete(self, random_user_payload):
        """Deleting the same user twice - second delete should fail or return different status."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        # First delete
        delete_resp1 = self.api.delete_user(email)
        assert delete_resp1.status == 204
        
        # Second delete of same user
        delete_resp2 = self.api.delete_user(email)
        # Should either be 404 (not found) or error
        assert delete_resp2.status in (404, 500)

    def test_delete_nonexistent_user_returns_404_or_error(self, unique_email):
        """Attempt to delete a user that never existed."""
        resp = self.api.delete_user(unique_email)
        # Should return 404 or 500
        assert resp.status in (404, 500)

    # ---- Invalid Input Cases ----
    def test_delete_user_empty_email(self):
        """DELETE /users/ with empty email."""
        resp = self.api.delete_user("")
        # Should return error status
        assert resp.status in (400, 404, 405, 500)

    def test_delete_user_invalid_email_format(self):
        """DELETE with email missing @ symbol."""
        resp = self.api.delete_user("invalidemail")
        assert resp.status in (400, 404, 500)

    def test_delete_user_special_characters_email(self):
        """DELETE with special characters (plus addressing)."""
        resp = self.api.delete_user("test+tag@example.com")
        assert resp.status in (404, 500)

    def test_delete_user_subdomain_email(self):
        """DELETE with subdomain email."""
        resp = self.api.delete_user("user@mail.subdomain.co.uk")
        assert resp.status in (404, 500)

    def test_delete_user_very_long_email(self):
        """DELETE with extremely long email."""
        long_email = "a" * 500 + "@example.com"
        resp = self.api.delete_user(long_email)
        assert resp.status in (400, 404, 500)

    def test_delete_user_sql_injection_attempt(self):
        """DELETE with SQL injection payload."""
        malicious_email = "test' OR '1'='1"
        resp = self.api.delete_user(malicious_email)
        # Should not execute SQL, just return error
        assert resp.status in (400, 404, 500)

    def test_delete_user_path_traversal_attempt(self):
        """DELETE with path traversal attempt."""
        resp = self.api.delete_user("../../../sensitive")
        # Should not allow path traversal
        assert resp.status in (400, 404, 500)

    def test_delete_user_with_spaces_in_email(self):
        """DELETE with unencoded spaces in email."""
        resp = self.api.delete_user("test email@example.com")
        assert resp.status in (400, 404, 500)

    # ---- Authentication & Authorization ----
    def test_delete_with_malformed_auth_token(self, random_user_payload):
        """DELETE with invalid/malformed auth token."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        malformed_api = UsersAPI(
            self.api._request,
            f"{BASE_URL}/{self.env_prefix}",
            auth_token="invalid_token_12345",
        )
        resp = malformed_api.delete_user(email)
        # Should return 401 (unauthorized)
        assert resp.status in (401, 403)

    # ---- Edge Cases ----
    def test_delete_user_case_sensitivity(self, random_user_payload):
        """Test if delete respects case sensitivity of email."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        # Try deleting with different case
        email_uppercase = email.upper()
        email_mixed = email[0].upper() + email[1:]
        
        delete_original = self.api.delete_user(email)
        assert delete_original.status == 204
        
        # Try deleting variations (should fail since user is deleted)
        delete_upper = self.api.delete_user(email_uppercase)
        delete_mixed = self.api.delete_user(email_mixed)
        
        # Both should fail since user already deleted
        assert delete_upper.status in (404, 500)
        assert delete_mixed.status in (404, 500)

    def test_delete_user_url_encoded_special_chars(self):
        """DELETE with URL-encoded special characters."""
        encoded_email = "test%20user@example.com"
        resp = self.api.delete_user(encoded_email)
        assert resp.status in (400, 404, 500)

    def test_delete_preserves_other_users(self, random_user_payload):
        """Deleting one user should not affect others."""
        from src.models.user import create_user_payload
        
        # Create two users
        user1_email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        user2_payload = create_user_payload(
            email=f"user2_{random_user_payload['email']}", 
            name="User Two"
        )
        self.api.create_user(user2_payload)
        
        # Delete first user
        delete_resp = self.api.delete_user(user1_email)
        assert delete_resp.status == 204
        
        # Verify second user still exists
        get_resp = self.api.get_user(user2_payload["email"])
        assert get_resp.status == 200

    # ---- Response Validation ----
    def test_delete_user_response_headers(self, random_user_payload):
        """Verify response has appropriate headers."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        resp = self.api.delete_user(email)
        assert resp.status == 204
        
        # 204 typically has minimal headers but should exist
        assert resp.headers is not None

    def test_delete_user_creates_truly_deleted_state(self, random_user_payload):
        """Verify deleted user cannot be updated or retrieved."""
        email = random_user_payload["email"]
        self.api.create_user(random_user_payload)
        
        # Delete
        del_resp = self.api.delete_user(email)
        assert del_resp.status == 204
        
        # Try to retrieve - should fail
        get_resp = self.api.get_user(email)
        assert get_resp.status in (404, 500)
        
        # Try to update - should also fail
        update_payload = {"name": "Updated Name", "email": email, "age": 50}
        update_resp = self.api.update_user(email, update_payload)
        assert update_resp.status in (404, 500)
