import os
import re
import sys

from telethon import events

import config
from bot import Irene
from database.store import DataStore
from helpers import send_message, edit_message, new_task
from helpers.guard import ban_check
from helpers.logger import LOGGER

_prefixes = "".join(re.escape(p) for p in config.COMMAND_PREFIXES)


async def check_pending_reboot():
    store = DataStore.get()
    pending = await store.get_restart_pending()
    if not pending:
        return
    chat_id = pending.get("chat_id")
    msg_id = pending.get("msg_id")
    await store.clear_restart_pending()
    if chat_id and msg_id:
        try:
            await edit_message(chat_id, msg_id, "✅ <b>Bot restarted successfully!</b>", parse_mode="html")
        except Exception:
            await send_message(chat_id, "✅ Bot restarted successfully!")


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}]restart(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def restart_handler(event):
    if event.sender_id != config.ADMIN_ID:
        from modules.sudo import is_sudo
        if not await is_sudo(event.sender_id):
            return

    msg = await send_message(event.chat_id, "🔄 <b>Restarting bot...</b>", parse_mode="html")
    if msg:
        await DataStore.get().set_restart_pending(event.chat_id, msg.id)

    LOGGER.info("Restart requested — exiting process.")
    os.execv(sys.executable, [sys.executable] + sys.argv)
