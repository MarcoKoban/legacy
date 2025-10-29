#!/usr/bin/env python3
"""
Test script to verify authentication is enforced on all protected endpoints.
"""

import sys

import requests

BASE_URL = "http://localhost:8000"


def test_endpoint_without_auth(endpoint: str, method: str = "GET"):
    """Test that endpoint returns 401 without authentication."""
    # print(f"\n🔍 Testing {method} {endpoint} WITHOUT authentication...")

    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json={}, timeout=5)
        else:
            # print(f"  ❌ Unsupported method: {method}")
            return False

        if response.status_code == 401:
            # print(f"  ✅ PASS: Got 401 Unauthorized (expected)")
            return True
        else:
            # print(f"  ❌ FAIL: Got {response.status_code}")
            # print(f"  Response: {response.text[:200]}")
            return False
    except requests.exceptions.ConnectionError:
        # print(f"  ⚠️  ERROR: Cannot connect to {BASE_URL}")
        return None
    except Exception:
        # print(f"  ⚠️  ERROR: {e}")
        return None


def test_endpoint_with_auth(endpoint: str, token: str, method: str = "GET"):
    """Test that endpoint works with valid authentication."""
    # print(f"\n🔍 Testing {method} {endpoint} WITH authentication...")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        if method == "GET":
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                timeout=5,
            )
        elif method == "POST":
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                json={},
                headers=headers,
                timeout=5,
            )
        else:
            # print(f"  ❌ Unsupported method: {method}")
            return False

        if response.status_code in [
            200,
            201,
            404,
        ]:  # 404 ok (endpoint exists but resource not found)
            # print(f"  ✅ PASS: Got {response.status_code}")
            return True
        elif response.status_code == 403:
            # print(f"  ⚠️  Got 403 Forbidden")
            # (authenticated but insufficient permissions)
            return True  # This is acceptable - auth is working
        else:
            # print(f"  ❌ FAIL: Got {response.status_code}")
            # print(f"  Response: {response.text[:200]}")
            return False
    except Exception:
        # print(f"  ⚠️  ERROR: {e}")
        return None


def get_admin_token():
    """Get admin token by logging in."""
    # print("\n🔐 Logging in as admin to get token...")

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=5,
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            # print(f"  ✅ Login successful, got token: {token[:20]}...")
            return token
        else:
            # print(f"  ❌ Login failed with status {response.status_code}")
            # print(f"  Response: {response.text}")
            return None
    except Exception:
        # print(f"  ⚠️  ERROR: {e}")
        return None


def main():
    """Run authentication enforcement tests."""
    # print("=" * 60)
    # print("🧪 Authentication Enforcement Test Suite")
    # print("=" * 60)

    # Test endpoints that should require authentication
    endpoints_to_test = [
        ("/api/v1/persons", "POST"),
        ("/api/v1/persons", "GET"),
        ("/api/v1/database/databases", "GET"),
        ("/api/v1/database/databases", "POST"),
        ("/api/v1/database/stats", "GET"),
        ("/api/v1/database/health", "GET"),
        ("/api/v1/database/info", "GET"),
    ]

    # print("\n" + "=" * 60)
    # print("PHASE 1: Test WITHOUT authentication (should get 401)")
    # print("=" * 60)

    results_without_auth = []
    for endpoint, method in endpoints_to_test:
        result = test_endpoint_without_auth(endpoint, method)
        results_without_auth.append((endpoint, method, result))

    # Get admin token for authenticated tests
    admin_token = get_admin_token()

    if admin_token:
        # print("\n" + "=" * 60)
        # print("PHASE 2: Test WITH authentication (should work)")
        # print("=" * 60)

        results_with_auth = []
        for endpoint, method in endpoints_to_test:
            result = test_endpoint_with_auth(endpoint, admin_token, method)
            results_with_auth.append((endpoint, method, result))
    else:
        # print("\n⚠️  Skipping authenticated tests (couldn't get token)")
        results_with_auth = []

    # Summary
    # print("\n" + "=" * 60)
    # print("📊 SUMMARY")
    # print("=" * 60)

    # without_auth_pass = sum(
    #   1 for _, _, r in results_without_auth if r == True
    # )
    without_auth_fail = sum(1 for _, _, r in results_without_auth if r is False)
    without_auth_error = sum(1 for _, _, r in results_without_auth if r is None)

    # print(f"\nWithout Auth Tests:")
    # print(f"  ✅ Passed: {without_auth_pass}/...")
    # print(f"  ❌ Failed: {without_auth_fail}/...")
    # print(f"  ⚠️  Errors: {without_auth_error}/...")

    if results_with_auth:
        # with_auth_pass = sum(
        #   1 for _, _, r in results_with_auth if r == True
        # )
        with_auth_fail = sum(1 for _, _, r in results_with_auth if r is False)
        with_auth_error = sum(1 for _, _, r in results_with_auth if r is None)

        # print(f"\nWith Auth Tests:")
        # print(f"  ✅ Passed: {with_auth_pass}/{len(results_with_auth)}")
        # print(f"  ❌ Failed: {with_auth_fail}/{len(results_with_auth)}")
        # print(f"  ⚠️  Errors: {with_auth_error}/{len(results_with_auth)}")

    # Exit code
    if without_auth_fail > 0 or (results_with_auth and with_auth_fail > 0):
        # print("\n❌ TESTS FAILED")
        sys.exit(1)
    elif without_auth_error > 0 or (results_with_auth and with_auth_error > 0):
        # print("\n⚠️  TESTS HAD ERRORS")
        sys.exit(2)
    else:
        # print("\n✅ ALL TESTS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
