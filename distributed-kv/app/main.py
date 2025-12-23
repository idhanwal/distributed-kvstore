#main.py


from fastapi import FastAPI
import time

from app.config import NODES, REPLICATION_FACTOR
from app.ring import HashRing
from app.store import KVStore
from app.coordinator import quorum_read, quorum_write

app = FastAPI()

ring = HashRing(NODES)
store = KVStore()

#Internal Replica Apis

@app.put("/replica/{key}")
async def replica_put(key: str, payload: dict):
    await store.put(key, payload["value"], payload["timestamp"])
    return {"status": "OK"}

@app.get("/replica/{key}")
async def replica_get(key: str):
    return await store.get(key)

@app.delete("/replica/{key}")
async def replica_delete(key: str, payload: dict):
    await store.delete(key, payload["timestamp"])
    return {"status": "OK"}


# Client facing APIs

@app.put("/kv/{key}")
async def put_key(key: str, payload: dict):
    replicas = ring.get_replicas(key, REPLICATION_FACTOR)

    success = await quorum_write(replicas, key, payload["value"])
    return {"success": success}

@app.get("/kv/{key}")
async def get_key(key: str):
    replicas = ring.get_replicas(key, REPLICATION_FACTOR)
    return await quorum_read(replicas, key)

@app.delete("kv/{key}")
async def delete_key(key: str):
    replicas = ring.get_replicas(key, REPLICATION_FACTOR)

    await quorum_write(replicas, key, None)
    return {"deleted": True}