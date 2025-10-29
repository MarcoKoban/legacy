"""
Database models for user authentication and management.

This module provides SQLAlchemy models for:
- User accounts with secure password storage
- User sessions and tokens
- Login attempts and security events
- Password history for preventing reuse
"""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from ..security.auth import UserRole

Base = declarative_base()


class UserModel(Base):
    """
    User account model with security features.

    **Security Features:**
    - Bcrypt hashed passwords
    - Account lockout after failed attempts
    - Password change tracking
    - GDPR consent tracking
    """

    __tablename__ = "users"

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)

    # Authentication
    hashed_password = Column(String(255), nullable=False)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)

    # User information
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Security
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # Family relationships (for genealogy access control)
    family_person_id = Column(UUID(as_uuid=True), nullable=True)

    # GDPR compliance
    gdpr_consent_given = Column(Boolean, default=False, nullable=False)
    gdpr_consent_date = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    password_history = relationship(
        "PasswordHistoryModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions = relationship(
        "UserSessionModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    login_attempts = relationship(
        "LoginAttemptModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class PasswordHistoryModel(Base):
    """
    Password history for preventing password reuse.

    Stores hashed passwords to prevent users from reusing
    recent passwords (security best practice).
    """

    __tablename__ = "password_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    hashed_password = Column(String(255), nullable=False)
    changed_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("UserModel", back_populates="password_history")

    def __repr__(self):
        return (
            f"<PasswordHistory(user_id={self.user_id}, changed_at={self.changed_at})>"
        )


class UserSessionModel(Base):
    """
    Active user sessions for token management.

    Tracks active refresh tokens and allows for:
    - Session revocation
    - Device management
    - Suspicious activity detection
    """

    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    # Token information
    refresh_token_jti = Column(String(255), unique=True, nullable=False, index=True)
    access_token_jti = Column(String(255), nullable=True, index=True)

    # Session context
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(Text, nullable=True)
    device_info = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_used_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoke_reason = Column(String(255), nullable=True)

    # Relationships
    user = relationship("UserModel", back_populates="sessions")

    def __repr__(self):
        string = f"<UserSession(id={self.id}, user_id={self.user_id}, "
        f"active={self.is_active})>"
        return string


class LoginAttemptModel(Base):
    """
    Login attempt tracking for security monitoring.

    Tracks all login attempts (successful and failed) for:
    - Brute force detection
    - Account lockout
    - Security auditing
    - Suspicious activity alerts
    """

    __tablename__ = "login_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    username = Column(String(50), nullable=False, index=True)

    # Attempt information
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(255), nullable=True)

    # Request context
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)

    # Timestamp
    attempted_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    user = relationship("UserModel", back_populates="login_attempts")

    def __repr__(self):
        string = f"<LoginAttempt(username='{self.username}', "
        f"success={self.success}, at={self.attempted_at})>"
        return string


class BlacklistedTokenModel(Base):
    """
    Blacklisted (revoked) tokens for logout and security.

    Stores revoked tokens until their expiration time.
    Tokens in this table cannot be used for authentication.
    """

    __tablename__ = "blacklisted_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    token_jti = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Token information
    token_type = Column(String(20), nullable=False)  # 'access' or 'refresh'
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Revocation details
    revoked_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    revoke_reason = Column(String(255), nullable=True)

    def __repr__(self):
        string = f"<BlacklistedToken(jti={self.token_jti[:8]}..., "
        f"expires={self.expires_at})>"
        return string
