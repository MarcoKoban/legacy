"""
Comprehensive tests for the audit trail system.
"""

import hashlib
import json
import unittest.mock
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from geneweb.api.security.audit import (
    AuditAction,
    AuditEvent,
    AuditLogger,
    AuditSeverity,
    AuditTrail,
    audit_logger,
)


class TestAuditEvent:
    """Test AuditEvent model validation and behavior."""

    def test_audit_event_creation_with_defaults(self):
        """Test audit event creation with minimal data."""
        event = AuditEvent(action=AuditAction.CREATE, description="Test event")

        assert event.action == AuditAction.CREATE
        assert event.description == "Test event"
        assert event.severity == AuditSeverity.INFO
        assert isinstance(event.id, UUID)
        assert isinstance(event.timestamp, datetime)

    def test_audit_event_creation_with_all_fields(self):
        """Test audit event creation with all fields populated."""
        user_id = uuid4()
        resource_id = uuid4()
        request_id = uuid4()
        data_subject_id = uuid4()

        event = AuditEvent(
            action=AuditAction.UPDATE,
            description="Full event test",
            severity=AuditSeverity.WARNING,
            user_id=user_id,
            username="testuser",
            user_role="admin",
            ip_address="192.168.1.1",
            user_agent="Test Agent",
            request_id=request_id,
            resource_type="person",
            resource_id=resource_id,
            old_values='{"name": "old"}',
            new_values='{"name": "new"}',
            gdpr_lawful_basis="consent",
            data_subject_id=data_subject_id,
            checksum="test_checksum",
            chain_hash="test_chain_hash",
            metadata='{"key": "value"}',
        )

        assert event.action == AuditAction.UPDATE
        assert event.severity == AuditSeverity.WARNING
        assert event.user_id == user_id
        assert event.username == "testuser"
        assert event.user_role == "admin"
        assert event.ip_address == "192.168.1.1"
        assert event.user_agent == "Test Agent"
        assert event.request_id == request_id
        assert event.resource_type == "person"
        assert event.resource_id == resource_id
        assert event.old_values == '{"name": "old"}'
        assert event.new_values == '{"name": "new"}'
        assert event.gdpr_lawful_basis == "consent"
        assert event.data_subject_id == data_subject_id
        assert event.checksum == "test_checksum"
        assert event.chain_hash == "test_chain_hash"
        assert event.metadata == '{"key": "value"}'

    def test_audit_action_enum_values(self):
        """Test all audit action enum values."""
        actions = [
            AuditAction.CREATE,
            AuditAction.READ,
            AuditAction.UPDATE,
            AuditAction.DELETE,
            AuditAction.ANONYMIZE,
            AuditAction.EXPORT,
            AuditAction.LOGIN,
            AuditAction.LOGOUT,
            AuditAction.CONSENT_GRANT,
            AuditAction.CONSENT_WITHDRAW,
            AuditAction.ACCESS_DENIED,
        ]

        for action in actions:
            event = AuditEvent(action=action, description="Test")
            assert event.action == action

    def test_audit_severity_enum_values(self):
        """Test all audit severity enum values."""
        severities = [
            AuditSeverity.INFO,
            AuditSeverity.WARNING,
            AuditSeverity.ERROR,
            AuditSeverity.CRITICAL,
        ]

        for severity in severities:
            event = AuditEvent(
                action=AuditAction.CREATE, description="Test", severity=severity
            )
            assert event.severity == severity


