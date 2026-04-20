import asyncio
import os
from typing import Optional

from telethon.tl.types import Message

from bot import Irene
from helpers.logger import LOGGER


async def send_message(chat_id: int, text: str, **kwargs) -> Optional[Message]:
    try:
        return await Irene.send_message(chat_id, text, **kwargs)
    except Exception as e:
        LOGGER.error(f"send_message failed: {e}")
        return None


async def edit_message(chat_id: int, msg_id: int, text: str, **kwargs) -> Optional[Message]:
    try:
        return await Irene.edit_message(chat_id, msg_id, text, **kwargs)
    except Exception as e:
        LOGGER.error(f"edit_message failed: {e}")
        return None


def new_task(func):
    import functools

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        asyncio.create_task(func(*args, **kwargs))
    return wrapper


async def clean_download(path: str):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception as e:
        LOGGER.warning(f"clean_download failed: {e}")


def split_repo(full_name: str):
    parts = full_name.split("/", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return None, None
