import functools

from database.store import DataStore
from helpers.logger import LOGGER


def ban_check(func):
    @functools.wraps(func)
    async def wrapper(event, *args, **kwargs):
        try:
            sender_id = event.sender_id if hasattr(event, "sender_id") else None
            if sender_id:
                store = DataStore.get()
                if await store.is_banned(sender_id):
                    return
        except Exception as e:
            LOGGER.warning(f"ban_check error: {e}")
        return await func(event, *args, **kwargs)
    return wrapper
