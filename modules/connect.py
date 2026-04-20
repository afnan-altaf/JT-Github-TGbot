import re

from telethon import events

import config
from bot import Irene
from crypto.vault import seal
from database.models import Account
from database.store import DataStore
from ghub.ghclient import GhApi, GhApiError
from ghub.oauth import build_auth_url, exchange_code
from helpers import LOGGER, send_message, new_task
from helpers.guard import ban_check

_prefixes = "".join(re.escape(p) for p in config.COMMAND_PREFIXES)


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}](connect|login)(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def connect_handler(event):
    if event.chat_id != event.sender_id:
        await send_message(event.chat_id, "⚠️ Please use /connect in a <b>private chat</b> with me.", parse_mode="html")
        return

    existing = await DataStore.get().get_account(event.sender_id)
    if existing and existing.token_enc:
        await send_message(
            event.chat_id,
            "✅ You already have a GitHub account connected.\n"
            "Use /logout to disconnect it first.",
        )
        return

    url = build_auth_url(state=str(event.sender_id))
    await send_message(
        event.chat_id,
        f"🔗 <b>Connect your GitHub account</b>\n\n"
        f'<a href="{url}">Click here to authorize</a>\n\n'
        "After granting access, return here — the bot will connect automatically.",
        parse_mode="html",
        link_preview=False,
    )


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}](logout|disconnect)(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def logout_handler(event):
    store = DataStore.get()
    existing = await store.get_account(event.sender_id)
    if not existing or not existing.token_enc:
        await send_message(event.chat_id, "You don't have a GitHub account connected.")
        return

    await store.clear_token(event.sender_id)
    await send_message(event.chat_id, "✅ GitHub account disconnected successfully.")


async def handle_oauth(code: str, state: str):
    try:
        user_id = int(state)
    except ValueError:
        LOGGER.warning(f"Invalid OAuth state: {state}")
        return

    try:
        token = await exchange_code(code)
    except Exception as e:
        LOGGER.error(f"OAuth code exchange failed: {e}")
        await send_message(user_id, "❌ GitHub authentication failed. Please try /connect again.")
        return

    try:
        api = GhApi(token)
        me = await api.get_me()
        gh_login = me.get("login", "")
    except GhApiError as e:
        LOGGER.error(f"Failed to fetch GitHub user after OAuth: {e}")
        gh_login = ""

    enc_token = seal(token)
    account = Account(user_id=user_id, token_enc=enc_token, gh_login=gh_login)
    await DataStore.get().save_account(account)

    await send_message(
        user_id,
        f"✅ <b>GitHub account connected!</b>\n"
        f"<b>Login:</b> <code>{gh_login}</code>\n\n"
        "You can now use /addrepo to link repositories.",
        parse_mode="html",
    )
    LOGGER.info(f"OAuth success — user_id={user_id} gh_login={gh_login}")
