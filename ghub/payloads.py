from ghub.markup import (
    format_push,
    format_issue,
    format_pr,
    format_fork,
    format_star,
    format_release,
    format_ping,
    format_generic,
)
from helpers.botutils import send_message
from helpers.logger import LOGGER
from database.store import DataStore


async def dispatch(chat_id: int, event: str, payload: dict):
    store = DataStore.get()
    repo_full = (payload.get("repository") or {}).get("full_name", "")

    dest_id = chat_id
    if repo_full:
        link = await store.get_repo(chat_id, repo_full)
        if link and link.peer_id:
            dest_id = link.peer_id

    if event == "push":
        text = format_push(payload)
    elif event in ("issues", "issue"):
        text = format_issue(payload)
    elif event == "pull_request":
        text = format_pr(payload)
    elif event == "fork":
        text = format_fork(payload)
    elif event == "star" or event == "watch":
        text = format_star(payload)
    elif event == "release":
        text = format_release(payload)
    elif event == "ping":
        text = format_ping(payload)
    else:
        text = format_generic(event, payload)

    if text:
        await send_message(dest_id, text, parse_mode="html", link_preview=False)
