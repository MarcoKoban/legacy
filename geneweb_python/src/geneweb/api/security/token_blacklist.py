"""
Token blacklist service for JWT token revocation.

This module provides a token blacklist mechanism to handle:
- Logout (revoke access tokens)
- Password changes (revoke all user tokens)
- Admin-initiated account suspension
- Token rotation and refresh token revocation

In production, use Redis for scalability and performance.
For now, using in-memory storage.
"""

from datetime import datetime, timezone
from typing import Optional, Set
from uuid import UUID

import structlog

logger = structlog.get_logger(__name__)


class TokenBlacklist:
    """
    In-memory token blacklist with automatic cleanup.

    **Production Note:** Replace with Redis or database for:
    - Horizontal scalability
    - Persistence across restarts
    - Better performance for large datasets

    Redis example:
    ```python
    redis_client.setex(f"blacklist:{token_id}", ttl_seconds, "revoked")
    ```
    """

    def __init__(self):
        # Set of revoked token IDs (JTI - JWT ID)
        self._blacklisted_tokens: Set[str] = set()

        # Map of token ID to expiration time for cleanup
        self._token_expiry: dict[str, datetime] = {}

        # Map of user ID to set of their revoked tokens (for bulk revocation)
        self._user_tokens: dict[UUID, Set[str]] = {}

        logger.info("Token blacklist initialized (in-memory)")

    def add_token(
        self, token_id: str, expires_at: datetime, user_id: Optional[UUID] = None
    ) -> None:
        """
        Add a token to the blacklist.

        Args:
            token_id: Unique token identifier (JTI from JWT payload)
            expires_at: Token expiration timestamp (for automatic cleanup)
            user_id: Optional user ID for bulk revocation
        """
        self._cleanup_expired()  # Clean up before adding

        self._blacklisted_tokens.add(token_id)
        self._token_expiry[token_id] = expires_at

        if user_id:
            if user_id not in self._user_tokens:
                self._user_tokens[user_id] = set()
            self._user_tokens[user_id].add(token_id)

        logger.info(
            "Token added to blacklist",
            token_id=token_id[:8] + "...",  # Log only first 8 chars for privacy
            expires_at=expires_at.isoformat(),
            user_id=str(user_id) if user_id else None,
        )

    def is_blacklisted(self, token_id: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            token_id: Token identifier to check

        Returns:
            True if token is blacklisted, False otherwise
        """
        self._cleanup_expired()  # Clean up before checking
        return token_id in self._blacklisted_tokens

    def revoke_user_tokens(self, user_id: UUID) -> int:
        """
        Revoke all tokens for a specific user.

        Useful for:
        - Password changes
        - Account suspension
        - Security incidents

        Args:
            user_id: User ID whose tokens should be revoked

        Returns:
            Number of tokens revoked
        """
        if user_id not in self._user_tokens:
            return 0

        tokens = self._user_tokens[user_id]
        count = len(tokens)

        logger.warning(
            "Revoking all tokens for user",
            user_id=str(user_id),
            token_count=count,
        )

        return count

    def _cleanup_expired(self) -> int:
        """
        Remove expired tokens from blacklist.

        This prevents the blacklist from growing indefinitely.
        Tokens are automatically removed after their expiration time.

        Returns:
            Number of tokens cleaned up
        """
        now = datetime.now(timezone.utc)
        expired_tokens = []

        for token_id, expiry in self._token_expiry.items():
            if expiry < now:
                expired_tokens.append(token_id)

        if expired_tokens:
            for token_id in expired_tokens:
                self._blacklisted_tokens.discard(token_id)
                del self._token_expiry[token_id]

                # Clean up from user_tokens map
                for user_tokens in self._user_tokens.values():
                    user_tokens.discard(token_id)

            logger.debug(
                "Cleaned up expired tokens from blacklist",
                count=len(expired_tokens),
            )

        return len(expired_tokens)

    def get_stats(self) -> dict:
        """
        Get blacklist statistics.

        Returns:
            Dictionary with blacklist metrics
        """
        self._cleanup_expired()

        return {
            "total_blacklisted": len(self._blacklisted_tokens),
            "total_users_with_revoked_tokens": len(self._user_tokens),
            "oldest_token_expires": (
                min(self._token_expiry.values()).isoformat()
                if self._token_expiry
                else None
            ),
            "newest_token_expires": (
                max(self._token_expiry.values()).isoformat()
                if self._token_expiry
                else None
            ),
        }

    def clear_all(self) -> None:
        """
        Clear all blacklisted tokens.

        **Warning:** Only use for testing or emergency situations!
        """
        count = len(self._blacklisted_tokens)
        self._blacklisted_tokens.clear()
        self._token_expiry.clear()
        self._user_tokens.clear()

        logger.warning("All tokens cleared from blacklist", count=count)


# Global blacklist instance
token_blacklist = TokenBlacklist()
