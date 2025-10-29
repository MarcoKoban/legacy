#!/usr/bin/env python
"""
Simple test script to verify database ownership functionality.
This tests that:
1. Users can create databases (owned by them)
2. Users can only see their own databases
3. Admins can see all databases
"""

import sys
from uuid import uuid4

from src.geneweb.api.dependencies import DatabaseManager


def test_database_ownership():
    """Test database ownership isolation."""

    print("=" * 60)
    print("Testing Database Ownership System")
    print("=" * 60)

    # Create a fresh database manager for testing
    db_manager = DatabaseManager()

    # Simulate two different users
    user1_id = str(uuid4())
    user2_id = str(uuid4())

    print(f"\nUser 1 ID: {user1_id}")
    print(f"User 2 ID: {user2_id}")

    # Test 1: User 1 creates a database
    print("\n[TEST 1] User 1 creates 'user1_db'...")
    try:
        db_name = db_manager.create_database(
            name="user1_db", create_if_missing=True, set_active=False, owner_id=user1_id
        )
        print(f"✓ Database '{db_name}' created successfully with owner: {user1_id}")
    except Exception as e:
        print(f"✗ Failed to create database: {e}")
        return False

    # Test 2: User 2 creates a database
    print("\n[TEST 2] User 2 creates 'user2_db'...")
    try:
        db_name = db_manager.create_database(
            name="user2_db", create_if_missing=True, set_active=False, owner_id=user2_id
        )
        print(f"✓ Database '{db_name}' created successfully with owner: {user2_id}")
    except Exception as e:
        print(f"✗ Failed to create database: {e}")
        return False

    # Test 3: User 1 can only see their own database
    print("\n[TEST 3] User 1 lists databases (should only see user1_db)...")
    user1_dbs = db_manager.list_databases(user_id=user1_id, is_admin=False)
    user1_db_names = [db["name"] for db in user1_dbs]
    print(f"User 1 sees: {user1_db_names}")

    if "user1_db" in user1_db_names and "user2_db" not in user1_db_names:
        print("✓ User 1 can only see their own database")
    else:
        print("✗ User 1 sees databases they shouldn't!")
        return False

    # Test 4: User 2 can only see their own database
    print("\n[TEST 4] User 2 lists databases (should only see user2_db)...")
    user2_dbs = db_manager.list_databases(user_id=user2_id, is_admin=False)
    user2_db_names = [db["name"] for db in user2_dbs]
    print(f"User 2 sees: {user2_db_names}")

    if "user2_db" in user2_db_names and "user1_db" not in user2_db_names:
        print("✓ User 2 can only see their own database")
    else:
        print("✗ User 2 sees databases they shouldn't!")
        return False

    # Test 5: Admin can see all databases
    print("\n[TEST 5] Admin lists databases (should see both)...")
    admin_dbs = db_manager.list_databases(user_id=str(uuid4()), is_admin=True)
    admin_db_names = [db["name"] for db in admin_dbs]
    print(f"Admin sees: {admin_db_names}")

    if "user1_db" in admin_db_names and "user2_db" in admin_db_names:
        print("✓ Admin can see all databases")
    else:
        print("✗ Admin doesn't see all databases!")
        return False

    # Test 6: User 1 cannot access User 2's database
    print("\n[TEST 6] User 1 tries to access user2_db...")
    can_access = db_manager.can_access_database("user2_db", user1_id, is_admin=False)
    if not can_access:
        print("✓ User 1 correctly denied access to user2_db")
    else:
        print("✗ User 1 should not be able to access user2_db!")
        return False

    # Test 7: User 1 CAN access their own database
    print("\n[TEST 7] User 1 tries to access user1_db...")
    can_access = db_manager.can_access_database("user1_db", user1_id, is_admin=False)
    if can_access:
        print("✓ User 1 correctly has access to user1_db")
    else:
        print("✗ User 1 should be able to access their own database!")
        return False

    # Test 8: Admin CAN access any database
    print("\n[TEST 8] Admin tries to access user1_db...")
    can_access = db_manager.can_access_database("user1_db", str(uuid4()), is_admin=True)
    if can_access:
        print("✓ Admin correctly has access to user1_db")
    else:
        print("✗ Admin should be able to access any database!")
        return False

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_database_ownership()
    sys.exit(0 if success else 1)
