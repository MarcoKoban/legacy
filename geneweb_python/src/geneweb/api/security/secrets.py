"""
Secrets management for Geneweb API
Handles encryption, key derivation, and secure storage
"""

import base64
import hashlib
import secrets
from typing import Dict, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..config import settings


class SecretsManager:
    """
    Manages secrets encryption and decryption
    """

    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize secrets manager with master key
        """
        self.master_key = master_key or settings.security.secret_key
        self._fernet = None

    def _get_fernet(self) -> Fernet:
        """
        Get or create Fernet instance for encryption
        """
        if self._fernet is None:
            # Derive key from master key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"geneweb_salt_2024",  # In production, use random salt per secret
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
            self._fernet = Fernet(key)

        return self._fernet

    def encrypt_secret(self, secret: str) -> str:
        """
        Encrypt a secret value
        """
        fernet = self._get_fernet()
        encrypted = fernet.encrypt(secret.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt_secret(self, encrypted_secret: str) -> str:
        """
        Decrypt a secret value
        """
        fernet = self._get_fernet()
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_secret.encode())
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode()

    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate a secure random token
        """
        return secrets.token_urlsafe(length)

    def hash_password(
        self, password: str, salt: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Hash a password with secure salt
        """
        if salt is None:
            salt = secrets.token_hex(16)

        # Use PBKDF2 with SHA256
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )

        hash_bytes = kdf.derive(password.encode())
        password_hash = base64.urlsafe_b64encode(hash_bytes).decode()

        return {
            "hash": password_hash,
            "salt": salt,
            "algorithm": "pbkdf2_sha256",
            "iterations": "100000",
        }

    def verify_password(self, password: str, stored_hash: Dict[str, str]) -> bool:
        """
        Verify a password against stored hash
        """
        try:
            computed_hash = self.hash_password(password, stored_hash["salt"])
            return secrets.compare_digest(computed_hash["hash"], stored_hash["hash"])
        except Exception:
            return False

    def generate_api_key(self, prefix: str = "gw") -> Dict[str, str]:
        """
        Generate a secure API key with checksum
        """
        # Generate random part
        random_part = secrets.token_urlsafe(24)

        # Create checksum
        checksum = hashlib.sha256(f"{prefix}_{random_part}".encode()).hexdigest()[:8]

        # Combine parts
        api_key = f"{prefix}_{random_part}_{checksum}"

        # Hash for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        return {"api_key": api_key, "hash": key_hash, "prefix": prefix}

    def verify_api_key(self, api_key: str, stored_hash: str) -> bool:
        """
        Verify an API key against stored hash
        """
        computed_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return secrets.compare_digest(computed_hash, stored_hash)


class CertificatePinning:
    """
    Certificate pinning implementation
    """

    def __init__(self, pins: list = None):
        """
        Initialize with certificate pins
        """
        self.pins = pins or settings.security.cert_pins

    def add_pin(self, pin: str):
        """
        Add a certificate pin
        """
        if pin not in self.pins:
            self.pins.append(pin)

    def verify_pin(self, cert_fingerprint: str) -> bool:
        """
        Verify certificate against pins
        """
        return cert_fingerprint in self.pins

    def get_hpkp_header(self, max_age: int = 2592000) -> str:
        """
        Generate HPKP header value
        """
        if not self.pins:
            return ""

        pins_str = "; ".join([f'pin-sha256="{pin}"' for pin in self.pins])
        return f"{pins_str}; max-age={max_age}; includeSubDomains"


# Global instances
secrets_manager = SecretsManager()
cert_pinning = CertificatePinning()


def get_secrets_manager() -> SecretsManager:
    """
    Get the global secrets manager instance
    """
    return secrets_manager


def get_certificate_pinning() -> CertificatePinning:
    """
    Get the global certificate pinning instance
    """
    return cert_pinning
