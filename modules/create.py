import base64
import io
import os
import re
import zipfile

from telethon import events

import config
from bot import Irene
from crypto.vault import unseal
from database.store import DataStore
from ghub.ghclient import GhApi, GhApiError
from helpers import send_message, new_task
from helpers.botutils import clean_download
from helpers.guard import ban_check
from helpers.logger import LOGGER

_prefixes = "".join(re.escape(p) for p in config.COMMAND_PREFIXES)


async def _get_api(tg_id: int):
    account = await DataStore.get().get_account(tg_id)
    if not account or not account.token_enc:
        return None
    try:
        return GhApi(unseal(account.token_enc))
    except Exception:
        return None


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}]create(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def create_handler(event):
    api = await _get_api(event.sender_id)
    if not api:
        await send_message(event.chat_id, "Please /connect your GitHub account first.")
        return

    args = event.pattern_match.string.split(None, 1)
    if len(args) < 2:
        await send_message(
            event.chat_id,
            "Usage: /create repo-name\n\n"
            "Optionally reply with a .zip file to upload its contents to the new repo.",
        )
        return

    repo_name = args[1].strip().replace(" ", "-")
    try:
        result = await api.create_repo(repo_name)
        full_name = result.get("full_name", repo_name)
        html_url = result.get("html_url", "")
    except GhApiError as exc:
        if exc.status in (401, 403):
            await DataStore.get().clear_token(event.sender_id)
            await send_message(event.chat_id, "⚠️ GitHub auth error. Please /connect again.")
            return
        await send_message(event.chat_id, f"Failed to create repo: {exc.message}")
        return

    await send_message(
        event.chat_id,
        f"✅ Repository <b>{full_name}</b> created!\n<a href='{html_url}'>View on GitHub</a>",
        parse_mode="html",
        link_preview=False,
    )

    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        if reply and reply.file and reply.file.name.endswith(".zip"):
            msg = await send_message(event.chat_id, "📦 Uploading zip contents to repo...")
            path = await reply.download_media("/tmp/upload.zip")
            try:
                owner, repo = full_name.split("/", 1)
                with zipfile.ZipFile(path) as zf:
                    for name in zf.namelist():
                        if name.endswith("/"):
                            continue
                        data = zf.read(name)
                        b64 = base64.b64encode(data).decode()
                        await api.upload_file(owner, repo, name, b64, f"Add {name}")
                await msg.edit("✅ All files uploaded successfully!")
            except Exception as e:
                LOGGER.exception(f"Zip upload error: {e}")
                await msg.edit(f"⚠️ Upload failed: {e}")
            finally:
                await clean_download(path)
