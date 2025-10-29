"""
GDPR compliance endpoints for person data management.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from ..models.person import (
    PersonAnonymizationRequest,
    PersonConsentUpdate,
    PersonGDPRExport,
)
from ..security.audit import audit_logger
from ..security.auth import Permission, SecurityContext
from ..security.encryption import GDPRAnonymizer
from ..services.person_service import PersonService
from .persons import get_security_context

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/persons", tags=["gdpr"])


@router.get("/{person_id}/gdpr-export", response_model=PersonGDPRExport)
async def export_person_data(
    person_id: UUID,
    security_context: SecurityContext = Depends(get_security_context),
    person_service: PersonService = Depends(),
) -> PersonGDPRExport:
    """
    Export complete person data for GDPR Article 15 (Right of Access).

    - **GDPR Article 15**: Complete data export including processing activities
    - **Security**: Enhanced audit logging for data export requests
    - **Format**: Machine-readable JSON with full transparency
    """
    # Check permissions - users can export their own data or admins can export any
    if security_context.user.role.value not in ["admin", "editor"]:
        if person_id != security_context.user.family_person_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only export own personal data",
            )

    security_context.require_permission(Permission.EXPORT_PERSON_DATA)

    try:
        # Get complete person data including encrypted fields
        person_data = await person_service.get_person_complete(
            person_id=person_id,
            security_context=security_context,
            decrypt_sensitive=True,  # Decrypt for export
        )

        if not person_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
            )

        # Get audit trail for this person
        audit_trail = await audit_logger.audit_trail.export_gdpr_audit_trail(person_id)

        # Get GDPR consent history
        consent_history = await person_service.get_consent_history(person_id)

        # Create comprehensive export
        export_data = PersonGDPRExport(
            person_data=person_data,
            audit_logs=audit_trail.get("events", []),
            gdpr_consents=consent_history,
            export_requested_by=security_context.user.user_id,
            lawful_basis="gdpr_article_15",
            data_retention_period="As per genealogy research requirements",
            third_party_processors=["None"],
        )

        # Log the export request
        await audit_logger.log_gdpr_export(
            security_context=security_context, person_id=person_id
        )

        logger.warning(
            "GDPR data export completed",
            person_id=str(person_id),
            requested_by=str(security_context.user.user_id),
            ip_address=security_context.ip_address,
            export_size=len(str(export_data)),
        )

        return export_data

    except Exception as e:
        logger.error(
            "GDPR export failed",
            error=str(e),
            person_id=str(person_id),
            user_id=str(security_context.user.user_id),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export person data",
        )


@router.post("/{person_id}/anonymize", status_code=status.HTTP_200_OK)
async def anonymize_person(
    person_id: UUID,
    anonymization_request: PersonAnonymizationRequest,
    security_context: SecurityContext = Depends(get_security_context),
    person_service: PersonService = Depends(),
) -> Dict[str, Any]:
    """
    Anonymize person data for GDPR Article 17 (Right to be Forgotten).

    - **GDPR Article 17**: Irreversible anonymization of personal data
    - **Security**: Admin-only operation with comprehensive audit trail
    - **Legal**: Maintains statistical data while removing identifiable information
    """
    # Only admins can anonymize data
    security_context.require_permission(Permission.ANONYMIZE_PERSON)

    # Validate the request
    if anonymization_request.person_id != person_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Person ID mismatch"
        )

    if not anonymization_request.confirm_irreversible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must confirm that anonymization is irreversible",
        )

    try:
        # Get current person data for audit
        person_data = await person_service.get_person_complete(
            person_id=person_id,
            security_context=security_context,
            decrypt_sensitive=True,
        )

        if not person_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
            )

        if person_data.anonymized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Person already anonymized",
            )

        # Perform anonymization
        anonymization_hash = GDPRAnonymizer.get_anonymization_hash(str(person_id))

        anonymized_data = GDPRAnonymizer.anonymize_person_data(person_data.dict())
        anonymized_data.update(
            {
                "anonymized": True,
                "anonymized_at": datetime.now(timezone.utc),
                "anonymization_hash": anonymization_hash,
                "anonymization_reason": anonymization_request.reason,
                "anonymized_by": security_context.user.user_id,
            }
        )

        # Update person with anonymized data
        await person_service.anonymize_person(
            person_id=person_id,
            anonymized_data=anonymized_data,
            security_context=security_context,
        )

        # Log anonymization
        await audit_logger.audit_trail.log_event(
            action=audit_logger.audit_trail.AuditAction.ANONYMIZE,
            description=f"Person anonymized: {anonymization_request.reason}",
            user_id=security_context.user.user_id,
            username=security_context.user.username,
            user_role=security_context.user.role.value,
            ip_address=security_context.ip_address,
            user_agent=security_context.user_agent,
            request_id=security_context.request_id,
            resource_type="person",
            resource_id=person_id,
            old_values=person_data.dict(),
            new_values=anonymized_data,
            data_subject_id=person_id,
            gdpr_lawful_basis=anonymization_request.legal_basis,
            severity=audit_logger.audit_trail.AuditSeverity.CRITICAL,
        )

        logger.critical(
            "Person anonymized under GDPR Article 17",
            person_id=str(person_id),
            anonymized_by=str(security_context.user.user_id),
            reason=anonymization_request.reason,
            anonymization_hash=anonymization_hash,
            ip_address=security_context.ip_address,
        )

        return {
            "message": "Person successfully anonymized",
            "person_id": str(person_id),
            "anonymization_hash": anonymization_hash,
            "anonymized_at": anonymized_data["anonymized_at"].isoformat(),
            "irreversible": True,
            "gdpr_article": "Article 17 - Right to be forgotten",
        }

    except Exception as e:
        logger.error(
            "Anonymization failed",
            error=str(e),
            person_id=str(person_id),
            user_id=str(security_context.user.user_id),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to anonymize person data",
        )


@router.post("/{person_id}/consent", status_code=status.HTTP_200_OK)
async def update_consent(
    person_id: UUID,
    consent_update: PersonConsentUpdate,
    security_context: SecurityContext = Depends(get_security_context),
    person_service: PersonService = Depends(),
) -> Dict[str, Any]:
    """
    Update GDPR consent for person data processing.

    - **GDPR**: Consent management for lawful data processing
    - **Audit**: All consent changes logged with IP and timestamp
    - **Granular**: Specific consent for different processing purposes
    """
    # Check permissions - users can manage their own consent or family members
    if security_context.user.role.value not in ["admin", "editor"]:
        if person_id != security_context.user.family_person_id:
            security_context.require_person_access(person_id, Permission.MANAGE_CONSENT)

    security_context.require_permission(Permission.MANAGE_CONSENT)

    try:
        # Validate person exists
        person = await person_service.get_person(person_id, security_context)
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
            )

        # Update consent with audit trail
        updated_consents = await person_service.update_consent(
            person_id=person_id,
            consents=consent_update.consents,
            updated_by=security_context.user.user_id,
            ip_address=security_context.ip_address,
            user_agent=security_context.user_agent,
        )

        # Log consent changes
        for consent in consent_update.consents:
            await audit_logger.audit_trail.log_event(
                action=(
                    audit_logger.audit_trail.AuditAction.CONSENT_GRANT
                    if consent.status.value == "granted"
                    else audit_logger.audit_trail.AuditAction.CONSENT_WITHDRAW
                ),
                description=f"Consent {consent.status.value} for {consent.purpose}",
                user_id=security_context.user.user_id,
                username=security_context.user.username,
                user_role=security_context.user.role.value,
                ip_address=security_context.ip_address,
                user_agent=security_context.user_agent,
                request_id=security_context.request_id,
                resource_type="person_consent",
                resource_id=person_id,
                data_subject_id=person_id,
                gdpr_lawful_basis="consent",
                metadata={
                    "consent_purpose": consent.purpose,
                    "consent_status": consent.status.value,
                },
            )

        logger.info(
            "GDPR consent updated",
            person_id=str(person_id),
            updated_by=str(security_context.user.user_id),
            consent_count=len(consent_update.consents),
            ip_address=security_context.ip_address,
        )

        return {
            "message": "Consent updated successfully",
            "person_id": str(person_id),
            "updated_consents": len(updated_consents),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(
            "Consent update failed",
            error=str(e),
            person_id=str(person_id),
            user_id=str(security_context.user.user_id),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update consent",
        )


@router.get("/{person_id}/data-processing-info")
async def get_data_processing_info(
    person_id: UUID, security_context: SecurityContext = Depends(get_security_context)
) -> Dict[str, Any]:
    """
    Get information about how person data is processed (GDPR transparency).

    - **GDPR Article 13/14**: Information about data processing
    - **Transparency**: Clear information about purposes and legal basis
    - **Rights**: Information about data subject rights
    """
    # Users can see processing info for their own data
    if security_context.user.role.value not in ["admin", "editor"]:
        if person_id != security_context.user.family_person_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only view own data processing information",
            )

    return {
        "data_controller": {
            "name": "Geneweb Genealogy System",
            "contact": "privacy@geneweb.org",
            "dpo_contact": "dpo@geneweb.org",
        },
        "processing_purposes": [
            {
                "purpose": "Genealogy research and family tree construction",
                "lawful_basis": "Legitimate interest",
                "description": (
                    "Building and maintaining family relationships "
                    "and historical records"
                ),
            },
            {
                "purpose": "Data sharing with family members",
                "lawful_basis": "Consent",
                "description": (
                    "Sharing genealogy information with " "authorized family members"
                ),
            },
        ],
        "data_categories": [
            "Basic identity (name, sex)",
            "Life events (birth, death, marriage)",
            "Family relationships",
            "Contact information (if provided)",
            "User activity logs",
        ],
        "retention_period": (
            "Data is retained for genealogical research purposes. "
            "Personal data can be anonymized upon request."
        ),
        "third_parties": "None - data is not shared with third parties",
        "your_rights": [
            "Right of access (Article 15) - Request copy of your data",
            "Right of rectification (Article 16) - Correct inaccurate data",
            "Right to erasure (Article 17) - Request anonymization",
            "Right to data portability (Article 20) - Export your data",
            "Right to object (Article 21) - Object to processing",
        ],
        "automated_decision_making": "None",
        "data_protection_measures": [
            "AES-256 encryption for sensitive data",
            "Role-based access control",
            "Comprehensive audit logging",
            "Regular security assessments",
        ],
    }
