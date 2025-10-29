"""
Secure audit trail system with cryptographic signatures for GDPR compliance.
"""

import hashlib
import hmac
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import structlog
from pydantic import BaseModel, Field

from ..config import settings
from .encryption import decrypt_json_data, encrypt_json_data

logger = structlog.get_logger(__name__)


class AuditAction(str, Enum):
    """Audit trail action types."""

    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    ANONYMIZE = "ANONYMIZE"
    EXPORT = "EXPORT"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CONSENT_GRANT = "CONSENT_GRANT"
    CONSENT_WITHDRAW = "CONSENT_WITHDRAW"
    ACCESS_DENIED = "ACCESS_DENIED"


class AuditSeverity(str, Enum):
    """Audit event severity levels."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuditEvent(BaseModel):
    """Comprehensive audit event model."""

    # Core identification
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Action details
    action: AuditAction
    severity: AuditSeverity = Field(default=AuditSeverity.INFO)
    description: str

    # User context
    user_id: Optional[UUID] = None
    username: Optional[str] = None
    user_role: Optional[str] = None

    # Request context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[UUID] = None
    session_id: Optional[str] = None

    # Resource context
    resource_type: Optional[str] = None  # "person", "family", "user", etc.
    resource_id: Optional[UUID] = None
    parent_resource_id: Optional[UUID] = None

    # Data changes (encrypted for sensitive data)
    old_values: Optional[str] = None  # Encrypted JSON
    new_values: Optional[str] = None  # Encrypted JSON

    # GDPR compliance
    gdpr_lawful_basis: Optional[str] = None
    data_subject_id: Optional[UUID] = None  # Person whose data is affected
    consent_reference: Optional[str] = None

    # Security
    checksum: Optional[str] = None  # Cryptographic signature
    chain_hash: Optional[str] = None  # Hash linking to previous event

    # Additional metadata
    metadata: Optional[str] = None  # Encrypted JSON for additional context


class AuditTrail:
    """Secure audit trail manager with cryptographic integrity."""

    def __init__(self):
        self.secret_key = settings.security.secret_key.encode()
        self._last_hash: Optional[str] = None

    def _generate_checksum(self, event: AuditEvent) -> str:
        """Generate HMAC signature for audit event integrity."""
        # Create canonical representation
        data_to_sign = {
            "id": str(event.id),
            "timestamp": event.timestamp.isoformat(),
            "action": event.action.value,
            "user_id": str(event.user_id) if event.user_id else None,
            "resource_type": event.resource_type,
            "resource_id": str(event.resource_id) if event.resource_id else None,
            "description": event.description,
            "old_values": event.old_values,
            "new_values": event.new_values,
        }

        canonical_json = json.dumps(data_to_sign, sort_keys=True, separators=(",", ":"))

        return hmac.new(
            self.secret_key, canonical_json.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def _generate_chain_hash(self, current_checksum: str) -> str:
        """Generate hash linking to previous audit event."""
        if self._last_hash is None:
            # First event in chain
            chain_data = f"genesis_{current_checksum}"
        else:
            chain_data = f"{self._last_hash}_{current_checksum}"

        return hashlib.sha256(chain_data.encode("utf-8")).hexdigest()

    def _encrypt_data_changes(self, data: Optional[Dict[str, Any]]) -> Optional[str]:
        """Encrypt sensitive data changes."""
        if data is None:
            return None

        # Filter out sensitive fields that should be encrypted
        sensitive_fields = {
            "birth_date",
            "birth_place",
            "death_date",
            "death_place",
            "email",
            "phone",
            "address",
            "notes",
        }

        sensitive_data = {k: v for k, v in data.items() if k in sensitive_fields}
        non_sensitive_data = {
            k: v for k, v in data.items() if k not in sensitive_fields
        }

        result = non_sensitive_data.copy()

        if sensitive_data:
            try:
                result["_encrypted_sensitive"] = encrypt_json_data(sensitive_data)
            except Exception as e:
                # Encryption failure should not block the request lifecycle.
                # Log a warning and continue without encrypted payload.
                logger.warning(
                    "Failed to encrypt sensitive audit data; "
                    "continuing without encrypted payload",
                    error=str(e),
                )
                # Do not include plaintext sensitive data in the audit event.
                result["_encrypted_sensitive"] = None

        return json.dumps(result, default=str)

    async def log_event(
        self,
        action: AuditAction,
        description: str,
        user_id: Optional[UUID] = None,
        username: Optional[str] = None,
        user_role: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        gdpr_lawful_basis: Optional[str] = None,
        data_subject_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """Log a comprehensive audit event."""

        # Try to encrypt metadata if provided, but don't fail on encryption errors
        encrypted_metadata = None
        if metadata:
            try:
                encrypted_metadata = encrypt_json_data(metadata)
            except Exception as e:
                logger.warning(
                    "Failed to encrypt audit metadata; "
                    "continuing without encrypted metadata",
                    error=str(e),
                )

        event = AuditEvent(
            action=action,
            description=description,
            severity=severity,
            user_id=user_id,
            username=username,
            user_role=user_role,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=self._encrypt_data_changes(old_values),
            new_values=self._encrypt_data_changes(new_values),
            gdpr_lawful_basis=gdpr_lawful_basis,
            data_subject_id=data_subject_id,
            metadata=encrypted_metadata,
        )

        # Generate cryptographic signatures
        event.checksum = self._generate_checksum(event)
        event.chain_hash = self._generate_chain_hash(event.checksum)

        # Update chain state
        self._last_hash = event.chain_hash

        # Log to structured logger
        logger.info(
            "Audit event",
            event_id=str(event.id),
            action=action.value,
            user_id=str(user_id) if user_id else None,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            severity=severity.value,
            ip_address=ip_address,
            checksum=event.checksum[:16],  # First 16 chars for logging
        )

        # Store in database (implement database storage)
        await self._store_audit_event(event)

        return event

    async def _store_audit_event(self, event: AuditEvent):
        """Store audit event in database."""
        # TODO: Implement database storage
        # This should store the event in a tamper-evident way
        pass

    def verify_event_integrity(self, event: AuditEvent) -> bool:
        """Verify cryptographic integrity of audit event."""
        try:
            expected_checksum = self._generate_checksum(event)
            return hmac.compare_digest(expected_checksum, event.checksum or "")
        except Exception as e:
            logger.error("Audit integrity verification failed", error=str(e))
            return False

    async def get_audit_trail(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        action: Optional[AuditAction] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Retrieve audit trail with filtering."""
        # TODO: Implement database query
        return []

    async def export_gdpr_audit_trail(self, data_subject_id: UUID) -> Dict[str, Any]:
        """Export complete audit trail for GDPR data subject."""
        events = await self.get_audit_trail(data_subject_id=data_subject_id)

        # Decrypt sensitive data for export
        decrypted_events = []
        for event in events:
            event_dict = event.model_dump()

            # Decrypt old/new values for transparency
            if event.old_values:
                try:
                    old_data = json.loads(event.old_values)
                    if "_encrypted_sensitive" in old_data:
                        sensitive_data = decrypt_json_data(
                            old_data["_encrypted_sensitive"]
                        )
                        old_data.update(sensitive_data)
                        del old_data["_encrypted_sensitive"]
                    event_dict["old_values"] = old_data
                except Exception:
                    event_dict["old_values"] = "Data could not be decrypted"

            if event.new_values:
                try:
                    new_data = json.loads(event.new_values)
                    if "_encrypted_sensitive" in new_data:
                        sensitive_data = decrypt_json_data(
                            new_data["_encrypted_sensitive"]
                        )
                        new_data.update(sensitive_data)
                        del new_data["_encrypted_sensitive"]
                    event_dict["new_values"] = new_data
                except Exception:
                    event_dict["new_values"] = "Data could not be decrypted"

            decrypted_events.append(event_dict)

        return {
            "data_subject_id": str(data_subject_id),
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_events": len(decrypted_events),
            "events": decrypted_events,
            "integrity_verified": all(
                self.verify_event_integrity(event) for event in events
            ),
        }


