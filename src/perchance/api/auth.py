"""Authentication management for perchance.org."""

from __future__ import annotations

from typing import Optional

import httpx

from perchance.models.user import AccountStatus, User


class AuthManager:
    """Handles login, session persistence, and token refresh."""

    AUTH_URL = "https://perchance.org/api/auth"

    def __init__(self) -> None:
        self._user: Optional[User] = None

    @property
    def current_user(self) -> User:
        return self._user or User(status=AccountStatus.anonymous)

    @property
    def is_authenticated(self) -> bool:
        return self._user is not None and self._user.status == AccountStatus.logged_in

    async def login(self, username: str, password: str) -> User:
        """Authenticate with username/password, returns User with session token."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.AUTH_URL}/login",
                json={"username": username, "password": password},
            )
            resp.raise_for_status()
            data = resp.json()
            self._user = User(
                username=data["username"],
                display_name=data.get("display_name"),
                avatar_url=data.get("avatar_url"),
                status=AccountStatus.logged_in,
                session_token=data["token"],
            )
            return self._user

    async def logout(self) -> None:
        """Clear session and invalidate token on server."""
        if self._user and self._user.session_token:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.AUTH_URL}/logout",
                    headers={"Authorization": f"Bearer {self._user.session_token}"},
                )
        self._user = None

    async def validate_session(self, token: str) -> bool:
        """Check if a stored session token is still valid."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.AUTH_URL}/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            return resp.status_code == 200
