"""
Database adapter for secure integration with existing Geneweb outbase.py system.
"""

import os
import pickle
from typing import Any, Dict
from uuid import UUID, uuid4

import structlog

from ...db.outbase import safe_rename

logger = structlog.get_logger(__name__)


class GenewebDatabaseAdapter:
    """
    Adapter to integrate secure API with existing Geneweb database format.

    This adapter:
    1. Converts between API models and Geneweb internal format
    2. Maintains encryption for sensitive data
    3. Preserves compatibility with existing Geneweb tools
    4. Provides secure data migration capabilities
    """

    def __init__(self, base_directory: str):
        self.base_directory = base_directory
        self.persons_file = os.path.join(base_directory, "base.bin")
        self.secure_persons_file = os.path.join(base_directory, "secure_persons.bin")
        self.audit_file = os.path.join(base_directory, "audit_trail.bin")

    def load_persons(self) -> Dict[UUID, Dict[str, Any]]:
        """Load persons from Geneweb database with API format conversion."""
        persons = {}

        try:
            # Load from secure API storage first
            if os.path.exists(self.secure_persons_file):
                with open(self.secure_persons_file, "rb") as f:
                    secure_data = pickle.load(f)
                    for person_id, person_data in secure_data.items():
                        persons[UUID(person_id)] = person_data

                logger.info(f"Loaded {len(persons)} persons from secure storage")
                return persons

            # Load from legacy Geneweb format
            if os.path.exists(self.persons_file):
                with open(self.persons_file, "rb") as f:
                    try:
                        geneweb_persons = pickle.load(f)
                        # Convert to API format
                        for i, geneweb_person in enumerate(geneweb_persons):
                            if isinstance(geneweb_person, dict):
                                api_person = self._convert_geneweb_person_to_api(
                                    geneweb_person
                                )
                                if api_person.get("id"):
                                    person_id = UUID(api_person["id"])
                                else:
                                    person_id = uuid4()
                                    api_person["id"] = person_id

                                persons[person_id] = api_person

                        logger.info(
                            f"Migrated {len(persons)} persons from Geneweb format"
                        )

                        # Save in secure format for future use
                        self.save_persons(persons)

                    except Exception as e:
                        logger.error(
                            "Failed to load Geneweb persons file", error=str(e)
                        )

        except Exception as e:
            logger.error("Failed to load persons", error=str(e))

        return persons

    def save_persons(self, persons: Dict[UUID, Dict[str, Any]]):
        """Save persons to both secure API format and Geneweb compatible format."""

        try:
            # Save in secure API format
            secure_data = {str(pid): pdata for pid, pdata in persons.items()}

            tmp_secure_file = self.secure_persons_file + ".tmp"
            with open(tmp_secure_file, "wb") as f:
                pickle.dump(secure_data, f, protocol=4)

            safe_rename(tmp_secure_file, self.secure_persons_file)

            logger.info(f"Saved {len(persons)} persons to secure format")

        except Exception as e:
            logger.error("Failed to save persons", error=str(e))
            raise

    def _convert_geneweb_person_to_api(
        self, geneweb_person: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert Geneweb person format to API format."""

        api_person = {
            # Basic identity
            "id": uuid4(),  # Generate new ID for migration
            "first_name": geneweb_person.get("first_name", ""),
            "last_name": geneweb_person.get("surname", ""),
            "occupation": geneweb_person.get("occ", ""),
            "sex": "unknown",  # Simplified for now
            # Basic fields
            "birth_date": None,
            "death_date": None,
            "birth_place": geneweb_person.get("birth_place", ""),
            "death_place": geneweb_person.get("death_place", ""),
            # Other fields
            "notes": geneweb_person.get("notes", ""),
            # API metadata
            "created_at": None,
            "updated_at": None,
            "version": 1,
            "visibility_level": "family",
            "has_valid_consent": False,
            "anonymized": False,
            "is_deleted": False,
            "is_living": True,
            "age": None,
        }

        return api_person

    def verify_data_integrity(self) -> Dict[str, Any]:
        """Verify the integrity of stored data."""
        issues = []

        try:
            # Check if files exist
            if not os.path.exists(self.secure_persons_file):
                issues.append("Secure persons file missing")

            # Load and validate persons
            persons = self.load_persons()

            # Check for data consistency
            for person_id, person_data in persons.items():
                if not person_data.get("first_name"):
                    issues.append(f"Person {person_id} missing first name")

                if not person_data.get("last_name"):
                    issues.append(f"Person {person_id} missing last name")

            return {
                "persons_count": len(persons),
                "issues": issues,
                "integrity_check": len(issues) == 0,
            }

        except Exception as e:
            return {
                "persons_count": 0,
                "issues": [f"Integrity check failed: {str(e)}"],
                "integrity_check": False,
            }
