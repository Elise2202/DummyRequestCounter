# tests/test_app.py
from fastapi.testclient import TestClient
from app.app import app

# --- A tiny in-memory fake Redis so tests don't need the real server ---
class FakeRedis:
    def __init__(self):
        self.store = {}

    def incr(self, key):
        self.store[key] = int(self.store.get(key, 0)) + 1
        return self.store[key]

    def get(self, key):
        v = self.store.get(key)
        return None if v is None else str(v)  # app expects a str from redis client

    def delete(self, key):
        self.store.pop(key, None)

# Helper to replace the global redis client inside the app during tests
def patch_redis(monkeypatch):
    from app import app as app_module  # this is the app.py module inside app/
    monkeypatch.setattr(app_module, "redis", FakeRedis())

client = TestClient(app)


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"


def test_counter_increments(monkeypatch):
    patch_redis(monkeypatch)
    r1 = client.get("/")
    r2 = client.get("/")
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["hits"] == "1"
    assert r2.json()["hits"] == "2"


def test_reset(monkeypatch):
    patch_redis(monkeypatch)
    # bump it once
    client.get("/")
    # reset
    r = client.post("/reset")
    assert r.status_code == 200 and r.json()["reset"] is True
    # after reset, first hit should be 1 again
    r = client.get("/")
    assert r.json()["hits"] == "1"


