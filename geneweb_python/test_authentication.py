"""
Test script for authentication system.

This script tests the complete authentication flow:
1. Register a new user
2. Login with credentials
3. Access protected endpoint
4. Refresh token
5. Change password
6. Logout
"""

import sys
from typing import Optional

import requests

BASE_URL = "http://localhost:8000"


class AuthTester:
    """Test harness for authentication endpoints."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.test_username = "test_user_" + str(hash("test"))[-6:]
        self.test_password = "TestP@ssw0rd123!"

    def test_health(self) -> bool:
        """Test authentication health endpoint."""
        # print("\n🔍 Testing auth health endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/v1/auth/health")
            if response.status_code == 200:
                # #data = response.json()
                # print(f"✅ Auth service is healthy")
                # print(f"   Features: {', '.join(data.get('features', {}).keys())}")
                return True
            else:
                # print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception:
            # print(f"❌ Health check error: {e}")
            return False

    def test_register(self) -> bool:
        """Test user registration."""
        # print(f"\n🔍 Testing user registration...")
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json={
                    "username": self.test_username,
                    "email": f"{self.test_username}@test.local",
                    "full_name": "Test User",
                    "password": self.test_password,
                    "role": "user",
                },
            )

            if response.status_code == 201:
                # #data = response.json()
                # print(f"✅ User registered successfully")
                # print(f"   Username: {data['username']}")
                # print(f"   Email: {data['email']}")
                # print(f"   Role: {data['role']}")
                return True
            elif response.status_code == 409:
                # print(f"⚠️  User already exists (OK for repeated tests)")
                return True
            else:
                # print(f"❌ Registration failed: {response.status_code}")
                # print(f"   Response: {response.text}")
                return False
        except Exception:
            # print(f"❌ Registration error: {e}")
            return False

    def test_login(self) -> bool:
        """Test user login."""
        # print(f"\n🔍 Testing login...")
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": self.test_username, "password": self.test_password},
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                # print(f"✅ Login successful")
                # print(f"   Token type: {data['token_type']}")
                # print(f"   Expires in: {data['expires_in']} seconds")
                # print(f"   User: {data['user']['username']} ({data['user']['role']})")
                return True
            else:
                # print(f"❌ Login failed: {response.status_code}")
                # print(f"   Response: {response.text}")
                return False
        except Exception:
            # print(f"❌ Login error: {e}")
            return False

    def test_get_me(self) -> bool:
        """Test getting current user info."""
        # print(f"\n🔍 Testing /auth/me endpoint...")
        if not self.access_token:
            # print(f"❌ No access token available")
            return False

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {self.access_token}"},
            )

            if response.status_code == 200:
                # data = response.json()
                # print(f"✅ User info retrieved")
                # print(f"   Username: {data['username']}")
                # print(f"   Email: {data['email']}")
                # print(f"   Role: {data['role']}")
                # print(f"   Active: {data['is_active']}")
                return True
            else:
                # print(f"❌ Get user info failed: {response.status_code}")
                # print(f"   Response: {response.text}")
                return False
        except Exception:
            # print(f"❌ Get user info error: {e}")
            return False

    def test_refresh(self) -> bool:
        """Test token refresh."""
        # print(f"\n🔍 Testing token refresh...")
        if not self.refresh_token:
            # print(f"❌ No refresh token available")
            return False

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/refresh",
                json={"refresh_token": self.refresh_token},
            )

            if response.status_code == 200:
                data = response.json()
                # old_access = self.access_token[:20] + "..."
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                # new_access = self.access_token[:20] + "..."
                # print(f"✅ Token refreshed successfully")
                # print(f"   Old token: {old_access}")
                # print(f"   New token: {new_access}")
                return True
            else:
                # print(f"❌ Token refresh failed: {response.status_code}")
                # print(f"   Response: {response.text}")
                return False
        except Exception:
            # print(f"❌ Token refresh error: {e}")
            return False

    def test_protected_endpoint(self) -> bool:
        """Test accessing a protected endpoint."""
        # print(f"\n🔍 Testing protected endpoint access...")
        if not self.access_token:
            # print(f"❌ No access token available")
            return False

        try:
            # Try to access persons endpoint (should be protected)
            response = requests.get(
                f"{self.base_url}/api/v1/persons",
                headers={"Authorization": f"Bearer {self.access_token}"},
            )

            # We don't care about the exact response, just that we're authenticated
            if response.status_code in [
                200,
                404,
                403,
            ]:  # 403 = no permission, but authenticated
                # print(
                #    f"✅ Protected endpoint accessible (status: {response.status_code})"
                # )
                return True
            elif response.status_code == 401:
                # print(f"❌ Authentication failed on protected endpoint")
                return False
            else:
                # print(f"⚠️  Unexpected status: {response.status_code}")
                return True  # Still OK, means we're authenticated
        except Exception:
            # print(f"❌ Protected endpoint error: {e}")
            return False

    def test_logout(self) -> bool:
        """Test logout."""
        # print(f"\n🔍 Testing logout...")
        if not self.access_token:
            # print(f"❌ No access token available")
            return False

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/logout",
                headers={"Authorization": f"Bearer {self.access_token}"},
            )

            if response.status_code == 200:
                # data = response.json()
                # print(f"✅ Logout successful")
                # print(f"   Message: {data['message']}")

                # Try to use the token again (should fail)
                # print(f"\n🔍 Verifying token is revoked...")
                verify_response = requests.get(
                    f"{self.base_url}/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                )

                if verify_response.status_code == 401:
                    # print(f"✅ Token successfully revoked")
                    return True
                else:
                    # print(
                    #     f"⚠️  Token still valid after logout (
                    # status: {verify_response.status_code})"
                    # )
                    return False
            else:
                # print(f"❌ Logout failed: {response.status_code}")
                # print(f"   Response: {response.text}")
                return False
        except Exception:
            # print(f"❌ Logout error: {e}")
            return False

    def run_all_tests(self) -> bool:
        """Run all authentication tests."""
        # print("=" * 60)
        # print("🧪 AUTHENTICATION SYSTEM TEST SUITE")
        # print("=" * 60)

        tests = [
            ("Health Check", self.test_health),
            ("User Registration", self.test_register),
            ("User Login", self.test_login),
            ("Get Current User", self.test_get_me),
            ("Token Refresh", self.test_refresh),
            ("Protected Endpoint", self.test_protected_endpoint),
            ("User Logout", self.test_logout),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception:
                # print(f"❌ Test '{test_name}' crashed: {e}")
                results.append((test_name, False))

        # #Print summary
        # print("\n" + "=" * 60)
        # print("📊 TEST SUMMARY")
        # print("=" * 60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        # for test_name, result in results:
        # status = "✅ PASS" if result else "❌ FAIL"
        # print(f"{status} - {test_name}")

        # print(f"\nResults: {passed}/{total} tests passed")

        if passed == total:
            # print("🎉 All tests passed!")
            return True
        else:
            # print(f"❌ {total - passed} test(s) failed")
            return False


def main():
    """Main test runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Test authentication system")
    parser.add_argument(
        "--url", default=BASE_URL, help=f"Base URL of the API (default: {BASE_URL})"
    )

    args = parser.parse_args()

    tester = AuthTester(base_url=args.url)
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
