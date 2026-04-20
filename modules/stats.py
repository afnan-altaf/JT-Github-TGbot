import re
from datetime import datetime, timedelta

from telethon import events

import config
from bot import Irene
from database.store import DataStore
from helpers import send_message, new_task
from helpers.guard import ban_check

_prefixes = "".join(re.escape(p) for p in config.COMMAND_PREFIXES)


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}]stats(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def stats_handler(event):
    if event.sender_id != config.ADMIN_ID:
        from modules.sudo import is_sudo
        if not await is_sudo(event.sender_id):
            return

    store = DataStore.get()
    now = datetime.utcnow()
    daily = await store.count_users({"is_group": False, "last_activity": {"$gte": now - timedelta(days=1)}})
    weekly = await store.count_users({"is_group": False, "last_activity": {"$gte": now - timedelta(weeks=1)}})
    monthly = await store.count_users({"is_group": False, "last_activity": {"$gte": now - timedelta(days=30)}})
    total_users = await store.count_users({"is_group": False})
    total_groups = await store.count_users({"is_group": True})

    text = (
        "<b>📊 JT GitHub Notify Bot — Stats</b>\n"
        "<b>━━━━━━━━━━━━━━━━</b>\n"
        f"<b>Daily active users:</b> {daily}\n"
        f"<b>Weekly active users:</b> {weekly}\n"
        f"<b>Monthly active users:</b> {monthly}\n"
        f"<b>Total users:</b> {total_users}\n"
        f"<b>Total groups:</b> {total_groups}"
    )
    await send_message(event.chat_id, text, parse_mode="html")
