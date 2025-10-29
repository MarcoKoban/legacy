"""Tests for authentication and authorization module."""

from datetime import datetime
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException, status
from jose import jwt

from geneweb.api.security.auth import (
    ALGORITHM,
    ROLE_PERMISSIONS,
    AuthService,
    Permission,
    SecurityContext,
    Token,
    TokenData,
    User,
    UserCreate,
    UserRole,
    auth_service,
    pwd_context,
)


class TestUserRole:
    """Test UserRole enum."""

    def test_user_role_values(self):
        """Test UserRole enum values."""
        assert UserRole.USER == "user"
        assert UserRole.ADMIN == "admin"


class TestPermission:
    """Test Permission enum."""

    def test_permission_values(self):
        """Test Permission enum values."""
        assert Permission.VIEW_PUBLIC_PERSONS == "view_public_persons"
        assert Permission.VIEW_FAMILY_PERSONS == "view_family_persons"
        assert Permission.CREATE_PERSON == "create_person"
        assert Permission.DELETE_PERSON == "delete_person"
        assert Permission.MANAGE_USERS == "manage_users"


class TestRolePermissions:
    """Test role-permission mappings."""

    def test_user_permissions(self):
        """Test USER role has all permissions."""
        user_perms = ROLE_PERMISSIONS[UserRole.USER]
        all_permissions = set(Permission.__members__.values())
        assert user_perms == all_permissions

    def test_admin_permissions(self):
        """Test ADMIN role has all permissions."""
        admin_perms = ROLE_PERMISSIONS[UserRole.ADMIN]
        all_permissions = set(Permission.__members__.values())
        assert admin_perms == all_permissions


class TestUserModel:
    """Test User model."""

    def test_user_creation_defaults(self):
        """Test User creation with default values."""
        user = User(
            email="test@example.com", username="testuser", full_name="Test User"
        )

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.role == UserRole.USER
        assert user.is_active is True
        assert isinstance(user.id, UUID)
        assert isinstance(user.created_at, datetime)
        assert user.last_login is None
        assert user.family_person_id is None
        assert user.related_person_ids == set()
        assert user.failed_login_attempts == 0
        assert user.locked_until is None
        assert user.gdpr_consent_given is False

    def test_user_creation_with_values(self):
        """Test User creation with specific values."""
        person_id = uuid4()
        related_ids = {uuid4(), uuid4()}

        user = User(
            email="admin@example.com",
            username="admin",
            full_name="Admin User",
            role=UserRole.ADMIN,
            family_person_id=person_id,
            related_person_ids=related_ids,
            gdpr_consent_given=True,
        )

        assert user.role == UserRole.ADMIN
        assert user.family_person_id == person_id
        assert user.related_person_ids == related_ids
        assert user.gdpr_consent_given is True


class TestUserCreate:
    """Test UserCreate model."""

    def test_user_create_validation(self):
        """Test UserCreate model validation."""
        user_create = UserCreate(
            email="new@example.com",
            username="newuser",
            full_name="New User",
            password="password123",
        )

        assert user_create.email == "new@example.com"
        assert user_create.password == "password123"
        assert user_create.role == UserRole.USER


class TestToken:
    """Test Token model."""

    def test_token_creation(self):
        """Test Token model creation."""
        token = Token(
            access_token="access_token_123",
            refresh_token="refresh_token_123",
            expires_in=1800,
        )

        assert token.access_token == "access_token_123"
        assert token.refresh_token == "refresh_token_123"
        assert token.token_type == "bearer"
        assert token.expires_in == 1800


class TestTokenData:
    """Test TokenData model."""

    def test_token_data_creation(self):
        """Test TokenData model creation."""
        user_id = uuid4()
        permissions = [Permission.VIEW_PUBLIC_PERSONS, Permission.CREATE_PERSON]

        token_data = TokenData(
            user_id=user_id,
            username="testuser",
            role=UserRole.USER,
            permissions=permissions,
        )

        assert token_data.user_id == user_id
        assert token_data.username == "testuser"
        assert token_data.role == UserRole.USER
        assert token_data.permissions == permissions


