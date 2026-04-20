from database.store import DataStore


async def track(user_id: int, chat_id: int):
    store = DataStore.get()
    is_group = chat_id < 0
    await store.track_user(user_id, is_group=is_group)
