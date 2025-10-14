from fastapi import FastAPI
from redis import Redis


app = FastAPI()

# Read configuration from environment (defaults work in Compose and CI smoke test)
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
COUNTER_KEY = os.getenv("COUNTER_KEY", "hits")

redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def index():
    redis.incr(COUNTER_KEY)
    hits = redis.get(COUNTER_KEY)
    return {"message": "Hello from FastAPI!", "hits": hits}


@app.post("/reset")
def reset():
    redis.delete(COUNTER_KEY)
    return {"reset": True}