class TestAuthService:
    """Test AuthService class."""

    @pytest.fixture
    def auth_service(self):
        """Create AuthService instance for testing."""
        return AuthService()

    def test_verify_password(self, auth_service):
        """Test password verification."""
        password = "test_password_123"
        hashed = auth_service.get_password_hash(password)

        assert auth_service.verify_password(password, hashed) is True
        assert auth_service.verify_password("wrong_password", hashed) is False

    def test_get_password_hash(self, auth_service):
        """Test password hashing."""
        password = "test_password_123"
        hashed = auth_service.get_password_hash(password)

        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0

        # Verify the hash works with bcrypt
        assert pwd_context.verify(password, hashed)

    @patch("geneweb.api.security.auth.settings")
    def test_create_access_token(self, mock_settings, auth_service):
        """Test access token creation."""
        mock_settings.security.secret_key = "test_secret_key"

        user = User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            role=UserRole.USER,
        )

        token = auth_service.create_access_token(user)

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify token content
        payload = jwt.decode(token, "test_secret_key", algorithms=[ALGORITHM])
        assert payload["sub"] == str(user.id)
        assert payload["username"] == user.username
        assert payload["role"] == user.role.value
        assert payload["type"] == "access"
        assert "permissions" in payload
        assert "exp" in payload
        assert "iat" in payload

    @patch("geneweb.api.security.auth.settings")
    def test_create_refresh_token(self, mock_settings, auth_service):
        """Test refresh token creation."""
        mock_settings.security.secret_key = "test_secret_key"

        user = User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            role=UserRole.USER,
        )

        token = auth_service.create_refresh_token(user)

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify token content
        payload = jwt.decode(token, "test_secret_key", algorithms=[ALGORITHM])
        assert payload["sub"] == str(user.id)
        assert payload["username"] == user.username
        assert payload["type"] == "refresh"

    @patch("geneweb.api.security.auth.settings")
    def test_verify_token_valid(self, mock_settings, auth_service):
        """Test token verification with valid token."""
        mock_settings.security.secret_key = "test_secret_key"

        user = User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            role=UserRole.USER,
            family_person_id=uuid4(),
        )

        token = auth_service.create_access_token(user)
        token_data = auth_service.verify_token(token)

        assert isinstance(token_data, TokenData)
        assert token_data.user_id == user.id
        assert token_data.username == user.username
        assert token_data.role == user.role
        assert token_data.family_person_id == user.family_person_id
        assert len(token_data.permissions) > 0

    @patch("geneweb.api.security.auth.settings")
    def test_verify_token_invalid(self, mock_settings, auth_service):
        """Test token verification with invalid token."""
        mock_settings.security.secret_key = "test_secret_key"

        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_token("invalid_token")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("geneweb.api.security.auth.settings")
    def test_verify_token_wrong_type(self, mock_settings, auth_service):
        """Test token verification with wrong token type."""
        mock_settings.security.secret_key = "test_secret_key"

        user = User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            role=UserRole.USER,
        )

        refresh_token = auth_service.create_refresh_token(user)

        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_token(refresh_token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token type" in str(exc_info.value.detail)

    def test_has_permission(self, auth_service):
        """Test permission checking - all roles have all permissions now."""
        # USER has all permissions
        assert (
            auth_service.has_permission(UserRole.USER, Permission.VIEW_PUBLIC_PERSONS)
            is True
        )
        assert (
            auth_service.has_permission(UserRole.USER, Permission.CREATE_PERSON) is True
        )
        assert (
            auth_service.has_permission(UserRole.USER, Permission.MANAGE_USERS) is True
        )
        # ADMIN has all permissions
        assert (
            auth_service.has_permission(UserRole.ADMIN, Permission.MANAGE_USERS) is True
        )
        assert (
            auth_service.has_permission(UserRole.ADMIN, Permission.CREATE_PERSON)
            is True
        )

    def test_can_access_person_admin(self, auth_service):
        """Test person access for admin role."""
        user = TokenData(
            user_id=uuid4(),
            username="admin",
            role=UserRole.ADMIN,
            permissions=list(ROLE_PERMISSIONS[UserRole.ADMIN]),
        )

        person_id = uuid4()

        # Admin can access anything
        assert (
            auth_service.can_access_person(user, person_id, Permission.DELETE_PERSON)
            is True
        )
        assert (
            auth_service.can_access_person(user, person_id, Permission.VIEW_ALL_PERSONS)
            is True
        )

    def test_can_access_person_user(self, auth_service):
        """Test person access for user role - all users have all permissions now."""
        user = TokenData(
            user_id=uuid4(),
            username="user",
            role=UserRole.USER,
            permissions=list(ROLE_PERMISSIONS[UserRole.USER]),
        )

        person_id = uuid4()

        # User can access anything now
        assert (
            auth_service.can_access_person(user, person_id, Permission.DELETE_PERSON)
            is True
        )
        assert (
            auth_service.can_access_person(user, person_id, Permission.VIEW_ALL_PERSONS)
            is True
        )
        assert (
            auth_service.can_access_person(user, person_id, Permission.CREATE_PERSON)
            is True
        )

    def test_authenticate_user_not_implemented(self, auth_service):
        """Test authenticate_user returns None (not implemented)."""
        result = auth_service.authenticate_user("testuser", "password")
        assert result is None

    def test_get_user_by_username_not_implemented(self, auth_service):
        """Test get_user_by_username returns None (not implemented)."""
        result = auth_service.get_user_by_username("testuser")
        assert result is None


class TestSecurityContext:
    """Test SecurityContext class."""

    @pytest.fixture
    def token_data(self):
        """Create TokenData for testing."""
        return TokenData(
            user_id=uuid4(),
            username="testuser",
            role=UserRole.USER,
            permissions=list(ROLE_PERMISSIONS[UserRole.USER]),
            family_person_id=uuid4(),
        )

    def test_security_context_creation(self, token_data):
        """Test SecurityContext creation."""
        context = SecurityContext(
            user=token_data, ip_address="192.168.1.1", user_agent="Test Agent"
        )

        assert context.user == token_data
        assert context.ip_address == "192.168.1.1"
        assert context.user_agent == "Test Agent"
        assert isinstance(context.request_id, UUID)
        assert isinstance(context.timestamp, datetime)

    def test_has_permission(self, token_data):
        """Test permission checking in security context -
        all users have all permissions."""
        context = SecurityContext(user=token_data)

        assert context.has_permission(Permission.VIEW_PUBLIC_PERSONS) is True
        assert context.has_permission(Permission.CREATE_PERSON) is True
        assert context.has_permission(Permission.MANAGE_USERS) is True
        assert context.has_permission(Permission.SYSTEM_ADMIN) is True

    def test_require_permission_valid(self, token_data):
        """Test require_permission with valid permission -
        all permissions are valid now."""
        context = SecurityContext(user=token_data)

        # Should not raise exception for any permission
        context.require_permission(Permission.CREATE_PERSON)
        context.require_permission(Permission.MANAGE_USERS)
        context.require_permission(Permission.SYSTEM_ADMIN)

    def test_can_access_person(self, token_data):
        """Test person access checking in security context
        - all users can access all persons."""
        context = SecurityContext(user=token_data)

        # Can access any person for any action
        person_id = uuid4()
        assert (
            context.can_access_person(person_id, Permission.UPDATE_OWN_PERSON) is True
        )
        assert context.can_access_person(person_id, Permission.VIEW_ALL_PERSONS) is True
        assert context.can_access_person(person_id, Permission.DELETE_PERSON) is True

    def test_require_person_access_valid(self, token_data):
        """Test require_person_access - all access is valid now."""
        context = SecurityContext(user=token_data)

        # Should not raise exception for any person/action
        person_id = uuid4()
        context.require_person_access(person_id, Permission.UPDATE_OWN_PERSON)
        context.require_person_access(person_id, Permission.DELETE_PERSON)
        context.require_person_access(person_id, Permission.VIEW_ALL_PERSONS)

    def test_get_audit_context(self, token_data):
        """Test audit context generation."""
        context = SecurityContext(
            user=token_data, ip_address="192.168.1.1", user_agent="Test Agent"
        )

        audit_context = context.get_audit_context()

        assert audit_context["user_id"] == str(token_data.user_id)
        assert audit_context["username"] == token_data.username
        assert audit_context["role"] == token_data.role.value
        assert audit_context["ip_address"] == "192.168.1.1"
        assert audit_context["user_agent"] == "Test Agent"
        assert "request_id" in audit_context
        assert "timestamp" in audit_context


class TestGlobalAuthService:
    """Test global auth service instance."""

    def test_global_auth_service_exists(self):
        """Test that global auth service instance exists."""
        assert isinstance(auth_service, AuthService)

    def test_global_auth_service_methods(self):
        """Test that global auth service has expected methods."""
        assert hasattr(auth_service, "verify_password")
        assert hasattr(auth_service, "get_password_hash")
        assert hasattr(auth_service, "create_access_token")
        assert hasattr(auth_service, "create_refresh_token")
        assert hasattr(auth_service, "verify_token")
        assert hasattr(auth_service, "authenticate_user")
        assert hasattr(auth_service, "has_permission")
        assert hasattr(auth_service, "can_access_person")


class TestPasswordContext:
    """Test password context configuration."""

    def test_password_context_schemes(self):
        """Test that password context uses bcrypt."""
        assert "bcrypt" in pwd_context.schemes()

    def test_password_hashing_works(self):
        """Test that password hashing and verification works."""
        password = "test_password_123"
        hashed = pwd_context.hash(password)

        assert isinstance(hashed, str)
        assert hashed != password
        assert pwd_context.verify(password, hashed) is True
        assert pwd_context.verify("wrong_password", hashed) is False

    def test_long_password_truncation(self):
        """Test that passwords longer than 72 bytes are truncated."""
        # Create a password longer than 72 bytes
        long_password = "a" * 80
        auth_service = AuthService()

        # Hash should work without raising ValueError
        hashed = auth_service.get_password_hash(long_password)
        assert isinstance(hashed, str)

        # Verification should work with same long password
        assert auth_service.verify_password(long_password, hashed) is True

        # Should fail with different password
        assert auth_service.verify_password("wrong", hashed) is False

        # Passwords with same first 72 chars should match
        similar_password = "a" * 72 + "b" * 8
        assert auth_service.verify_password(similar_password, hashed) is True
