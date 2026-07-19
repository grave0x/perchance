"""Authentication management — stubbed (no public perchance auth API)."""

from __future__ import annotations

from perchance_toolkit.models.user import AccountStatus, User


class AuthManager:
    """Perchance.org has no public authentication API.

    All users are treated as anonymous. This class is kept for interface
    compatibility with CLI/TUI/GUI consumers.
    """

    _user: User = User(status=AccountStatus.anonymous)

    @property
    def current_user(self) -> User:
        return self._user

    @property
    def is_authenticated(self) -> bool:
        return False

    async def login(self, username: str, password: str) -> User:
        """Always raises — not supported."""
        msg = "perchance.org has no public auth API. Authentication is not available."
        raise NotImplementedError(msg)

    async def logout(self) -> None:
        self._user = User(status=AccountStatus.anonymous)

    async def validate_session(self, token: str) -> bool:
        return False
