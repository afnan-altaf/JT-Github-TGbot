import re

from telethon import events

import config
from bot import Irene
from crypto.vault import unseal
from database.store import DataStore
from ghub.ghclient import GhApi, GhApiError
from helpers import send_message, new_task
from helpers.guard import ban_check
from helpers.utils import split_repo

_prefixes = "".join(re.escape(p) for p in config.COMMAND_PREFIXES)


async def _get_api(tg_id: int):
    account = await DataStore.get().get_account(tg_id)
    if not account or not account.token_enc:
        return None
    try:
        return GhApi(unseal(account.token_enc))
    except Exception:
        return None


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}](del|deleterepo)(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def deleterepo_handler(event):
    args = event.pattern_match.string.split(None, 1)
    if len(args) < 2:
        await send_message(event.chat_id, "Usage: /del owner/repo")
        return

    repo_name = args[1].strip()
    owner, repo = split_repo(repo_name)
    if not owner or not repo:
        await send_message(event.chat_id, "Invalid format. Use: /del owner/repo")
        return

    api = await _get_api(event.sender_id)
    if not api:
        await send_message(event.chat_id, "Please /connect your GitHub account first.")
        return

    try:
        await api.delete_repo(owner, repo)
        await DataStore.get().remove_repo(event.chat_id, repo_name)
        await send_message(event.chat_id, f"✅ Repository <b>{repo_name}</b> deleted from GitHub.", parse_mode="html")
    except GhApiError as exc:
        if exc.status in (401, 403):
            await DataStore.get().clear_token(event.sender_id)
            await send_message(event.chat_id, "⚠️ GitHub auth error. Please /connect again.")
            return
        await send_message(event.chat_id, f"Failed: {exc.message}")


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}]setdescription(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def setdesc_handler(event):
    args = event.pattern_match.string.split(None, 2)
    if len(args) < 3:
        await send_message(event.chat_id, "Usage: /setdescription owner/repo New description here")
        return

    repo_name, desc = args[1].strip(), args[2].strip()
    owner, repo = split_repo(repo_name)
    if not owner or not repo:
        await send_message(event.chat_id, "Invalid repo format.")
        return

    api = await _get_api(event.sender_id)
    if not api:
        await send_message(event.chat_id, "Please /connect your GitHub account first.")
        return

    try:
        await api.update_repo(owner, repo, description=desc)
        await send_message(event.chat_id, f"✅ Description updated for <b>{repo_name}</b>.", parse_mode="html")
    except GhApiError as exc:
        await send_message(event.chat_id, f"Failed: {exc.message}")


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}]sethandle(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def sethandle_handler(event):
    args = event.pattern_match.string.split(None, 2)
    if len(args) < 3:
        await send_message(event.chat_id, "Usage: /sethandle owner/repo new-name")
        return

    repo_name, new_name = args[1].strip(), args[2].strip()
    owner, repo = split_repo(repo_name)
    if not owner or not repo:
        await send_message(event.chat_id, "Invalid repo format.")
        return

    api = await _get_api(event.sender_id)
    if not api:
        await send_message(event.chat_id, "Please /connect your GitHub account first.")
        return

    try:
        await api.update_repo(owner, repo, name=new_name)
        await send_message(event.chat_id, f"✅ Repository renamed to <b>{new_name}</b>.", parse_mode="html")
    except GhApiError as exc:
        await send_message(event.chat_id, f"Failed: {exc.message}")