class TestAuditTrail:
    """Test AuditTrail functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch("geneweb.api.security.audit.settings") as mock_settings:
            mock_settings.security.secret_key = "test-secret-key"
            self.audit_trail = AuditTrail()

    def test_audit_trail_initialization(self):
        """Test audit trail initialization."""
        assert self.audit_trail.secret_key == b"test-secret-key"
        assert self.audit_trail._last_hash is None

    def test_generate_checksum(self):
        """Test checksum generation for audit events."""
        event = AuditEvent(
            action=AuditAction.CREATE,
            description="Test event",
            user_id=uuid4(),
            resource_type="person",
            resource_id=uuid4(),
        )

        checksum = self.audit_trail._generate_checksum(event)

        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA256 hex digest length

        # Test checksum consistency
        checksum2 = self.audit_trail._generate_checksum(event)
        assert checksum == checksum2

    def test_generate_checksum_different_events(self):
        """Test that different events generate different checksums."""
        event1 = AuditEvent(action=AuditAction.CREATE, description="Event 1")
        event2 = AuditEvent(action=AuditAction.UPDATE, description="Event 2")

        checksum1 = self.audit_trail._generate_checksum(event1)
        checksum2 = self.audit_trail._generate_checksum(event2)

        assert checksum1 != checksum2

    def test_generate_chain_hash_first_event(self):
        """Test chain hash generation for first event."""
        checksum = "test_checksum"

        chain_hash = self.audit_trail._generate_chain_hash(checksum)

        expected_data = f"genesis_{checksum}"
        expected_hash = hashlib.sha256(expected_data.encode("utf-8")).hexdigest()

        assert chain_hash == expected_hash

    def test_generate_chain_hash_subsequent_event(self):
        """Test chain hash generation for subsequent events."""
        self.audit_trail._last_hash = "previous_hash"
        checksum = "test_checksum"

        chain_hash = self.audit_trail._generate_chain_hash(checksum)

        expected_data = f"previous_hash_{checksum}"
        expected_hash = hashlib.sha256(expected_data.encode("utf-8")).hexdigest()

        assert chain_hash == expected_hash

    def test_encrypt_data_changes_none(self):
        """Test encryption with None data."""
        result = self.audit_trail._encrypt_data_changes(None)
        assert result is None

    @patch("geneweb.api.security.audit.encrypt_json_data")
    def test_encrypt_data_changes_with_sensitive_data(self, mock_encrypt):
        """Test encryption of sensitive data fields."""
        mock_encrypt.return_value = "encrypted_data"

        data = {
            "first_name": "John",  # Non-sensitive
            "last_name": "Doe",  # Non-sensitive
            "birth_date": "1990-01-01",  # Sensitive
            "email": "john@example.com",  # Sensitive
            "notes": "Private notes",  # Sensitive
        }

        result = self.audit_trail._encrypt_data_changes(data)
        result_json = json.loads(result)

        # Non-sensitive data should be preserved
        assert result_json["first_name"] == "John"
        assert result_json["last_name"] == "Doe"

        # Sensitive data should be encrypted
        assert result_json["_encrypted_sensitive"] == "encrypted_data"
        assert "birth_date" not in result_json
        assert "email" not in result_json
        assert "notes" not in result_json

        # Verify encrypt_json_data was called with sensitive data
        mock_encrypt.assert_called_once_with(
            {
                "birth_date": "1990-01-01",
                "email": "john@example.com",
                "notes": "Private notes",
            }
        )

    def test_encrypt_data_changes_no_sensitive_data(self):
        """Test encryption with no sensitive data."""
        data = {"first_name": "John", "last_name": "Doe", "id": "123"}

        result = self.audit_trail._encrypt_data_changes(data)
        result_json = json.loads(result)

        assert result_json == data
        assert "_encrypted_sensitive" not in result_json

    @pytest.mark.asyncio
    @patch("geneweb.api.security.audit.logger")
    async def test_log_event_minimal(self, mock_logger):
        """Test logging minimal audit event."""
        with patch.object(
            self.audit_trail, "_store_audit_event", new_callable=AsyncMock
        ) as mock_store:
            event = await self.audit_trail.log_event(
                action=AuditAction.CREATE, description="Test event"
            )

            assert event.action == AuditAction.CREATE
            assert event.description == "Test event"
            assert event.severity == AuditSeverity.INFO
            assert event.checksum is not None
            assert event.chain_hash is not None
            assert self.audit_trail._last_hash == event.chain_hash

            # Verify logging
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert call_args[0][0] == "Audit event"

            # Verify storage
            mock_store.assert_called_once_with(event)

    @pytest.mark.asyncio
    @patch("geneweb.api.security.audit.logger")
    @patch("geneweb.api.security.audit.encrypt_json_data")
    async def test_log_event_complete(self, mock_encrypt, mock_logger):
        """Test logging complete audit event with all fields."""
        mock_encrypt.return_value = "encrypted_metadata"

        user_id = uuid4()
        resource_id = uuid4()
        request_id = uuid4()
        data_subject_id = uuid4()

        old_values = {"name": "old"}
        new_values = {"name": "new"}
        metadata = {"key": "value"}

        with patch.object(
            self.audit_trail, "_store_audit_event", new_callable=AsyncMock
        ):
            event = await self.audit_trail.log_event(
                action=AuditAction.UPDATE,
                description="Complete test event",
                user_id=user_id,
                username="testuser",
                user_role="admin",
                ip_address="192.168.1.1",
                user_agent="Test Agent",
                request_id=request_id,
                resource_type="person",
                resource_id=resource_id,
                old_values=old_values,
                new_values=new_values,
                severity=AuditSeverity.WARNING,
                gdpr_lawful_basis="consent",
                data_subject_id=data_subject_id,
                metadata=metadata,
            )

            assert event.action == AuditAction.UPDATE
            assert event.description == "Complete test event"
            assert event.severity == AuditSeverity.WARNING
            assert event.user_id == user_id
            assert event.username == "testuser"
            assert event.user_role == "admin"
            assert event.ip_address == "192.168.1.1"
            assert event.user_agent == "Test Agent"
            assert event.request_id == request_id
            assert event.resource_type == "person"
            assert event.resource_id == resource_id
            assert event.gdpr_lawful_basis == "consent"
            assert event.data_subject_id == data_subject_id
            assert event.checksum is not None
            assert event.chain_hash is not None
            assert event.old_values is not None
            assert event.new_values is not None
            assert event.metadata == "encrypted_metadata"

    def test_verify_event_integrity_valid(self):
        """Test event integrity verification with valid checksum."""
        event = AuditEvent(action=AuditAction.CREATE, description="Test event")

        # Generate valid checksum
        event.checksum = self.audit_trail._generate_checksum(event)

        assert self.audit_trail.verify_event_integrity(event) is True

    def test_verify_event_integrity_invalid(self):
        """Test event integrity verification with invalid checksum."""
        event = AuditEvent(
            action=AuditAction.CREATE,
            description="Test event",
            checksum="invalid_checksum",
        )

        assert self.audit_trail.verify_event_integrity(event) is False

    def test_verify_event_integrity_none_checksum(self):
        """Test event integrity verification with None checksum."""
        event = AuditEvent(
            action=AuditAction.CREATE, description="Test event", checksum=None
        )

        assert self.audit_trail.verify_event_integrity(event) is False

    @patch("geneweb.api.security.audit.logger")
    def test_verify_event_integrity_exception(self, mock_logger):
        """Test event integrity verification with exception."""
        event = AuditEvent(action=AuditAction.CREATE, description="Test event")

        # Corrupt the event to cause an exception
        event.timestamp = "invalid_timestamp"

        result = self.audit_trail.verify_event_integrity(event)

        assert result is False
        mock_logger.error.assert_called_once_with(
            "Audit integrity verification failed", error=unittest.mock.ANY
        )

    @pytest.mark.asyncio
    async def test_get_audit_trail_placeholder(self):
        """Test get_audit_trail placeholder implementation."""
        result = await self.audit_trail.get_audit_trail()
        assert result == []

    @pytest.mark.asyncio
    @patch("geneweb.api.security.audit.decrypt_json_data")
    @patch.object(AuditTrail, "get_audit_trail")
    async def test_export_gdpr_audit_trail(self, mock_get_trail, mock_decrypt):
        """Test GDPR audit trail export."""
        data_subject_id = uuid4()

        # Mock events with encrypted data
        event1 = AuditEvent(
            action=AuditAction.CREATE,
            description="Event 1",
            old_values='{"name": "old", "_encrypted_sensitive": "encrypted1"}',
            new_values='{"name": "new", "_encrypted_sensitive": "encrypted2"}',
        )

        event2 = AuditEvent(
            action=AuditAction.UPDATE,
            description="Event 2",
            old_values='{"id": "123"}',
            new_values='{"id": "456"}',
        )

        mock_get_trail.return_value = [event1, event2]
        mock_decrypt.side_effect = [
            {"birth_date": "1990-01-01"},
            {"birth_date": "1991-01-01"},
        ]

        with patch.object(
            self.audit_trail, "verify_event_integrity", return_value=True
        ):
            result = await self.audit_trail.export_gdpr_audit_trail(data_subject_id)

        assert result["data_subject_id"] == str(data_subject_id)
        assert result["total_events"] == 2
        assert result["integrity_verified"] is True
        assert len(result["events"]) == 2

        # Check first event decryption
        event1_data = result["events"][0]
        assert event1_data["old_values"]["name"] == "old"
        assert event1_data["old_values"]["birth_date"] == "1990-01-01"
        assert "_encrypted_sensitive" not in event1_data["old_values"]

        # Check second event (no encryption)
        event2_data = result["events"][1]
        assert event2_data["old_values"]["id"] == "123"


class TestAuditLogger:
    """Test AuditLogger high-level interface."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch("geneweb.api.security.audit.settings") as mock_settings:
            mock_settings.security.secret_key = "test-secret-key"
            self.audit_logger = AuditLogger()

        # Mock security context
        self.security_context = MagicMock()
        self.security_context.user.user_id = uuid4()
        self.security_context.user.username = "testuser"
        self.security_context.user.role.value = "admin"
        self.security_context.ip_address = "192.168.1.1"
        self.security_context.user_agent = "Test Agent"
        self.security_context.request_id = uuid4()

    @pytest.mark.asyncio
    async def test_log_person_created(self):
        """Test person creation logging."""
        person_id = uuid4()
        person_data = {
            "first_name": "John",
            "last_name": "Doe",
            "birth_date": "1990-01-01",
        }

        with patch.object(
            self.audit_logger.audit_trail, "log_event", new_callable=AsyncMock
        ) as mock_log:
            await self.audit_logger.log_person_created(
                self.security_context, person_id, person_data
            )

            mock_log.assert_called_once()
            call_kwargs = mock_log.call_args.kwargs

            assert call_kwargs["action"] == AuditAction.CREATE
            assert "Person created" in call_kwargs["description"]
            assert call_kwargs["user_id"] == self.security_context.user.user_id
            assert call_kwargs["resource_type"] == "person"
            assert call_kwargs["resource_id"] == person_id
            assert call_kwargs["new_values"] == person_data
            assert call_kwargs["data_subject_id"] == person_id
            assert call_kwargs["gdpr_lawful_basis"] == "consent"

    @pytest.mark.asyncio
    async def test_log_person_updated(self):
        """Test person update logging."""
        person_id = uuid4()
        old_data = {"name": "Old Name"}
        new_data = {"name": "New Name"}

        with patch.object(
            self.audit_logger.audit_trail, "log_event", new_callable=AsyncMock
        ) as mock_log:
            await self.audit_logger.log_person_updated(
                self.security_context, person_id, old_data, new_data
            )

            mock_log.assert_called_once()
            call_kwargs = mock_log.call_args.kwargs

            assert call_kwargs["action"] == AuditAction.UPDATE
            assert call_kwargs["resource_type"] == "person"
            assert call_kwargs["resource_id"] == person_id
            assert call_kwargs["old_values"] == old_data
            assert call_kwargs["new_values"] == new_data
            assert call_kwargs["gdpr_lawful_basis"] == "legitimate_interest"

    @pytest.mark.asyncio
    async def test_log_person_deleted(self):
        """Test person deletion logging."""
        person_id = uuid4()
        person_data = {"name": "Deleted Person"}

        with patch.object(
            self.audit_logger.audit_trail, "log_event", new_callable=AsyncMock
        ) as mock_log:
            await self.audit_logger.log_person_deleted(
                self.security_context, person_id, person_data
            )

            mock_log.assert_called_once()
            call_kwargs = mock_log.call_args.kwargs

            assert call_kwargs["action"] == AuditAction.DELETE
            assert call_kwargs["severity"] == AuditSeverity.WARNING
            assert call_kwargs["resource_type"] == "person"
            assert call_kwargs["resource_id"] == person_id
            assert call_kwargs["old_values"] == person_data
            assert call_kwargs["gdpr_lawful_basis"] == "gdpr_article_17"

    @pytest.mark.asyncio
    async def test_log_person_accessed(self):
        """Test person access logging."""
        person_id = uuid4()

        with patch.object(
            self.audit_logger.audit_trail, "log_event", new_callable=AsyncMock
        ) as mock_log:
            await self.audit_logger.log_person_accessed(
                self.security_context, person_id, "detailed_view"
            )

            mock_log.assert_called_once()
            call_kwargs = mock_log.call_args.kwargs

            assert call_kwargs["action"] == AuditAction.READ
            assert "detailed_view" in call_kwargs["description"]
            assert call_kwargs["resource_type"] == "person"
            assert call_kwargs["resource_id"] == person_id
            assert call_kwargs["data_subject_id"] == person_id

    @pytest.mark.asyncio
    async def test_log_gdpr_export(self):
        """Test GDPR export logging."""
        person_id = uuid4()

        with patch.object(
            self.audit_logger.audit_trail, "log_event", new_callable=AsyncMock
        ) as mock_log:
            await self.audit_logger.log_gdpr_export(self.security_context, person_id)

            mock_log.assert_called_once()
            call_kwargs = mock_log.call_args.kwargs

            assert call_kwargs["action"] == AuditAction.EXPORT
            assert call_kwargs["severity"] == AuditSeverity.WARNING
            assert call_kwargs["resource_type"] == "person"
            assert call_kwargs["resource_id"] == person_id
            assert call_kwargs["gdpr_lawful_basis"] == "gdpr_article_15"

    @pytest.mark.asyncio
    async def test_log_access_denied(self):
        """Test access denied logging."""
        resource_id = uuid4()

        with patch.object(
            self.audit_logger.audit_trail, "log_event", new_callable=AsyncMock
        ) as mock_log:
            await self.audit_logger.log_access_denied(
                self.security_context, "person", resource_id, "Insufficient permissions"
            )

            mock_log.assert_called_once()
            call_kwargs = mock_log.call_args.kwargs

            assert call_kwargs["action"] == AuditAction.ACCESS_DENIED
            assert call_kwargs["severity"] == AuditSeverity.WARNING
            assert "Insufficient permissions" in call_kwargs["description"]
            assert call_kwargs["resource_type"] == "person"
            assert call_kwargs["resource_id"] == resource_id


