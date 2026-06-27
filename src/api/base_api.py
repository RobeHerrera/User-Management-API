from typing import Optional

from playwright.sync_api import APIRequestContext


class BaseAPI:
    """Base class for API Object Model wrappers.

    Provides convenience methods that forward to an APIRequestContext
    while reducing boilerplate for headers, base URLs, etc.
    """

    def __init__(self, request_context: APIRequestContext, base_url: str):
        self._request = request_context
        self._base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # HTTP verb helpers
    # ------------------------------------------------------------------

    def get(self, path: str, **kwargs):
        url = f"{self._base_url}{path}"
        return self._request.get(url, **kwargs)

    def post(self, path: str, payload: Optional[dict] = None, **kwargs):
        url = f"{self._base_url}{path}"
        kwargs.setdefault("headers", {})
        if payload is not None:
            kwargs["data"] = payload
            kwargs["headers"].setdefault("Content-Type", "application/json")
        return self._request.post(url, **kwargs)

    def put(self, path: str, payload: Optional[dict] = None, **kwargs):
        url = f"{self._base_url}{path}"
        kwargs.setdefault("headers", {})
        if payload is not None:
            kwargs["data"] = payload
            kwargs["headers"].setdefault("Content-Type", "application/json")
        return self._request.put(url, **kwargs)

    def delete(self, path: str, **kwargs):
        url = f"{self._base_url}{path}"
        return self._request.delete(url, **kwargs)