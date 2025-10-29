"""
Role-Based Access Control (RBAC) system for Geneweb API.
"""

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import UUID, uuid4

import structlog
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field

from ..config import settings

# Configure bcrypt to handle long passwords before importing passlib
# This prevents errors during passlib's backend initialization
try:
    import bcrypt

    # Fix bcrypt version detection for newer versions
    if not hasattr(bcrypt, "__about__"):
        # Create a mock __about__ module to prevent passlib warnings
        class _About:
            __version__ = (
                bcrypt.__version__ if hasattr(bcrypt, "__version__") else "4.0.0"
            )

        bcrypt.__about__ = _About()

    # Monkey-patch bcrypt.hashpw to truncate passwords
    _original_hashpw = bcrypt.hashpw
    _original_checkpw = bcrypt.checkpw

    def _safe_hashpw(password, salt):
        """Wrap bcrypt.hashpw to truncate passwords to 72 bytes."""
        if isinstance(password, str):
            password = password.encode("utf-8")
        if len(password) > 72:
            password = password[:72]
        return _original_hashpw(password, salt)

    def _safe_checkpw(password, hashed_password):
        """Wrap bcrypt.checkpw to truncate passwords to 72 bytes."""
        if isinstance(password, str):
            password = password.encode("utf-8")
        if len(password) > 72:
            password = password[:72]
        return _original_checkpw(password, hashed_password)

    bcrypt.hashpw = _safe_hashpw
    bcrypt.checkpw = _safe_checkpw
except ImportError:
    pass  # bcrypt not available, passlib will handle it

from passlib.context import CryptContext

logger = structlog.get_logger(__name__)


# Password hashing context
# Note: bcrypt is monkey-patched above to handle passwords > 72 bytes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


class UserRole(str, Enum):
    """User roles - simplified to USER and ADMIN."""

    USER = "user"  # Regular authenticated user - has full access
    ADMIN = "admin"  # Administrator - has full access including user management


class Permission(str, Enum):
    """Granular permissions."""

    # Person permissions
    VIEW_PUBLIC_PERSONS = "view_public_persons"
    VIEW_FAMILY_PERSONS = "view_family_persons"
    VIEW_ALL_PERSONS = "view_all_persons"
    CREATE_PERSON = "create_person"
    UPDATE_OWN_PERSON = "update_own_person"
    UPDATE_FAMILY_PERSON = "update_family_person"
    UPDATE_ANY_PERSON = "update_any_person"
    DELETE_PERSON = "delete_person"

    # GDPR permissions
    EXPORT_PERSON_DATA = "export_person_data"
    ANONYMIZE_PERSON = "anonymize_person"
    MANAGE_CONSENT = "manage_consent"

    # System permissions
    VIEW_AUDIT_LOG = "view_audit_log"
    MANAGE_USERS = "manage_users"
    SYSTEM_ADMIN = "system_admin"


# Role-permission mapping
# Simplified: Both USER and ADMIN have all permissions
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.USER: {
        # All permissions for regular users
        *Permission.__members__.values()
    },
    UserRole.ADMIN: {
        # All permissions for admins
        *Permission.__members__.values()
    },
}


class User(BaseModel):
    """User model for authentication."""

    id: UUID = Field(default_factory=uuid4)
    email: str
    username: str
    full_name: str
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None

    # Family relationship (for FAMILY role)
    family_person_id: Optional[UUID] = None
    related_person_ids: Set[UUID] = Field(default_factory=set)

    # Security
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None

    # GDPR
    gdpr_consent_given: bool = Field(default=False)
    gdpr_consent_date: Optional[datetime] = None


class UserCreate(BaseModel):
    """Model for creating a new user."""

    email: str
    username: str
    full_name: str
    password: str = Field(..., min_length=8)
    role: UserRole = Field(default=UserRole.USER)
    family_person_id: Optional[UUID] = None


