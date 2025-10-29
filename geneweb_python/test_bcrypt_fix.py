#!/usr/bin/env python3
"""
Test script to verify bcrypt password truncation handling.

This script tests that our TruncatingCryptContext correctly handles
long passwords (>72 bytes) without raising ValueError, which can occur
with bcrypt v4.1.0+ when truncate_error is enabled.

Run this script to verify the fix works correctly:
    python test_bcrypt_fix.py
"""

import sys
from pathlib import Path

from geneweb.api.security.auth import AuthService, pwd_context

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_password_context_with_long_password():
    """Test that pwd_context handles long passwords correctly."""
    # Create a password longer than 72 bytes
    long_password = "a" * 100

    try:
        # Hash the password
        hashed = pwd_context.hash(long_password)

        # Verify the password
        assert pwd_context.verify(
            long_password, hashed
        ), "Password verification failed!"

        # Verify that passwords with same first 72 bytes match
        similar_password = "a" * 72 + "b" * 28
        assert pwd_context.verify(
            similar_password, hashed
        ), "Similar password verification failed!"

        return True
    except ValueError:
        return False


def test_auth_service_with_long_password():
    """Test that AuthService handles long passwords correctly."""
    auth_service = AuthService()
    long_password = "x" * 150

    try:
        # Hash the password
        hashed = auth_service.get_password_hash(long_password)
        # Verify the password
        assert auth_service.verify_password(
            long_password, hashed
        ), "Password verification failed!"

        return True
    except ValueError:
        return False


def test_normal_password():
    """Test that normal passwords still work correctly."""
    normal_password = "MySecurePassword123!"

    try:
        hashed = pwd_context.hash(normal_password)

        assert pwd_context.verify(normal_password, hashed), "Verification failed!"

        assert not pwd_context.verify(
            "WrongPassword", hashed
        ), "Wrong password verified!"

        return True
    except Exception:
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("BCrypt Password Truncation Fix Test")
    print("=" * 60)

    # Run all tests
    results = []
    results.append(test_password_context_with_long_password())
    results.append(test_auth_service_with_long_password())
    results.append(test_normal_password())

    print("\n" + "=" * 60)
    if all(results):
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED!")
        print("=" * 60)
        sys.exit(1)
