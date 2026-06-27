from tests.config import BASE_URL

PLAYWRIGHT_CONFIG = {
    "base_url": BASE_URL,
    "use": {
        "headless": True,
        "trace": "retain-on-failure",
    },
}
