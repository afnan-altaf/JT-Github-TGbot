import re

from telethon import events

import config
from bot import Irene
from database.store import DataStore
from helpers import send_message, new_task
from helpers.guard import ban_check

_prefixes = "".join(re.escape(p) for p in config.COMMAND_PREFIXES)


def is_owner(user_id: int) -> bool:
    return user_id == config.ADMIN_ID


async def is_sudo(user_id: int) -> bool:
    if is_owner(user_id):
        return True
    sudo_ids = await DataStore.get().get_sudo_ids()
    return user_id in sudo_ids


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}](auth|addadmin)(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def auth_handler(event):
    if not is_owner(event.sender_id):
        return

    args = event.pattern_match.string.split(None, 1)
    if len(args) < 2:
        await send_message(event.chat_id, "Usage: /auth <user_id>")
        return

    try:
        target_id = int(args[1].strip())
    except ValueError:
        await send_message(event.chat_id, "Invalid user ID.")
        return

    await DataStore.get().add_sudo(target_id)
    await send_message(event.chat_id, f"✅ User <code>{target_id}</code> added as sudo admin.", parse_mode="html")


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}](deauth|removeadmin)(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def deauth_handler(event):
    if not is_owner(event.sender_id):
        return

    args = event.pattern_match.string.split(None, 1)
    if len(args) < 2:
        await send_message(event.chat_id, "Usage: /deauth <user_id>")
        return

    try:
        target_id = int(args[1].strip())
    except ValueError:
        await send_message(event.chat_id, "Invalid user ID.")
        return

    await DataStore.get().remove_sudo(target_id)
    await send_message(event.chat_id, f"✅ User <code>{target_id}</code> removed from sudo.", parse_mode="html")


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}]ban(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def ban_handler(event):
    if not await is_sudo(event.sender_id):
        return

    args = event.pattern_match.string.split(None, 1)
    if len(args) < 2:
        await send_message(event.chat_id, "Usage: /ban <user_id>")
        return

    try:
        target_id = int(args[1].strip())
    except ValueError:
        await send_message(event.chat_id, "Invalid user ID.")
        return

    if target_id == config.ADMIN_ID:
        await send_message(event.chat_id, "Cannot ban the owner.")
        return

    await DataStore.get().ban_user(target_id)
    await send_message(event.chat_id, f"✅ User <code>{target_id}</code> has been banned.", parse_mode="html")


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}]unban(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def unban_handler(event):
    if not await is_sudo(event.sender_id):
        return

    args = event.pattern_match.string.split(None, 1)
    if len(args) < 2:
        await send_message(event.chat_id, "Usage: /unban <user_id>")
        return

    try:
        target_id = int(args[1].strip())
    except ValueError:
        await send_message(event.chat_id, "Invalid user ID.")
        return

    await DataStore.get().unban_user(target_id)
    await send_message(event.chat_id, f"✅ User <code>{target_id}</code> has been unbanned.", parse_mode="html")


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}]banlist(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def banlist_handler(event):
    if not await is_sudo(event.sender_id):
        return

    banned = await DataStore.get().get_banned()
    if not banned:
        await send_message(event.chat_id, "No banned users.")
        return

    lines = ["<b>🚫 Banned Users:</b>\n"]
    for doc in banned:
        lines.append(f"• <code>{doc['user_id']}</code>")
    await send_message(event.chat_id, "\n".join(lines), parse_mode="html")
