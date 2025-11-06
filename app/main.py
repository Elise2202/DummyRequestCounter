import os
import redis
from fastapi import FastAPI

app = FastAPI()

# Redis config
redis_host = os.environ.get("REDIS_HOST", "redis")
redis_port = int(os.environ.get("REDIS_PORT", "6379"))
r = redis.Redis(host=redis_host, port=redis_port, db=0)


@app.get("/")
def read_root():
    hits = r.incr("hits")
    log_data = (
        f'{{"message":"Hello from FastAPI!", "hits": {hits}}}\n'
    )

    # Ensure log directory exists
    os.makedirs("/var/log/app", exist_ok=True)

    # Write to log file
    with open("/var/log/app/app.log", "a", encoding="utf-8") as f:
        f.write(log_data)

    return {"message": "Hello from FastAPI!", "hits": hits}
