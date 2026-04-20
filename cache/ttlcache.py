import asyncio
import time
from typing import Any, Optional


class TTLCache:
    def __init__(self):
        self._store: dict = {}
        self._lock = asyncio.Lock()

    async def get(self, key: Any) -> Optional[Any]:
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires = entry
            if expires and time.monotonic() > expires:
                del self._store[key]
                return None
            return value

    async def put(self, key: Any, value: Any, ttl: Optional[float] = None):
        async with self._lock:
            expires = (time.monotonic() + ttl) if ttl else None
            self._store[key] = (value, expires)

    async def delete(self, key: Any):
        async with self._lock:
            self._store.pop(key, None)

    async def clear(self):
        async with self._lock:
            self._store.clear()
