from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Account:
    user_id: int
    token_enc: Optional[str] = None
    gh_login: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LinkedRepo:
    name: str
    hook_id: int
    peer_id: Optional[int] = None
    events: List[str] = field(default_factory=list)


@dataclass
class UserActivity:
    user_id: int
    is_group: bool = False
    last_activity: datetime = field(default_factory=datetime.utcnow)
    command_count: int = 0
