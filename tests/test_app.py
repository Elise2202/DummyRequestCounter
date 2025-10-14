from fastapi.testclient import TestClient
from app.app import app


class FakeRedis:
    """Very small in-memory fake to avoid needing a real Redis in unit tests."""

    def __init__(self):
        self.store = {}

    def incr(self, key):
        self.store[key] = int(self.store.get(key, 0)) + 1
        return self.store[key]

    def get(self, key):
        value = self.store.get(key)
        return None if value is None else str(value)

    def delete(self, key):
        self.store.pop(key, None)


def patch_redis(monkeypatch):
    # Replace the global redis client inside the application during tests
    from app import app as app_module  # import the module that contains "redis"
    monkeypatch.setattr(app_module, "redis", FakeRedis())


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_counter_increments(monkeypatch):
    patch_redis(monkeypatch)

    r1 = client.get("/")
    r2 = client.get("/")

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["hits"] == "1"
    assert r2.json()["hits"] == "2"


def test_reset(monkeypatch):
    patch_redis(monkeypatch)

    # bump once
    client.get("/")

    # reset
    r = client.post("/reset")
    assert r.status_code == 200
    assert r.json()["reset"] is True

    # first hit after reset should be 1
    r = client.get("/")
    assert r.json()["hits"] == "1"
