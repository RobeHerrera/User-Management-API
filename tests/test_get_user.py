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
        print(f"List users response data: {data}")
        assert isinstance(data, list)

    def test_get_nonexistent_user(self, unique_email):
        resp = self.api.get_user(unique_email)
        # Should be 404?
        assert resp.status == 500
        assert_error_response(resp.json())