class AuditLogger:
    """High-level audit logging interface."""

    def __init__(self):
        self.audit_trail = AuditTrail()

    async def log_person_created(
        self, security_context, person_id: UUID, person_data: Dict[str, Any]
    ):
        """Log person creation."""
        await self.audit_trail.log_event(
            action=AuditAction.CREATE,
            description=(
                f"Person created: {person_data.get('first_name', '')} "
                f"{person_data.get('last_name', '')}"
            ),
            user_id=security_context.user.user_id,
            username=security_context.user.username,
            user_role=security_context.user.role.value,
            ip_address=security_context.ip_address,
            user_agent=security_context.user_agent,
            request_id=security_context.request_id,
            resource_type="person",
            resource_id=person_id,
            new_values=person_data,
            data_subject_id=person_id,
            gdpr_lawful_basis="consent",
        )

    async def log_person_updated(
        self,
        security_context,
        person_id: UUID,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any],
    ):
        """Log person update."""
        await self.audit_trail.log_event(
            action=AuditAction.UPDATE,
            description=f"Person updated: {person_id}",
            user_id=security_context.user.user_id,
            username=security_context.user.username,
            user_role=security_context.user.role.value,
            ip_address=security_context.ip_address,
            user_agent=security_context.user_agent,
            request_id=security_context.request_id,
            resource_type="person",
            resource_id=person_id,
            old_values=old_data,
            new_values=new_data,
            data_subject_id=person_id,
            gdpr_lawful_basis="legitimate_interest",
        )

    async def log_person_deleted(
        self, security_context, person_id: UUID, person_data: Dict[str, Any]
    ):
        """Log person deletion/anonymization."""
        await self.audit_trail.log_event(
            action=AuditAction.DELETE,
            description=f"Person deleted/anonymized: {person_id}",
            user_id=security_context.user.user_id,
            username=security_context.user.username,
            user_role=security_context.user.role.value,
            ip_address=security_context.ip_address,
            user_agent=security_context.user_agent,
            request_id=security_context.request_id,
            resource_type="person",
            resource_id=person_id,
            old_values=person_data,
            data_subject_id=person_id,
            severity=AuditSeverity.WARNING,
            gdpr_lawful_basis="gdpr_article_17",
        )

    async def log_person_accessed(
        self, security_context, person_id: UUID, access_type: str = "view"
    ):
        """Log person data access."""
        await self.audit_trail.log_event(
            action=AuditAction.READ,
            description=f"Person data accessed: {access_type}",
            user_id=security_context.user.user_id,
            username=security_context.user.username,
            user_role=security_context.user.role.value,
            ip_address=security_context.ip_address,
            user_agent=security_context.user_agent,
            request_id=security_context.request_id,
            resource_type="person",
            resource_id=person_id,
            data_subject_id=person_id,
            gdpr_lawful_basis="legitimate_interest",
        )

    async def log_gdpr_export(self, security_context, person_id: UUID):
        """Log GDPR data export."""
        await self.audit_trail.log_event(
            action=AuditAction.EXPORT,
            description="GDPR data export requested",
            user_id=security_context.user.user_id,
            username=security_context.user.username,
            user_role=security_context.user.role.value,
            ip_address=security_context.ip_address,
            user_agent=security_context.user_agent,
            request_id=security_context.request_id,
            resource_type="person",
            resource_id=person_id,
            data_subject_id=person_id,
            severity=AuditSeverity.WARNING,
            gdpr_lawful_basis="gdpr_article_15",
        )

    async def log_access_denied(
        self,
        security_context,
        resource_type: str,
        resource_id: Optional[UUID],
        reason: str,
    ):
        """Log access denied attempts."""
        await self.audit_trail.log_event(
            action=AuditAction.ACCESS_DENIED,
            description=f"Access denied: {reason}",
            user_id=security_context.user.user_id,
            username=security_context.user.username,
            user_role=security_context.user.role.value,
            ip_address=security_context.ip_address,
            user_agent=security_context.user_agent,
            request_id=security_context.request_id,
            resource_type=resource_type,
            resource_id=resource_id,
            severity=AuditSeverity.WARNING,
        )

    async def log_user_login(
        self,
        user_id: UUID,
        username: str,
        ip_address: Optional[str],
        user_agent: Optional[str],
    ):
        """Log successful user login."""
        await self.audit_trail.log_event(
            action=AuditAction.LOGIN,
            description="User logged in successfully",
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="user",
            resource_id=user_id,
            severity=AuditSeverity.INFO,
        )

    async def log_user_logout(
        self,
        user_id: UUID,
        username: str,
        ip_address: Optional[str],
    ):
        """Log user logout."""
        await self.audit_trail.log_event(
            action=AuditAction.LOGOUT,
            description="User logged out",
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            resource_type="user",
            resource_id=user_id,
            severity=AuditSeverity.INFO,
        )

    async def log_user_created(
        self,
        user_id: UUID,
        username: str,
        role: str,
        ip_address: Optional[str],
    ):
        """Log new user registration."""
        await self.audit_trail.log_event(
            action=AuditAction.CREATE,
            description=f"New user account created with role: {role}",
            user_id=user_id,
            username=username,
            user_role=role,
            ip_address=ip_address,
            resource_type="user",
            resource_id=user_id,
            severity=AuditSeverity.INFO,
        )

    async def log_password_changed(
        self,
        user_id: UUID,
        username: str,
        ip_address: Optional[str],
    ):
        """Log password change event."""
        await self.audit_trail.log_event(
            action=AuditAction.UPDATE,
            description="User password changed",
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            resource_type="user",
            resource_id=user_id,
            severity=AuditSeverity.WARNING,
        )

    async def log_failed_login(
        self,
        username: str,
        ip_address: Optional[str],
        reason: str,
    ):
        """Log failed login attempt."""
        await self.audit_trail.log_event(
            action=AuditAction.ACCESS_DENIED,
            description=f"Failed login attempt: {reason}",
            username=username,
            ip_address=ip_address,
            resource_type="user",
            severity=AuditSeverity.WARNING,
        )


# Global audit logger instance
audit_logger = AuditLogger()
