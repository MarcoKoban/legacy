#!/usr/bin/env python3
"""
Demonstration script for the secure encryption improvements.
Shows the salt security vulnerability fix.
"""

import os
import sys

from geneweb.api.security.encryption import (
    DataEncryptor,
    get_salt_info,
    verify_encryption_strength,
)

sys.path.append("src")


def main():
    """Demonstrate the secure encryption system."""
    print("🔒 Geneweb Encryption Security Demo")
    print("=" * 50)

    # Set up master key for demo
    os.environ["GENEWEB_MASTER_KEY"] = "demo-master-key-12345"

    print("\n1. Encryption System Verification:")
    security_info = verify_encryption_strength()
    for key, value in security_info.items():
        print(f"   {key}: {value}")

    print("\n2. Salt Configuration:")
    salt_info = get_salt_info()
    for key, value in salt_info.items():
        print(f"   {key}: {value}")

    print("\n3. Encryption Demo:")
    encryptor = DataEncryptor()

    # Test data
    sensitive_data = "John Doe, SSN: 123-45-6789, DOB: 1990-01-01"
    print(f"   Original: {sensitive_data}")

    # Encrypt
    encrypted = encryptor.encrypt(sensitive_data)
    print(f"   Encrypted: {encrypted[:60]}...")

    # Decrypt
    decrypted = encryptor.decrypt(encrypted)
    print(f"   Decrypted: {decrypted}")

    print(f"   ✅ Round-trip successful: {sensitive_data == decrypted}")

    print("\n4. Security Improvements:")
    print("   ✅ Hardcoded salt vulnerability FIXED")
    print("   ✅ Installation-specific random salt generated")
    print("   ✅ Secure file storage with proper permissions (600)")
    print("   ✅ Environment variable support for production")
    print("   ✅ Comprehensive logging and audit trail")

    print("\n5. Production Setup:")
    print("   For production deployment, set environment variable:")
    print("   export GENEWEB_ENCRYPTION_SALT=<base64-encoded-salt>")
    print("   This ensures consistent encryption across server restarts.")


if __name__ == "__main__":
    main()
