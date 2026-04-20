import re

from telethon import events

import config
from bot import Irene
from database.store import DataStore
from helpers import send_message, new_task
from helpers.buttons import SmartButtons
from helpers.guard import ban_check

_prefixes = "".join(re.escape(p) for p in config.COMMAND_PREFIXES)


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}]settings(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def settings_handler(event):
    links = await DataStore.get().list_repos(event.chat_id)
    if not links:
        await send_message(event.chat_id, "No repositories linked. Use /addrepo first.")
        return

    sb = SmartButtons()
    for link in links:
        sb.button(link.name, callback_data=f"c:r:{link.name}")

    await send_message(
        event.chat_id,
        "<b>⚙️ Select a repository to configure:</b>",
        parse_mode="html",
        buttons=sb.build_menu(b_cols=1),
    )
