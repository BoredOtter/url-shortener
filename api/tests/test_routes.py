import hashlib
import unittest

from fastapi.testclient import TestClient

from app import routes
from app.factory import create_app


class FakeRedis:
    def __init__(self) -> None:
        self.data: dict[str, str] = {}

    def ping(self) -> bool:
        return True

    def setex(self, key: str, _ttl: int, value: str) -> None:
        self.data[key] = value

    def get(self, key: str) -> str | None:
        return self.data.get(key)


class RoutesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._original_redis = routes.redis_client
        self.fake_redis = FakeRedis()
        routes.redis_client = self.fake_redis

        self.app = create_app()
        self.client_context = TestClient(self.app)
        self.client = self.client_context.__enter__()

    def tearDown(self) -> None:
        self.client_context.__exit__(None, None, None)
        routes.redis_client = self._original_redis

    def test_health_and_readiness_endpoints(self):
        self.assertEqual(self.client.get("/healthz").json(), {"status": "live"})
        self.assertEqual(self.client.get("/livez").json(), {"status": "live"})

        startup_response = self.client.get("/startupz")
        self.assertEqual(startup_response.status_code, 200)
        self.assertEqual(startup_response.json(), {"status": "started"})

        ready_response = self.client.get("/readyz")
        self.assertEqual(ready_response.status_code, 200)
        self.assertEqual(
            ready_response.json(),
            {
                "status": "ready",
                "dependencies": {"redis": "ok"},
            },
        )

    def test_shorten_and_redirect_flow(self):
        response = self.client.post("/api/shorten", json={"url": "example.com/path"})
        self.assertEqual(response.status_code, 200)

        body = response.json()
        expected_long_url = "https://example.com/path"
        expected_short_id = hashlib.md5(expected_long_url.encode()).hexdigest()[:6]

        self.assertEqual(body["long_url"], expected_long_url)
        self.assertTrue(body["short_url"].endswith(f"/api/{expected_short_id}"))

        redirect_response = self.client.get(f"/api/{expected_short_id}", follow_redirects=False)
        self.assertEqual(redirect_response.status_code, 307)
        self.assertEqual(redirect_response.headers["location"], expected_long_url)

    def test_redirect_returns_404_for_missing_id(self):
        response = self.client.get("/api/does-not-exist", follow_redirects=False)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "ShortURL not found"})


if __name__ == "__main__":
    unittest.main()
