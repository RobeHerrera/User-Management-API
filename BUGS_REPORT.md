# Bugs Report — User Management API (E2E via Playwright APIRequestContext)

This report documents behavior that does **not** match `sdet_challenge_api.yml`.

## Environment prefix: `/dev`

### 1) `GET /dev/users/{email}` after deleting a user
- **Expected (spec):** `404`
- **Actual:** `500 INTERNAL SERVER ERROR`
- **Where discovered:** `tests/test_users_api.py::TestUsersAPI::test_create_get_update_delete_user_happy_path[dev]`
- **Notes:** The delete call returned `204`, but subsequent GET returned a server error.

### 2) Duplicate email handling
- **Endpoint:** `POST /dev/users`
- **Setup:** Create a user with email `X`, then POST another user with the **same** email `X`.
- **Expected (spec):** `409 Conflict`
- **Actual:** `500 INTERNAL SERVER ERROR`
- **Where discovered:** `tests/test_users_api.py::TestUsersAPI::test_create_duplicate_email_returns_409[dev]`

### 3) Non-existent user retrieval
- **Endpoint:** `GET /dev/users/{email}`
- **Expected (spec):** `404`
- **Actual:** `500 INTERNAL SERVER ERROR`
- **Where discovered:** `tests/test_users_api.py::TestUsersAPI::test_get_nonexistent_user_returns_404[dev]`

## Environment prefix: `/prod`

### 1) Delete requires auth token
- **Endpoint:** `DELETE /prod/users/{email}`
- **Expected (spec):** `204`
- **Actual:** `401 UNAUTHORIZED`
- **Where discovered:** `tests/test_users_api.py::TestUsersAPI::test_create_get_update_delete_user_happy_path[prod]`
- **Notes:** Test sends `Authorization: mysecrettoken`. The server appears to require a different auth header name/value format.

### 2) Duplicate email handling
- **Endpoint:** `POST /prod/users`
- **Expected (spec):** `409 Conflict`
- **Actual:** `500 INTERNAL SERVER ERROR`
- **Where discovered:** `tests/test_users_api.py::TestUsersAPI::test_create_duplicate_email_returns_409[prod]`

### 3) Non-existent user retrieval
- **Endpoint:** `GET /prod/users/{email}`
- **Expected (spec):** `404`
- **Actual:** `500 INTERNAL SERVER ERROR`
- **Where discovered:** `tests/test_users_api.py::TestUsersAPI::test_get_nonexistent_user_returns_404[prod]`

---

## Summary
Multiple endpoints return `500` where the OpenAPI spec expects `404` and `409`, plus `DELETE` in `/prod` returns `401` even when the test provides the documented token.

