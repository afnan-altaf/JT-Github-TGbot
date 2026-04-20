import re

from telethon import events

import config
from bot import Irene
from helpers import send_message, new_task
from helpers.guard import ban_check

_prefixes = "".join(re.escape(p) for p in config.COMMAND_PREFIXES)

HELP_TEXT = """<b>📖 JT GitHub Notify Bot — Commands</b>
<b>━━━━━━━━━━━━━━━━━━━━━━</b>

<b>🔗 GitHub Account</b>
/connect — Link your GitHub account via OAuth
/logout — Disconnect your GitHub account

<b>📦 Repositories</b>
/addrepo owner/repo — Link a repository (creates webhook)
/addrepo — Browse your repos interactively
/removerepo owner/repo — Unlink a repository
/repos — List all linked repositories
/settings — Configure webhook settings
/create repo-name — Create a new GitHub repository

<b>⚙️ Actions (reply to a notification)</b>
/approve — Approve a Pull Request
/close — Close an issue or PR
/reopen — Reopen an issue or PR

<b>🛠 Repo Management</b>
/del owner/repo — Delete a GitHub repository
/setdescription owner/repo text — Update description
/sethandle owner/repo newname — Rename a repository

<b>🧹 Utilities</b>
/reload — Refresh admin cache for this chat

<b>🛡 Admin Only</b>
/stats — View bot statistics
/ban user_id — Ban a user
/unban user_id — Unban a user
/banlist — View banned users
/logs — Download the log file
/restart — Restart the bot
/auth user_id — Add a sudo admin
/deauth user_id — Remove a sudo admin
"""


@Irene.on(events.NewMessage(pattern=re.compile(rf"^[{_prefixes}]help(?:\s|$)", re.IGNORECASE)))
@ban_check
@new_task
async def help_handler(event):
    await send_message(event.chat_id, HELP_TEXT, parse_mode="html")
