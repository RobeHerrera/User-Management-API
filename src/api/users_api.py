from typing import Optional

from src.api.base_api import BaseAPI
from tests.config import AUTH_TOKEN


class UsersAPI(BaseAPI):
    """API Object Model for the /users endpoints."""

    USERS_PATH = "/users"

    def __init__(self, request_context, base_url: str, auth_token: str = AUTH_TOKEN):
        super().__init__(request_context, base_url)
        self._auth_token = auth_token

    # ------------------------------------------------------------------
    # Endpoint methods
    # ------------------------------------------------------------------

    def list_users(self):
        """GET /users — list all users."""
        return self.get(self.USERS_PATH)

    def create_user(self, payload: dict):
        """POST /users — create a new user."""
        return self.post(self.USERS_PATH, payload=payload)

    def get_user(self, email: str):
        """GET /users/{email} — get a single user."""
        return self.get(f"{self.USERS_PATH}/{email}")

    def update_user(self, email: str, payload: dict):
        """PUT /users/{email} — update an existing user."""
        return self.put(f"{self.USERS_PATH}/{email}", payload=payload)

    def delete_user(self, email: str):
        """DELETE /users/{email} — delete a user (requires auth)."""
        return self.delete(
            f"{self.USERS_PATH}/{email}",
            headers={"Authentication": self._auth_token},
        )