class TestGlobalAuditLogger:
    """Test global audit logger instance."""

    def test_global_audit_logger_instance(self):
        """Test that global audit logger is available."""
        assert audit_logger is not None
        assert isinstance(audit_logger, AuditLogger)
        assert hasattr(audit_logger, "audit_trail")


class TestIntegrationScenarios:
    """Test integration scenarios for audit system."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch("geneweb.api.security.audit.settings") as mock_settings:
            mock_settings.security.secret_key = "test-secret-key"
            self.audit_trail = AuditTrail()

    @pytest.mark.asyncio
    async def test_audit_chain_integrity(self):
        """Test audit event chain integrity."""
        with patch.object(
            self.audit_trail, "_store_audit_event", new_callable=AsyncMock
        ):
            # Log first event
            event1 = await self.audit_trail.log_event(
                action=AuditAction.CREATE, description="First event"
            )

            # Log second event
            event2 = await self.audit_trail.log_event(
                action=AuditAction.UPDATE, description="Second event"
            )

            # Verify chain linking
            assert event1.chain_hash != event2.chain_hash
            assert self.audit_trail._last_hash == event2.chain_hash

            # Verify integrity
            assert self.audit_trail.verify_event_integrity(event1)
            assert self.audit_trail.verify_event_integrity(event2)

    @pytest.mark.asyncio
    async def test_complete_person_lifecycle_audit(self):
        """Test complete person lifecycle audit trail."""
        person_id = uuid4()
        security_context = MagicMock()
        security_context.user.user_id = uuid4()
        security_context.user.username = "testuser"
        security_context.user.role.value = "admin"
        security_context.ip_address = "192.168.1.1"
        security_context.user_agent = "Test Agent"
        security_context.request_id = uuid4()

        audit_logger_instance = AuditLogger()

        with patch.object(
            audit_logger_instance.audit_trail,
            "_store_audit_event",
            new_callable=AsyncMock,
        ):
            # Person creation
            await audit_logger_instance.log_person_created(
                security_context, person_id, {"name": "John Doe"}
            )

            # Person access
            await audit_logger_instance.log_person_accessed(security_context, person_id)

            # Person update
            await audit_logger_instance.log_person_updated(
                security_context,
                person_id,
                {"name": "John Doe"},
                {"name": "John Smith"},
            )

            # GDPR export
            await audit_logger_instance.log_gdpr_export(security_context, person_id)

            # Person deletion
            await audit_logger_instance.log_person_deleted(
                security_context, person_id, {"name": "John Smith"}
            )

            # Verify chain state is maintained
            assert audit_logger_instance.audit_trail._last_hash is not None

    @pytest.mark.asyncio
    async def test_timestamp_consistency(self):
        """Test timestamp consistency in audit events."""
        with patch.object(
            self.audit_trail, "_store_audit_event", new_callable=AsyncMock
        ):
            event = await self.audit_trail.log_event(
                action=AuditAction.CREATE, description="Timestamp test"
            )

            # Verify timestamp is recent (within last few seconds)
            # Make sure both datetimes are timezone-aware for comparison
            current_time = datetime.now(timezone.utc)
            event_time = event.timestamp
            if event_time.tzinfo is None:
                event_time = event_time.replace(tzinfo=timezone.utc)

            time_diff = current_time - event_time
            assert time_diff.total_seconds() < 5
