from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AccountStatus(str, Enum):
    anonymous = "anonymous"
    logged_in = "logged_in"
    session_expired = "session_expired"


class User(BaseModel):
    """Represents a perchance.org user (logged-in or anonymous)."""

    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    status: AccountStatus = AccountStatus.anonymous
    joined: Optional[datetime] = None
    stats: dict[str, int] = Field(default_factory=dict)
    session_token: Optional[str] = None