class UserInDB(User):
    """User model with hashed password."""

    hashed_password: str


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data."""

    user_id: UUID
    username: str
    role: UserRole
    permissions: List[Permission]
    family_person_id: Optional[UUID] = None
    related_person_ids: Set[UUID] = Field(default_factory=set)


class AuthService:
    """Authentication service for user management."""

    def __init__(self):
        self.security = HTTPBearer()
        # In-memory user database (in production, use real database)
        self.users_db: Dict[str, Dict] = {}
        self._initialize_default_users()

    def _initialize_default_users(self):
        """Initialize default admin and demo users."""
        # Create default admin user
        admin_user = User(
            username="admin",
            email="admin@geneweb.local",
            full_name="Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        self.users_db["admin"] = {
            "user": admin_user,
            "hashed_password": self.get_password_hash(
                "admin123"
            ),  # Change in production!
        }

        # Create demo family user
        demo_user = User(
            username="demo",
            email="demo@geneweb.local",
            full_name="Demo User",
            role=UserRole.USER,
            is_active=True,
        )
        self.users_db["demo"] = {
            "user": demo_user,
            "hashed_password": self.get_password_hash(
                "demo1234"
            ),  # Changed to meet 8-char minimum
        }

        logger.info("Default users initialized", users=list(self.users_db.keys()))

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def create_access_token(self, user: User) -> str:
        """Create JWT access token with JTI for revocation support."""
        permissions = list(ROLE_PERMISSIONS.get(user.role, set()))

        # Generate unique token ID for blacklist tracking
        token_id = str(uuid4())

        payload = {
            "jti": token_id,  # JWT ID for blacklist
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value,
            "permissions": [p.value for p in permissions],
            "family_person_id": (
                str(user.family_person_id) if user.family_person_id else None
            ),
            "related_person_ids": [str(pid) for pid in user.related_person_ids],
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }

        return jwt.encode(payload, settings.security.secret_key, algorithm=ALGORITHM)

    def create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token with JTI for revocation support."""
        # Generate unique token ID for blacklist tracking
        token_id = str(uuid4())

        payload = {
            "jti": token_id,  # JWT ID for blacklist
            "sub": str(user.id),
            "username": user.username,
            "exp": datetime.now(timezone.utc)
            + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }

        return jwt.encode(payload, settings.security.secret_key, algorithm=ALGORITHM)

    def verify_token(self, token: str, check_blacklist: bool = True) -> TokenData:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token string
            check_blacklist: Whether to check if token is blacklisted (default: True)

        Returns:
            TokenData with user information and permissions

        Raises:
            HTTPException: If token is invalid, expired, or blacklisted
        """
        try:
            payload = jwt.decode(
                token, settings.security.secret_key, algorithms=[ALGORITHM]
            )

            user_id = payload.get("sub")
            username = payload.get("username")
            role = payload.get("role")
            permissions = payload.get("permissions", [])
            token_type = payload.get("type", "access")
            token_id = payload.get("jti")

            if user_id is None or username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )

            if token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )

            # Check if token is blacklisted (revoked)
            if check_blacklist and token_id:
                from .token_blacklist import token_blacklist

                if token_blacklist.is_blacklisted(token_id):
                    logger.warning(
                        "Attempt to use blacklisted token",
                        token_id=token_id[:8] + "...",
                        username=username,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has been revoked",
                    )

            # Convert strings back to proper types
            family_person_id = None
            if payload.get("family_person_id"):
                family_person_id = UUID(payload["family_person_id"])

            related_person_ids = set()
            if payload.get("related_person_ids"):
                related_person_ids = {
                    UUID(pid) for pid in payload["related_person_ids"]
                }

            return TokenData(
                user_id=UUID(user_id),
                username=username,
                role=UserRole(role),
                permissions=[Permission(p) for p in permissions],
                family_person_id=family_person_id,
                related_person_ids=related_person_ids,
            )

        except JWTError as e:
            logger.warning("JWT verification failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    def verify_refresh_token(self, token: str) -> TokenData:
        """Verify and decode refresh JWT token."""
        try:
            payload = jwt.decode(
                token, settings.security.secret_key, algorithms=[ALGORITHM]
            )

            user_id = payload.get("sub")
            username = payload.get("username")
            token_type = payload.get("type", "access")

            if user_id is None or username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )

            if token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )

            # For refresh tokens, we only need user_id and username
            # Other fields will be populated when creating the new access token
            return TokenData(
                user_id=UUID(user_id),
                username=username,
                role=UserRole.USER,  # Placeholder, will be replaced
                permissions=[],  # Placeholder, will be replaced
                family_person_id=None,
                related_person_ids=set(),
            )

        except JWTError as e:
            logger.warning("Refresh token verification failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        user_data = self.users_db.get(username)
        if not user_data:
            return None

        if not self.verify_password(password, user_data["hashed_password"]):
            return None

        return user_data["user"]

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username from database."""
        user_data = self.users_db.get(username)
        return user_data["user"] if user_data else None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email from database."""
        for user_data in self.users_db.values():
            if user_data["user"].email == email:
                return user_data["user"]
        return None

    def has_permission(self, user_role: UserRole, permission: Permission) -> bool:
        """Check if user role has specific permission."""
        return permission in ROLE_PERMISSIONS.get(user_role, set())

    def can_access_person(
        self, user: TokenData, person_id: UUID, action: Permission
    ) -> bool:
        """Check if user can access specific person for given action."""
        # Admin can access everything
        if user.role == UserRole.ADMIN:
            return True

        # Check basic permission
        if not self.has_permission(user.role, action):
            return False

        # All users now have the same permissions, so return True
        return True


class SecurityContext:
    """Security context for request processing."""

    def __init__(
        self,
        user: TokenData,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        self.user = user
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.request_id = uuid4()
        self.timestamp = datetime.now(timezone.utc)

    def has_permission(self, permission: Permission) -> bool:
        """Check if current user has permission."""
        return permission in self.user.permissions

    def can_access_person(self, person_id: UUID, action: Permission) -> bool:
        """Check if current user can access person for action."""
        auth_service = AuthService()
        return auth_service.can_access_person(self.user, person_id, action)

    def require_permission(self, permission: Permission):
        """Require specific permission, raise exception if not granted."""
        if not self.has_permission(permission):
            logger.warning(
                "Permission denied",
                user_id=str(self.user.user_id),
                permission=permission.value,
                ip_address=self.ip_address,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' required",
            )

    def require_person_access(self, person_id: UUID, action: Permission):
        """Require access to specific person, raise exception if denied."""
        if not self.can_access_person(person_id, action):
            logger.warning(
                "Person access denied",
                user_id=str(self.user.user_id),
                person_id=str(person_id),
                action=action.value,
                ip_address=self.ip_address,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to person {person_id}",
            )

    def get_audit_context(self) -> Dict[str, Any]:
        """Get context for audit logging."""
        return {
            "user_id": str(self.user.user_id),
            "username": self.user.username,
            "role": self.user.role.value,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_id": str(self.request_id),
            "timestamp": self.timestamp.isoformat(),
        }


# Global auth service instance
auth_service = AuthService()
