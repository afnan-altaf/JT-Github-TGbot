import re

from telethon import events

import config
from bot import Irene
from crypto.vault import seal, unseal
from database.models import LinkedRepo
from database.store import DataStore
from ghub.events import SUPPORTED
from ghub.ghclient import GhApi, GhApiError
from helpers import LOGGER, send_message, new_task
from helpers.buttons import SmartButtons
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


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}](repos|myrepos)(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def repos_handler(event):
    links = await DataStore.get().list_repos(event.chat_id)
    if not links:
        await send_message(event.chat_id, "No repositories linked in this chat. Use /addrepo to add one.")
        return

    lines = ["<b>📦 Linked Repositories:</b>\n"]
    for i, link in enumerate(links, 1):
        dest = f" → <code>{link.peer_id}</code>" if link.peer_id else ""
        lines.append(f"{i}. <code>{link.name}</code>{dest}  [hook: {link.hook_id}]")

    await send_message(event.chat_id, "\n".join(lines), parse_mode="html")


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}]addrepo(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def addrepo_handler(event):
    api = await _get_api(event.sender_id)
    if not api:
        await send_message(event.chat_id, "Please /connect your GitHub account first.")
        return

    args = event.pattern_match.string.split(None, 1)
    repo_name = args[1].strip() if len(args) > 1 else ""

    if repo_name:
        owner, repo = split_repo(repo_name)
        if not owner or not repo:
            await send_message(event.chat_id, "Invalid format. Use: /addrepo owner/repo")
            return

        chat_token = seal(str(event.chat_id))
        webhook_url = f"{config.PUBLIC_URL}/webhook/{chat_token}"
        default_evts = [e.key for e in SUPPORTED]

        try:
            hook = await api.create_hook(owner, repo, webhook_url, config.HOOK_SECRET, default_evts)
        except GhApiError as exc:
            if exc.status in (401, 403):
                await DataStore.get().clear_token(event.sender_id)
                await send_message(event.chat_id, "⚠️ GitHub auth error. Please /connect again.")
                return
            await send_message(event.chat_id, f"⚠️ Webhook creation failed: {exc.message}")
            return

        await DataStore.get().add_repo(event.chat_id, LinkedRepo(name=repo_name, hook_id=hook["id"]))
        await send_message(event.chat_id, f"✅ Repository <b>{repo_name}</b> linked!", parse_mode="html")
    else:
        try:
            repos = await api.list_repos(page=1, per_page=5)
        except GhApiError as exc:
            await send_message(event.chat_id, f"GitHub API error: {exc.message}")
            return

        if not repos:
            await send_message(event.chat_id, "No repositories found on your account.")
            return

        sb = SmartButtons()
        for r in repos:
            sb.button(r["full_name"], callback_data=f"c:ar:id:{r['id']}")
        sb.button("Next ➡️", callback_data="c:ar:pg:2", position="footer")
        await send_message(
            event.chat_id,
            "Select a repository to add:",
            buttons=sb.build_menu(b_cols=1, f_cols=1),
        )


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}]removerepo(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def removerepo_handler(event):
    args = event.pattern_match.string.split(None, 1)
    if len(args) < 2:
        await send_message(event.chat_id, "Usage: /removerepo owner/repo")
        return

    repo_name = args[1].strip()
    owner, repo = split_repo(repo_name)
    if not owner or not repo:
        await send_message(event.chat_id, "Invalid format. Use: /removerepo owner/repo")
        return

    store = DataStore.get()
    link = await store.get_repo(event.chat_id, repo_name)
    if not link:
        await send_message(event.chat_id, f"Repository <b>{repo_name}</b> is not linked to this chat.", parse_mode="html")
        return

    api = await _get_api(event.sender_id)
    if api:
        try:
            await api.delete_hook(owner, repo, link.hook_id)
        except GhApiError:
            pass

    await store.remove_repo(event.chat_id, repo_name)
    await send_message(event.chat_id, f"✅ Repository <b>{repo_name}</b> unlinked.", parse_mode="html")
