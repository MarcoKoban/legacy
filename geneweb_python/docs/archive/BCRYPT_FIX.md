# BCrypt Password Truncation Fix

## Problem

Tests were failing in GitHub Actions but passing locally with the following error:

```
ValueError: password cannot be longer than 72 bytes, truncate manually if necessary (e.g. my_password[:72])
```

### Affected Tests
- `tests/unit/api/security/test_auth.py::TestAuthService::test_verify_password`
- `tests/unit/api/security/test_auth.py::TestAuthService::test_get_password_hash`
- `tests/unit/api/security/test_auth.py::TestPasswordContext::test_password_hashing_works`
- `tests/unit/api/security/test_auth.py::TestPasswordContext::test_long_password_truncation`

## Root Cause

**BCrypt v4.1.0+** introduced a strict 72-byte password limit. When a password exceeds 72 bytes, it now raises a `ValueError` instead of silently handling the truncation.

The issue occurred because:
1. Tests were calling `pwd_context.hash()` and `pwd_context.verify()` directly
2. These direct calls bypassed the truncation logic in `AuthService.get_password_hash()` and `AuthService.verify_password()`
3. Different environments (local vs GitHub Actions) may have had different bcrypt behavior

## Solution

Created a **custom `TruncatingCryptContext`** class that extends `passlib.context.CryptContext` to automatically truncate passwords before hashing or verification:

```python
def _truncate_password(password: str) -> str:
    """
    Truncate password to 72 bytes for bcrypt compatibility.
    
    Bcrypt has a 72-byte limit. This function ensures passwords are truncated
    safely without breaking UTF-8 character boundaries.
    """
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        # Truncate at byte level, ensuring we don't break UTF-8 sequences
        truncated = password_bytes[:72]
        # Decode with error handling in case we cut in the middle of a multi-byte char
        return truncated.decode("utf-8", errors="ignore")
    return password


class TruncatingCryptContext(CryptContext):
    """CryptContext that automatically truncates passwords to 72 bytes for bcrypt."""
    
    def hash(self, secret, **kwds):
        """Hash a password, truncating to 72 bytes for bcrypt."""
        # Always truncate before passing to bcrypt
        truncated_secret = _truncate_password(secret)
        # Don't pass truncate_error to avoid issues with different bcrypt versions
        kwds.pop('truncate_error', None)
        return super().hash(truncated_secret, **kwds)
    
    def verify(self, secret, hash, **kwds):
        """Verify a password, truncating to 72 bytes for bcrypt."""
        # Always truncate before passing to bcrypt
        truncated_secret = _truncate_password(secret)
        # Don't pass truncate_error to avoid issues with different bcrypt versions
        kwds.pop('truncate_error', None)
        return super().verify(truncated_secret, hash, **kwds)


pwd_context = TruncatingCryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False,  # Explicitly disable truncate_error for bcrypt
)
```

## Benefits

1. **Consistent behavior**: All password operations (direct or through `AuthService`) now handle long passwords correctly
2. **BCrypt compatibility**: Works with both old and new versions of bcrypt (including v4.1.0+ with strict truncation)
3. **UTF-8 safe**: Properly handles multi-byte characters without breaking character boundaries
4. **Transparent**: No changes needed to existing code that uses `pwd_context`
5. **Explicit configuration**: The `bcrypt__truncate_error=False` parameter explicitly tells passlib to not raise errors on truncation
6. **Defensive programming**: Removes any `truncate_error` keyword arguments that might be passed through different code paths

## Testing

All 37 tests in `tests/unit/api/security/test_auth.py` pass, including:
- Password hashing and verification with normal passwords
- Long password truncation (>72 bytes)
- Direct calls to `pwd_context.hash()` and `pwd_context.verify()`

## Security Note

The 72-byte limit is a BCrypt algorithm limitation, not a security concern. Passwords are truncated consistently during both hashing and verification, ensuring authentication still works correctly. Users should still be encouraged to use strong passwords within the limit.
