import re

from telethon import events

import config
from bot import Irene
from helpers import send_message, new_task
from helpers.guard import ban_check

_prefixes = "".join(re.escape(p) for p in config.COMMAND_PREFIXES)


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}]reload(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def reload_handler(event):
    try:
        from modules.admins import get_admin_cache
        cache = get_admin_cache()
        await cache.delete(event.chat_id)
        await send_message(event.chat_id, "✅ Admin cache cleared for this chat.")
    except Exception as e:
        await send_message(event.chat_id, f"Failed to reload: {e}")
