#!/usr/bin/env python3
"""
Demo script for multi-database management.

This script demonstrates how to use the new multi-database features.
"""

import json

import requests

# API base URL
BASE_URL = "http://localhost:8000/api/v1/database"


def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_json(data):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2))


def demo_multi_database_management():
    """Demonstrate multi-database management features."""

    print_section("Multi-Database Management Demo")

    # 1. List existing databases
    print_section("1. List Current Databases")
    response = requests.get(f"{BASE_URL}/databases")
    if response.status_code == 200:
        data = response.json()
        print(f"Active database: {data['active_database']}")
        print(f"Total databases: {len(data['databases'])}")
        print("\nDatabases:")
        print_json(data["databases"])
    else:
        print(f"Error: {response.status_code}")

    # 2. Create new database
    print_section("2. Create New Database")
    payload = {"name": "demo_family_tree", "set_active": False}
    response = requests.post(f"{BASE_URL}/databases", json=payload)
    if response.status_code == 201:
        data = response.json()
        print(f"✅ {data['message']}")
        print("\nDatabase info:")
        print_json(data["database"])
    else:
        print(f"Error: {response.status_code} - {response.text}")

    # 3. Create another database
    print_section("3. Create Another Database")
    payload = {"name": "demo_research", "set_active": False}
    response = requests.post(f"{BASE_URL}/databases", json=payload)
    if response.status_code == 201:
        data = response.json()
        print(f"✅ {data['message']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

    # 4. List all databases
    print_section("4. List All Databases")
    response = requests.get(f"{BASE_URL}/databases")
    if response.status_code == 200:
        data = response.json()
        print(f"Total databases: {len(data['databases'])}")
        for db in data["databases"]:
            status = "🟢 ACTIVE" if db["active"] else "⚪ Inactive"
            print(f"\n{status} - {db['name']}")
            print(f"  Path: {db['path']}")
            print(f"  Persons: {db['person_count']}, Families: {db['family_count']}")
            print(f"  Pending patches: {db['pending_patches']}")

    # 5. Get active database
    print_section("5. Get Active Database Info")
    response = requests.get(f"{BASE_URL}/databases/active")
    if response.status_code == 200:
        data = response.json()
        print(f"Active database: {data['name']}")
        print_json(data)

    # 6. Activate a database
    print_section("6. Switch Active Database")
    response = requests.post(f"{BASE_URL}/databases/demo_family_tree/activate")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['message']}")
        print(f"New active database: {data['active_database']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

    # 7. Verify active database changed
    print_section("7. Verify Active Database Changed")
    response = requests.get(f"{BASE_URL}/databases/active")
    if response.status_code == 200:
        data = response.json()
        print(f"Current active database: {data['name']}")

    # 8. Get database statistics
    print_section("8. Get Database Statistics")
    response = requests.get(f"{BASE_URL}/stats")
    if response.status_code == 200:
        data = response.json()
        print("Current database stats:")
        print_json(data)

    # 9. Delete a database (memory only)
    print_section("9. Delete Database (Memory Only)")
    # First switch to another database
    response = requests.post(f"{BASE_URL}/databases/demo_research/activate")
    if response.status_code == 200:
        # Now delete the previous active database
        response = requests.delete(
            f"{BASE_URL}/databases/demo_family_tree?delete_files=false"
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            print(f"Files deleted from disk: {data['deleted_files']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")

    # 10. Final database list
    print_section("10. Final Database List")
    response = requests.get(f"{BASE_URL}/databases")
    if response.status_code == 200:
        data = response.json()
        print(f"Remaining databases: {len(data['databases'])}")
        for db in data["databases"]:
            status = "🟢 ACTIVE" if db["active"] else "⚪ Inactive"
            print(f"{status} - {db['name']}")

    print_section("Demo Complete!")
    print("All multi-database operations demonstrated successfully!")


def demo_error_cases():
    """Demonstrate error handling."""

    print_section("Error Handling Demo")

    # 1. Try to activate non-existent database
    print_section("1. Activate Non-Existent Database")
    response = requests.post(f"{BASE_URL}/databases/nonexistent/activate")
    if response.status_code == 404:
        print("✅ Correctly returned 404 for non-existent database")
        print(f"Error: {response.json()['detail']}")

    # 2. Try to delete active database
    print_section("2. Try to Delete Active Database")
    # Get active database
    response = requests.get(f"{BASE_URL}/databases/active")
    if response.status_code == 200:
        active_name = response.json()["name"]

        # Try to delete it
        response = requests.delete(f"{BASE_URL}/databases/{active_name}")
        if response.status_code == 400:
            print("✅ Correctly prevented deletion of active database")
            print(f"Error: {response.json()['detail']}")

    print_section("Error Handling Demo Complete!")


def cleanup_demo_databases():
    """Clean up demo databases."""

    print_section("Cleanup Demo Databases")

    # Get list of databases
    response = requests.get(f"{BASE_URL}/databases")
    if response.status_code == 200:
        databases = response.json()["databases"]

        # Find demo databases
        demo_dbs = [db for db in databases if db["name"].startswith("demo_")]

        if not demo_dbs:
            print("No demo databases to clean up")
            return

        # Switch to a non-demo database first
        non_demo_db = next(
            (db for db in databases if not db["name"].startswith("demo_")), None
        )
        if non_demo_db:
            requests.post(f"{BASE_URL}/databases/{non_demo_db['name']}/activate")

        # Delete demo databases
        for db in demo_dbs:
            if not db["active"]:
                response = requests.delete(
                    f"{BASE_URL}/databases/{db['name']}?delete_files=true"
                )
                if response.status_code == 200:
                    print(f"✅ Deleted {db['name']}")
                else:
                    print(f"❌ Failed to delete {db['name']}")

    print_section("Cleanup Complete!")


if __name__ == "__main__":
    import sys

    print(
        """
╔══════════════════════════════════════════════════════════════╗
║         GeneWeb Multi-Database Management Demo              ║
║                                                              ║
║  This demo shows how to use the new multi-database features ║
╚══════════════════════════════════════════════════════════════╝
    """
    )

    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        cleanup_demo_databases()
    elif len(sys.argv) > 1 and sys.argv[1] == "--errors":
        demo_error_cases()
    else:
        print("\nOptions:")
        print("  python demo_multi_db.py           - Run full demo")
        print("  python demo_multi_db.py --errors  - Demo error handling")
        print("  python demo_multi_db.py --cleanup - Clean up demo databases")
        print("\n")

        try:
            demo_multi_database_management()
            print("\n💡 Tip: Run with --errors to see error handling examples")
            print("💡 Tip: Run with --cleanup to remove demo databases")
        except requests.exceptions.ConnectionError:
            print("\n❌ ERROR: Could not connect to API server")
            print("Make sure the GeneWeb API is running on http://localhost:8000")
            print("\nStart the server with:")
            print("  cd geneweb_python")
            print("  python start_api.py")
            sys.exit(1)
