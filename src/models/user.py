from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    name: str
    email: str
    age: int


def create_user_payload(
    email: str,
    name: str = "Jane Doe",
    age: int = 30,
) -> dict:
    """Build a JSON payload for creating/updating a user."""
    return {"name": name, "email": email, "age": age}