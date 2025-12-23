#store.py
# This is the local storage engine for the single nodes
# this provides In-memory access, Write-ahead logging, Crash recovery

import json
import asyncio

class KVStore:
    def __init__(self, wal_path="data/wal.log"):
        self.data = {}
        self.lock = asyncio.Lock()
        self.wal_path = wal_path
        self.recover()

    def recover(self):
        try:
            with open(self.wal_path, "r") as f:
                for line in f:
                    key, record = json.loads(line)
                    self.data[key] = record
        except FileNotFoundError:
            # Fresh node, No WAL found
            pass

    async def _append_wal(self, key, record):
        #append only
        with open(self.wal_path, "a") as f:
            f.write(json.dumps((key, record)) + "\n")

    async def put(self, key, value, timestamp):
        async with self.lock:
            record = {
                "value": value,
                "timestamp": timestamp,
                "deleted": False
            }
            # Write to WAL before updating memory
            await self._append_wal(key, record)
            self.data[key] = record

    async def delete(self, key, timestamp):
        async with self.lock:
            record = {
                "value": None,
                "timestamp": timestamp,
                "deleted": True
            }

            await self._append_wal(key, record)
            self.data[key] = record

    async def get(self, key):
        return self.data.get(key)

