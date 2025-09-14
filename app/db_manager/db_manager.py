from .singleton_decorator import singleton
from tinydb import TinyDB, where
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

_DB_PATH = '/config/routes_db.json'

@singleton
class DBManager:
    def __init__(self):
        self._db = TinyDB(_DB_PATH)
        self._lock = asyncio.Lock()

    def with_db(self, fn):
        return fn(self._db)

    async def with_db_async(self, fn):
        async with self._lock:
            db = self._ensure_db()
            return fn(db)

    def close(self):
        if self._db is not None:
            try:
                self._db.close()
            finally:
                self._db = None

    def reopen(self):
        if self._db is None:
            self._db = TinyDB(_DB_PATH)