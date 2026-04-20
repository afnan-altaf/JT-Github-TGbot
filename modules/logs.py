import os
import re

from telethon import events

import config
from bot import Irene
from helpers import send_message, new_task
from helpers.guard import ban_check

_prefixes = "".join(re.escape(p) for p in config.COMMAND_PREFIXES)
LOG_FILE = "bot.log"


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}]logs(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def logs_handler(event):
    if event.sender_id != config.ADMIN_ID:
        from modules.sudo import is_sudo
        if not await is_sudo(event.sender_id):
            return

    if not os.path.exists(LOG_FILE):
        await send_message(event.chat_id, "No log file found.")
        return

    try:
        await Irene.send_file(event.chat_id, LOG_FILE, caption="📋 Bot log file")
    except Exception as e:
        await send_message(event.chat_id, f"Failed to send log: {e}")
