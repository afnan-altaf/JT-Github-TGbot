<div align="center">

<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="120" height="120"/>

# JT-Github-TGbot — Telegram GitHub Automation Bot

**A powerful GitHub integration bot for Telegram with real-time webhooks, secure token vault, and automation system.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Telethon](https://img.shields.io/badge/Telethon-Latest-blue)](https://github.com/LonamiWebs/Telethon)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-green?logo=mongodb)](https://mongodb.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

</div>

---

## Features

- Connect multiple GitHub accounts securely
- AES-encrypted **token vault system**
- Real-time GitHub webhook integration
- Repository linking and management
- Live notifications for:
  - Push events
  - Pull requests
  - Issues
  - Releases
  - Forks, Stars, and more
- Modular plugin-based architecture
- FastAPI-powered webhook server
- MongoDB async database (Motor)
- Clean inline button UI system
- Dynamic module auto-loader
- Secure storage for sensitive credentials

---

## Requirements

- Python **3.10+**
- MongoDB database
- Telegram API credentials from https://my.telegram.org
- GitHub OAuth App credentials

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file based on `sample.env`:

```env
API_ID=123456
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
MONGO_URI=mongodb://localhost:27017
DB_NAME=JTGithubBot
GH_CLIENT_ID=your_github_oauth_client_id
GH_CLIENT_SECRET=your_github_oauth_client_secret
HOOK_SECRET=your_random_webhook_secret
PUBLIC_URL=https://yourdomain.com
CIPHER_KEY=your_base64_32byte_aes_key
HOOK_PORT=8080
UPDATES_URL=t.me/your_channel
ADMIN_ID=your_telegram_user_id
```

> **Important:** Never expose secrets in public repositories.

---

## Running

```bash
python main.py
```

Or with Docker:

```bash
docker-compose up -d
```

---

## Commands

| Command | Description |
|---|---|
| /start | Start the bot |
| /help | Show help menu |
| /connect | Link your GitHub account |
| /logout | Remove GitHub account |
| /repos | List linked repositories |
| /addrepo | Link a repository |
| /removerepo | Unlink a repository |
| /settings | Configure repo settings |
| /create | Create a new GitHub repo |
| /approve | Approve a PR (reply to notification) |
| /close | Close an issue or PR |
| /reopen | Reopen an issue or PR |
| /del | Delete a GitHub repository |
| /setdescription | Update repo description |
| /sethandle | Rename a repository |
| /stats | Bot usage statistics (admin) |
| /ban | Ban a user (admin) |
| /unban | Unban a user (admin) |
| /logs | Download log file (admin) |
| /restart | Restart the bot (admin) |

---

## Project Structure

```
JT-Github-TGbot/
├── main.py                # Entry point & module loader
├── config.py             # Configuration (use .env in production)
├── bot.py                # Telegram client setup
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose config
├── cache/
│   └── ttlcache.py       # TTL in-memory cache
├── core/
│   └── start.py          # /start handler
├── modules/              # Command handlers
│   ├── actions.py        # /approve, /close, /reopen
│   ├── admins.py         # Admin utilities
│   ├── callbacks.py      # Inline button callbacks
│   ├── callbacks_repo.py # Repo config callbacks
│   ├── connect.py        # /connect, /logout
│   ├── create.py         # /create
│   ├── help.py           # /help
│   ├── logs.py           # /logs
│   ├── middleware.py     # Activity tracking
│   ├── reload.py         # /reload
│   ├── repomanage.py     # /del, /setdescription, /sethandle
│   ├── repos.py          # /addrepo, /removerepo, /repos
│   ├── restart.py        # /restart
│   ├── settings.py       # /settings
│   ├── stats.py          # /stats
│   └── sudo.py           # /ban, /unban, /auth
├── ghub/
│   ├── events.py         # Supported GitHub event types
│   ├── genbtn.py         # Button builders
│   ├── ghclient.py       # GitHub API client
│   ├── hookserver.py     # FastAPI webhook server
│   ├── markup.py         # Notification message formatters
│   ├── middleware.py     # Tracking middleware
│   ├── oauth.py          # GitHub OAuth helpers
│   └── payloads.py       # Webhook payload dispatcher
├── helpers/
│   ├── botutils.py       # send_message, edit_message utilities
│   ├── buttons.py        # SmartButtons builder
│   ├── donate.py         # Donation text
│   ├── guard.py          # Ban check decorator
│   ├── logger.py         # Logging setup
│   └── utils.py          # Utility functions
├── crypto/
│   └── vault.py          # AES-256-GCM encryption
└── database/
    ├── models.py         # Data models
    └── store.py          # MongoDB data store
```

---

## Security

- Tokens encrypted with **AES-256-GCM** before storage
- Webhook signatures verified with **HMAC-SHA256**
- Webhook token uses encrypted chat ID

---

## License

MIT License

**Copyright © 2025 JT. All rights reserved.**

---

<div align="center">Made with by JT</div>
