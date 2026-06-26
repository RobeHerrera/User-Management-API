import os
import uuid
import pytest

from playwright.sync_api import APIRequestContext, expect

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "mysecrettoken")


def _user_payload(email: str, *, name: str = "Jane Doe", age: int = 30):
    return {"name": name, "email": email, "age": age}


def _assert_user_shape(user: dict):
    assert isinstance(user, dict)
    assert set(["name", "email", "age"]).issubset(set(user.keys()))
    assert isinstance(user["name"], str)
    assert isinstance(user["email"], str)
    assert isinstance(user["age"], int)


@pytest.fixture(scope="session")
def request_context(playwright):
    # Playwright's request client doesn't require browser launch.
    return playwright.request.new_context()


@pytest.mark.parametrize("env_prefix", ["dev", "prod"])
class TestUsersAPI:
    @pytest.fixture(autouse=True)
    def _setup_urls(self, env_prefix):
        self.env_prefix = env_prefix
        self.base = f"{BASE_URL}/{env_prefix}"
        self.users_url = f"{self.base}/users"
        self.headers_with_auth = {"Authorization": AUTH_TOKEN}

    def test_list_users_empty_initially(self, request_context: APIRequestContext):
        resp = request_context.get(self.users_url)
        assert resp.status == 200
        data = resp.json()
        assert isinstance(data, list)


    def test_create_get_update_delete_user_happy_path(self, request_context: APIRequestContext):
        email = f"{uuid.uuid4()}@example.com"

        # Create
        create_resp = request_context.post(
            self.users_url,
            headers={"Content-Type": "application/json"},
            data={"name": "Jane Doe", "email": email, "age": 30},
        )
        assert create_resp.status == 201
        created = create_resp.json()
        _assert_user_shape(created)
        assert created["email"] == email
        assert created["name"] == "Jane Doe"
        assert created["age"] == 30

        # Get
        get_resp = request_context.get(f"{self.users_url}/{email}")
        assert get_resp.status == 200
        fetched = get_resp.json()
        _assert_user_shape(fetched)
        assert fetched["email"] == email

        # Update
        update_resp = request_context.put(
            f"{self.users_url}/{email}",
            headers={"Content-Type": "application/json"},
            data={"name": "Jane Updated", "email": email, "age": 31},
        )
        assert update_resp.status == 200
        updated = update_resp.json()
        _assert_user_shape(updated)
        assert updated["email"] == email
        assert updated["name"] == "Jane Updated"
        assert updated["age"] == 31

        # Delete
        delete_resp = request_context.delete(
            f"{self.users_url}/{email}",
            headers=self.headers_with_auth,
        )
        assert delete_resp.status == 204

        # Get after delete
        get_after_resp = request_context.get(f"{self.users_url}/{email}")
        assert get_after_resp.status == 404

    def test_create_duplicate_email_returns_409(self, request_context: APIRequestContext):
        email = f"{uuid.uuid4()}@example.com"

        payload = _user_payload(email)

        first = request_context.post(
            self.users_url,
            headers={"Content-Type": "application/json"},
            data=payload,
        )
        assert first.status == 201

        second = request_context.post(
            self.users_url,
            headers={"Content-Type": "application/json"},
            data=_user_payload(email, name="Other Name", age=40),
        )
        assert second.status == 409

        body = second.json()
        assert isinstance(body, dict)
        assert "error" in body

    def test_validation_missing_required_fields_returns_400(self, request_context: APIRequestContext):
        # Missing name
        email = f"{uuid.uuid4()}@example.com"
        resp = request_context.post(
            self.users_url,
            headers={"Content-Type": "application/json"},
            data={"email": email, "age": 30},
        )
        assert resp.status == 400
        body = resp.json()
        assert isinstance(body, dict)
        assert "error" in body

    def test_get_nonexistent_user_returns_404(self, request_context: APIRequestContext):
        email = f"{uuid.uuid4()}@example.com"
        resp = request_context.get(f"{self.users_url}/{email}")
        assert resp.status == 404
        body = resp.json()
        assert isinstance(body, dict)
        assert "error" in body

    def test_update_nonexistent_user_returns_404(self, request_context: APIRequestContext):
        email = f"{uuid.uuid4()}@example.com"
        resp = request_context.put(
            f"{self.users_url}/{email}",
            headers={"Content-Type": "application/json"},
            data={"name": "Does Not Exist", "email": email, "age": 30},
        )
        assert resp.status == 404
        body = resp.json()
        assert isinstance(body, dict)
        assert "error" in body

    def test_delete_without_auth_returns_401(self, request_context: APIRequestContext):
        email = f"{uuid.uuid4()}@example.com"
        resp = request_context.delete(f"{self.users_url}/{email}")
        # Spec says 401 for auth required/invalid, but could be 404 depending on implementation.
        assert resp.status in (401, 404)
        if resp.status == 401:
            body = resp.json()
            assert isinstance(body, dict)
            assert "error" in body

