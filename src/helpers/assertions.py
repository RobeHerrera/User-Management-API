def assert_user_shape(user: dict):
    """Verify that a response dict has the expected User shape."""
    assert isinstance(user, dict), f"Expected dict, got {type(user)}"
    assert {"name", "email", "age"}.issubset(user.keys()), (
        f"Missing one or more required keys. Got: {set(user.keys())}"
    )
    assert isinstance(user["name"], str), f"name should be str, got {type(user['name'])}"
    assert isinstance(user["email"], str), f"email should be str, got {type(user['email'])}"
    assert isinstance(user["age"], int), f"age should be int, got {type(user['age'])}"


def assert_error_response(body: dict):
    """Verify that a response body is an error dict with an 'error' key."""
    assert isinstance(body, dict), f"Expected dict, got {type(body)}"
    assert "error" in body, f"Missing 'error' key in {body}"