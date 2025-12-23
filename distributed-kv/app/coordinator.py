# coordinator.py
# The coordinator logic implements Dynamo's quorum protocol
# Any node can become a coordinator for any request


import asyncio
import httpx
import time

from app.config import WRITE_QUORUM, READ_QUORUM

async def quorum_write(replicas, key, value):
    timestamp = time.time()

    payload = {
        "value": value,
        "timestamp": timestamp
    }

    async with httpx.AsyncClient(timeout=1.0) as client:
        tasks = []

        for replica in replicas:
            tasks.append(
                client.put(f"{replica}/replica/{key}", json=payload)
            )

        responses = await asyncio.gather(
            *tasks, return_exceptions=True
        )

    success_count = sum(
        1 for r in responses if not isinstance(r, Exception)
    )
    return success_count >= WRITE_QUORUM

async def quorum_read(replicas, key):
    async with httpx.AsyncClient(timeout=1.0) as client:
        tasks = []

        for replica in replicas:
            tasks.append(
                client.get(f"{replica}/replica/{key}")
            )

        responses = await asyncio.gather(
            *tasks, return_exceptions=True
        )

        records = [
            r.json() for r in responses
            if not isinstance(r, Exception) and r.json() is not None
        ]

        if not records:
            return None

        latest = max(records, key=lambda r: r["timestamp"])

        return latest