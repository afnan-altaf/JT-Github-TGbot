from __future__ import annotations

from datetime import datetime
from typing import Optional, List

import motor.motor_asyncio

import config
from database.models import Account, LinkedRepo, UserActivity
from helpers.logger import LOGGER


class DataStore:
    _instance: Optional[DataStore] = None

    def __init__(self):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URI)
        self._db = self._client[config.DB_NAME]
        self._accounts = self._db["accounts"]
        self._repos = self._db["repos"]
        self._users = self._db["users"]
        self._bans = self._db["bans"]
        self._sudo = self._db["sudo"]

    @classmethod
    def get(cls) -> DataStore:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def setup(self):
        await self._accounts.create_index("user_id", unique=True)
        await self._repos.create_index([("chat_id", 1), ("name", 1)], unique=True)
        await self._users.create_index("user_id", unique=True)
        await self._bans.create_index("user_id", unique=True)
        LOGGER.info("DataStore indexes created.")

    async def get_account(self, user_id: int) -> Optional[Account]:
        doc = await self._accounts.find_one({"user_id": user_id})
        if not doc:
            return None
        return Account(
            user_id=doc["user_id"],
            token_enc=doc.get("token_enc"),
            gh_login=doc.get("gh_login"),
        )

    async def save_account(self, account: Account):
        await self._accounts.update_one(
            {"user_id": account.user_id},
            {"$set": {
                "user_id": account.user_id,
                "token_enc": account.token_enc,
                "gh_login": account.gh_login,
            }},
            upsert=True,
        )

    async def clear_token(self, user_id: int):
        await self._accounts.update_one(
            {"user_id": user_id},
            {"$unset": {"token_enc": "", "gh_login": ""}},
        )

    async def add_repo(self, chat_id: int, repo: LinkedRepo):
        await self._repos.update_one(
            {"chat_id": chat_id, "name": repo.name},
            {"$set": {
                "chat_id": chat_id,
                "name": repo.name,
                "hook_id": repo.hook_id,
                "peer_id": repo.peer_id,
                "events": repo.events,
            }},
            upsert=True,
        )

    async def get_repo(self, chat_id: int, name: str) -> Optional[LinkedRepo]:
        doc = await self._repos.find_one({"chat_id": chat_id, "name": name})
        if not doc:
            return None
        return LinkedRepo(
            name=doc["name"],
            hook_id=doc["hook_id"],
            peer_id=doc.get("peer_id"),
            events=doc.get("events", []),
        )

    async def list_repos(self, chat_id: int) -> List[LinkedRepo]:
        cursor = self._repos.find({"chat_id": chat_id})
        docs = await cursor.to_list(length=None)
        return [
            LinkedRepo(
                name=d["name"],
                hook_id=d["hook_id"],
                peer_id=d.get("peer_id"),
                events=d.get("events", []),
            )
            for d in docs
        ]

    async def remove_repo(self, chat_id: int, name: str):
        await self._repos.delete_one({"chat_id": chat_id, "name": name})

    async def update_repo(self, chat_id: int, name: str, **fields):
        await self._repos.update_one(
            {"chat_id": chat_id, "name": name},
            {"$set": fields},
        )

    async def track_user(self, user_id: int, is_group: bool = False):
        await self._users.update_one(
            {"user_id": user_id},
            {"$set": {"last_activity": datetime.utcnow(), "is_group": is_group},
             "$inc": {"command_count": 1}},
            upsert=True,
        )

    async def count_users(self, query: dict = None) -> int:
        return await self._users.count_documents(query or {})

    async def top_users(self, limit: int = 50) -> list:
        cursor = self._users.find(
            {"is_group": False},
            sort=[("command_count", -1)],
            limit=limit,
        )
        return await cursor.to_list(length=limit)

    async def is_banned(self, user_id: int) -> bool:
        return bool(await self._bans.find_one({"user_id": user_id}))

    async def ban_user(self, user_id: int):
        await self._bans.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id}},
            upsert=True,
        )

    async def unban_user(self, user_id: int):
        await self._bans.delete_one({"user_id": user_id})

    async def get_banned(self) -> list:
        cursor = self._bans.find({})
        return await cursor.to_list(length=None)

    async def add_sudo(self, user_id: int):
        await self._sudo.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id}},
            upsert=True,
        )

    async def remove_sudo(self, user_id: int):
        await self._sudo.delete_one({"user_id": user_id})

    async def get_sudo_ids(self) -> list:
        cursor = self._sudo.find({})
        docs = await cursor.to_list(length=None)
        return [d["user_id"] for d in docs]

    async def set_restart_pending(self, chat_id: int, msg_id: int):
        await self._db["meta"].update_one(
            {"key": "pending_restart"},
            {"$set": {"chat_id": chat_id, "msg_id": msg_id}},
            upsert=True,
        )

    async def get_restart_pending(self) -> Optional[dict]:
        return await self._db["meta"].find_one({"key": "pending_restart"})

    async def clear_restart_pending(self):
        await self._db["meta"].delete_one({"key": "pending_restart"})
