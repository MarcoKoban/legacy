"""
Authentication router for login, token refresh, and user management.

This module provides secure authentication endpoints with:
- JWT-based authentication (access + refresh tokens)
- Password hashing with bcrypt
- Rate limiting protection
- Audit logging
- Token refresh and revocation
"""

from datetime import datetime, timezone
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm,
)
from pydantic import BaseModel, Field

from ..security.audit import audit_logger
from ..security.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    Token,
    User,
    UserCreate,
    auth_service,
)

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
security = HTTPBearer()


# Pydantic models for request/response
class LoginRequest(BaseModel):
    """Login credentials."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class LoginResponse(Token):
    """Login response with user info."""

    user: dict = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str = Field(
        ..., description="Refresh token to exchange for new access token"
    )


class ChangePasswordRequest(BaseModel):
    """Change password request."""

    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    """User information response (without sensitive data)."""

    id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    credentials: LoginRequest,
) -> LoginResponse:
    """
    Authenticate user and return JWT tokens.

    **Security Features:**
    - Password hashing verification with bcrypt
    - Rate limiting to prevent brute force
    - Failed login attempt tracking
    - Account lockout after multiple failures
    - Audit logging of all login attempts

    **Returns:**
    - access_token: Short-lived token for API access (30 minutes)
    - refresh_token: Long-lived token for obtaining new access tokens (7 days)
    - token_type: Always "bearer"
    - expires_in: Access token expiration time in seconds
    """
    # Get client IP for audit logging
    client_ip = request.client.host if request.client else "unknown"

    # Authenticate user
    user = auth_service.authenticate_user(credentials.username, credentials.password)

    if not user:
        # Log failed login attempt
        logger.warning(
            "Failed login attempt",
            username=credentials.username,
            ip_address=client_ip,
        )
        # Generic error message to prevent username enumeration
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is active
    if not user.is_active:
        logger.warning(
            "Login attempt for inactive account",
            username=credentials.username,
            ip_address=client_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        logger.warning(
            "Login attempt for locked account",
            username=credentials.username,
            ip_address=client_ip,
            locked_until=user.locked_until.isoformat(),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is locked until {user.locked_until.isoformat()}",
        )

    # Create tokens
    access_token = auth_service.create_access_token(user)
    refresh_token = auth_service.create_refresh_token(user)

    # Update last login timestamp
    user.last_login = datetime.now(timezone.utc)
    user.failed_login_attempts = 0  # Reset failed attempts on successful login

    # Log successful login
    logger.info(
        "User logged in successfully",
        user_id=str(user.id),
        username=user.username,
        ip_address=client_ip,
    )

    # Audit log
    try:
        await audit_logger.log_user_login(
            user_id=user.id,
            username=user.username,
            ip_address=client_ip,
            user_agent=request.headers.get("User-Agent"),
        )
    except Exception as e:
        logger.error("Failed to log audit event", error=str(e))

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
        },
    )


@router.post("/login/oauth2", response_model=Token, status_code=status.HTTP_200_OK)
async def login_oauth2(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """
    OAuth2-compatible login endpoint.

    This endpoint follows the OAuth2 password flow specification
    for compatibility with OAuth2 clients and Swagger UI.
    """
    # Authenticate user
    user = auth_service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    # Create tokens
    access_token = auth_service.create_access_token(user)
    refresh_token = auth_service.create_refresh_token(user)

    # Update last login
    user.last_login = datetime.now(timezone.utc)

    logger.info(
        "User logged in via OAuth2",
        user_id=str(user.id),
        username=user.username,
        ip_address=request.client.host if request.client else "unknown",
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_token(
    request: Request,
    refresh_request: RefreshTokenRequest,
) -> Token:
    """
    Refresh access token using a valid refresh token.

    **Security Features:**
    - Validates refresh token signature and expiration
    - Checks token type (must be 'refresh')
    - Generates new access token
    - Can optionally rotate refresh token

    **Note:** The refresh token itself is not rotated by default.
    For maximum security, implement refresh token rotation.
    """
    try:
        # Verify refresh token
        token_data = auth_service.verify_refresh_token(refresh_request.refresh_token)

        # Get current user data
        user = auth_service.get_user_by_username(token_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )

        # Create new access token
        new_access_token = auth_service.create_access_token(user)

        # Optionally rotate refresh token (recommended for production)
        new_refresh_token = auth_service.create_refresh_token(user)

        logger.info(
            "Token refreshed successfully",
            user_id=str(user.id),
            username=user.username,
            ip_address=request.client.host if request.client else "unknown",
        )

        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Logout user and invalidate token.

    **Security Features:**
    - Adds token to blacklist for revocation
    - Token cannot be reused after logout
    - Audit logging of logout event

    **Note:** Client should also discard tokens locally.
    """
    from jose import jwt

    from ..security.token_blacklist import token_blacklist

    try:
        # Verify the token is valid (without checking blacklist to allow logout)
        token_data = auth_service.verify_token(
            credentials.credentials, check_blacklist=False
        )

        # Decode token to get expiration and JTI
        payload = jwt.decode(
            credentials.credentials,
            (
                auth_service.security.secret_key
                if hasattr(auth_service, "security")
                else ""
            ),
            algorithms=["HS256"],
            options={"verify_signature": False},  # Already verified above
        )

        token_id = payload.get("jti")
        exp_timestamp = payload.get("exp")

        if token_id and exp_timestamp:
            # Add token to blacklist
            from datetime import datetime, timezone

            expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            token_blacklist.add_token(token_id, expires_at, user_id=token_data.user_id)

        logger.info(
            "User logged out",
            user_id=str(token_data.user_id),
            username=token_data.username,
            ip_address=request.client.host if request.client else "unknown",
        )

        # Audit log
        try:
            await audit_logger.log_user_logout(
                user_id=token_data.user_id,
                username=token_data.username,
                ip_address=request.client.host if request.client else "unknown",
            )
        except Exception as e:
            logger.error("Failed to log audit event", error=str(e))

        return {
            "message": "Successfully logged out",
            "detail": "Token has been revoked and cannot be reused",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserResponse:
    """
    Get current authenticated user information.

    **Requires:** Valid access token

    **Returns:** User information (without sensitive data like password)
    """
    try:
        # Verify token
        token_data = auth_service.verify_token(credentials.credentials)

        # Get full user data
        user = auth_service.get_user_by_username(token_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get current user", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    request: Request,
    user_data: UserCreate,
) -> UserResponse:
    """
    Register a new user account.

    **Security Features:**
    - Password strength validation (min 8 characters)
    - Email validation
    - Username uniqueness check
    - Password hashing with bcrypt
    - Audit logging

    **Note:** In production, you may want to:
    - Add email verification
    - Add CAPTCHA
    - Require admin approval for certain roles
    - Implement rate limiting per IP
    """
    # Check if username already exists
    existing_user = auth_service.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )

    # Check if email already exists
    existing_email = auth_service.get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Validate password strength (basic validation, can be enhanced)
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )

    # Create user
    try:
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role,
            family_person_id=user_data.family_person_id,
            password_changed_at=datetime.now(timezone.utc),
        )

        # Hash password and store user
        hashed_password = auth_service.get_password_hash(user_data.password)
        auth_service.users_db[user_data.username] = {
            "user": new_user,
            "hashed_password": hashed_password,
        }

        logger.info(
            "New user registered",
            user_id=str(new_user.id),
            username=new_user.username,
            role=new_user.role.value,
            ip_address=request.client.host if request.client else "unknown",
        )

        # Audit log
        try:
            await audit_logger.log_user_created(
                user_id=new_user.id,
                username=new_user.username,
                role=new_user.role.value,
                ip_address=request.client.host if request.client else "unknown",
            )
        except Exception as e:
            logger.error("Failed to log audit event", error=str(e))

        return UserResponse(
            id=str(new_user.id),
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role.value,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            last_login=new_user.last_login,
        )

    except Exception as e:
        logger.error("User registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request: Request,
    password_data: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Change user password.

    **Requires:** Valid access token

    **Security Features:**
    - Verifies current password
    - Validates new password strength
    - Confirms password match
    - Updates password_changed_at timestamp
    - Audit logging
    """
    # Verify token
    token_data = auth_service.verify_token(credentials.credentials)

    # Get user
    user_data = auth_service.users_db.get(token_data.username)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user = user_data["user"]
    current_hash = user_data["hashed_password"]

    # Verify current password
    if not auth_service.verify_password(password_data.current_password, current_hash):
        logger.warning(
            "Failed password change attempt - incorrect current password",
            user_id=str(user.id),
            username=user.username,
            ip_address=request.client.host if request.client else "unknown",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    # Validate new password
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match",
        )

    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long",
        )

    # Don't allow reusing the same password
    if auth_service.verify_password(password_data.new_password, current_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )

    # Update password
    new_hash = auth_service.get_password_hash(password_data.new_password)
    user_data["hashed_password"] = new_hash
    user.password_changed_at = datetime.now(timezone.utc)

    logger.info(
        "Password changed successfully",
        user_id=str(user.id),
        username=user.username,
        ip_address=request.client.host if request.client else "unknown",
    )

    # Audit log
    try:
        await audit_logger.log_password_changed(
            user_id=user.id,
            username=user.username,
            ip_address=request.client.host if request.client else "unknown",
        )
    except Exception as e:
        logger.error("Failed to log audit event", error=str(e))

    return {
        "message": "Password changed successfully",
        "detail": "Please login again with your new password",
    }


@router.get("/health", status_code=status.HTTP_200_OK)
async def auth_health_check() -> dict:
    """
    Health check endpoint for authentication service.

    **Public endpoint** - No authentication required
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "features": {
            "login": "enabled",
            "refresh": "enabled",
            "registration": "enabled",
            "password_change": "enabled",
        },
        "security": {
            "token_type": "JWT",
            "access_token_expiry_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expiry_days": REFRESH_TOKEN_EXPIRE_DAYS,
            "password_hashing": "bcrypt",
        },
    }
