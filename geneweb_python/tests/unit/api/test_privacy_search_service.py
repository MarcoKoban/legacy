"""
Tests for PrivacyAwareSearch service - Core functionality.

Tests the essential privacy protection logic:
- Living person detection (règle des 100 ans)
- Privacy level determination
- Data anonymization at different levels
- Edge cases handling
- RGPD compliance

Note: Full integration tests with search_persons() will be in test_search_endpoints.py
"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from geneweb.api.models.search import PrivacyLevel
from geneweb.api.services.privacy_search import PrivacyAwareSearch
from geneweb.core.person import Person
from geneweb.db.database import Database


class TestLivingPersonDetection:
    """Test living person detection logic (règle des 100 ans)."""

    @pytest.fixture
    def service(self):
        """Create service with mock database."""
        db = Mock(spec=Database)
        return PrivacyAwareSearch(db)

    def test_person_with_death_date_not_living(self, service):
        """Person with death date should not be living."""
        person = Mock(spec=Person)
        person.birth = None
        person.death = Mock()
        person.death.date = "1990-08-20"

        assert service.is_person_living(person) is False

    def test_person_without_birth_date_considered_living(self, service):
        person = Mock(spec=Person)
        person.birth = None
        person.death = None

        assert service.is_person_living(person) is True

    def test_young_person_without_death_living(self, service):
        """Young person without death date should be living."""
        person = Mock(spec=Person)
        person.birth = Mock()
        person.birth.date = "2000-01-01"
        person.death = None

        assert service.is_person_living(person) is True

    def test_old_person_over_100_not_living(self, service):
        person = Mock(spec=Person)
        person.birth = Mock()
        person.birth.date = "1910-01-01"  # 115 years old in 2025
        person.death = None

        assert service.is_person_living(person) is False

    def test_person_at_100_years_boundary(self, service):
        """Test person exactly at 100 years boundary."""
        current_year = datetime.now().year
        birth_year = current_year - 100

        person = Mock(spec=Person)
        person.birth = Mock()
        person.birth.date = f"{birth_year}-01-01"
        person.death = None

        # Should not be living (age >= 100)
        assert service.is_person_living(person) is False

    def test_person_with_invalid_birth_date(self, service):
        """Test handling person with invalid birth date."""
        person = Mock(spec=Person)
        person.birth = Mock()
        person.birth.date = "invalid"
        person.death = None

        # Should handle gracefully and consider living (conservative)
        is_living = service.is_person_living(person)
        assert is_living is True


class TestPrivacyLevelDetermination:
    """Test privacy level determination (RGPD compliance)."""

    @pytest.fixture
    def service(self):
        """Create service with mock database."""
        db = Mock(spec=Database)
        return PrivacyAwareSearch(db)

    def test_deceased_person_public(self, service):
        """Deceased person should have PUBLIC privacy level."""
        person = Mock(spec=Person)
        person.birth = Mock()
        person.birth.date = "1920-01-01"
        person.death = Mock()
        person.death.date = "1990-01-01"

        level = service.get_privacy_level(person, None)
        assert level == PrivacyLevel.PUBLIC

    def test_living_person_without_user_anonymized(self, service):
        person = Mock(spec=Person)
        person.birth = Mock()
        person.birth.date = "2000-01-01"
        person.death = None

        level = service.get_privacy_level(person, None)
        assert level == PrivacyLevel.ANONYMIZED

    def test_living_person_with_user_protected(self, service):
        """Living person with user auth should have protection level."""
        person = Mock(spec=Person)
        person.birth = Mock()
        person.birth.date = "2000-01-01"
        person.death = None

        level = service.get_privacy_level(person, "user_123")
        # Currently returns ANONYMIZED, could be RESTRICTED with family authorization
        assert level in [PrivacyLevel.RESTRICTED, PrivacyLevel.ANONYMIZED]

    def test_old_person_treated_as_deceased(self, service):
        """Person >100 years should be treated as deceased (PUBLIC)."""
        person = Mock(spec=Person)
        person.birth = Mock()
        person.birth.date = "1910-01-01"
        person.death = None

        level = service.get_privacy_level(person, None)
        assert level == PrivacyLevel.PUBLIC


class TestDataAnonymization:
    """Test data anonymization at different privacy levels (RGPD Articles 5, 9)."""

    @pytest.fixture
    def service(self):
        """Create service with mock database."""
        db = Mock(spec=Database)
        return PrivacyAwareSearch(db)

    def test_public_level_no_anonymization(self, service):
        """PUBLIC level should not anonymize data (deceased persons)."""
        person = Mock(spec=Person)
        person.key = "p1"
        person.first_name = "Jean"
        person.surname = "Dupont"
        person.sex = Mock()
        person.sex.value = "male"
        person.birth = Mock()
        person.birth.date = "1920-05-15"
        person.birth.place = "Paris"
        person.death = Mock()
        person.death.date = "1990-08-20"
        person.death.place = "Lyon"
        person.occupation = "Engineer"

        result = service.anonymize_person(person, PrivacyLevel.PUBLIC)

        assert result.person_id == "p1"
        assert result.first_name == "Jean"
        assert result.surname == "Dupont"
        assert result.sex == "male"
        assert result.birth_date == "1920-05-15"
        assert result.death_date == "1990-08-20"
        assert result.anonymized is False
        assert result.privacy_level == PrivacyLevel.PUBLIC

    def test_restricted_level_partial_anonymization(self, service):
        """RESTRICTED level should partially anonymize sensitive data."""
        person = Mock(spec=Person)
        person.key = "p2"
        person.first_name = "Marie"
        person.surname = "Martin"
        person.sex = Mock()
        person.sex.value = "female"
        person.birth = Mock()
        person.birth.date = "2000-03-10"
        person.birth.place = "Bordeaux"
        person.death = None
        person.occupation = "Doctor"

        result = service.anonymize_person(person, PrivacyLevel.RESTRICTED)

        assert result.person_id == "p2"
        assert result.first_name == "Marie"
        assert result.surname == "Martin"
        assert result.birth_date == "2000"  # Year only (privacy protection)
        assert result.birth_place is None  # Hidden
        assert result.occupation is None  # Hidden
        assert result.is_living is True
        assert result.anonymized is True
        assert result.privacy_level == PrivacyLevel.RESTRICTED

    def test_anonymized_level_full_anonymization(self, service):
        person = Mock(spec=Person)
        person.key = "p3"
        person.first_name = "Sophie"
        person.surname = "Bernard"
        person.sex = Mock()
        person.sex.value = "female"
        person.birth = Mock()
        person.birth.date = "2005-07-20"
        person.death = None

        result = service.anonymize_person(person, PrivacyLevel.ANONYMIZED)

        assert result.person_id == "p3"
        assert result.first_name == "[Personne vivante]"
        assert result.surname == "[Confidentiel]"
        assert result.sex is None  # Hidden
        assert result.birth_date is None  # Hidden
        assert result.birth_place is None  # Hidden
        assert result.death_date is None  # Hidden
        assert result.is_living is True
        assert result.anonymized is True
        assert result.privacy_level == PrivacyLevel.ANONYMIZED

    def test_anonymization_preserves_deceased_flag(self, service):
        """Anonymization should preserve deceased status for PUBLIC level."""
        person = Mock(spec=Person)
        person.key = "p4"
        person.first_name = "Pierre"
        person.surname = "Durant"
        person.sex = Mock()
        person.sex.value = "male"
        person.birth = Mock()
        person.birth.date = "1850-01-01"
        person.death = Mock()
        person.death.date = "1920-01-01"
        person.occupation = None

        result = service.anonymize_person(person, PrivacyLevel.PUBLIC)

        assert result.is_living is False
        assert result.anonymized is False


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def service(self):
        """Create service with mock database."""
        db = Mock(spec=Database)
        return PrivacyAwareSearch(db)

    def test_person_without_names(self, service):
        """Test handling person without names (should provide defaults)."""
        person = Mock(spec=Person)
        person.key = "p1"
        person.first_name = None
        person.surname = None
        person.sex = None
        person.birth = None
        person.death = None
        person.occupation = None

        result = service.anonymize_person(person, PrivacyLevel.PUBLIC)

        assert result.first_name == "Unknown"
        assert result.surname == "Unknown"

    def test_person_without_sex(self, service):
        """Test handling person without sex field."""
        person = Mock(spec=Person)
        person.key = "p2"
        person.first_name = "Alex"
        person.surname = "Smith"
        person.sex = None
        person.birth = None
        person.death = None
        person.occupation = None

        result = service.anonymize_person(person, PrivacyLevel.PUBLIC)

        # Implementation returns None for missing sex, not "unknown"
        assert result.sex is None

    def test_person_with_only_birth_year(self, service):
        """Test person with only birth year (no full date)."""
        person = Mock(spec=Person)
        person.birth = Mock()
        person.birth.date = "1995"
        person.death = None

        # Should be able to calculate age from year
        is_living = service.is_person_living(person)
        assert is_living is True  # Born 1995, < 100 years

    def test_person_born_future_year(self, service):
        """Test person with future birth year (data error)."""
        person = Mock(spec=Person)
        person.birth = Mock()
        person.birth.date = "2030-01-01"
        person.death = None

        # Should handle invalid data conservatively
        is_living = service.is_person_living(person)
        assert is_living is True


class TestRGPDCompliance:
    """Test RGPD compliance aspects."""

    @pytest.fixture
    def service(self):
        """Create service with mock database."""
        db = Mock(spec=Database)
        return PrivacyAwareSearch(db)

    def test_living_persons_protected_by_default(self, service):
        """RGPD Article 9: Living persons must be protected by default."""
        living_person = Mock(spec=Person)
        living_person.birth = Mock()
        living_person.birth.date = "2000-01-01"
        living_person.death = None

        # Without authentication, must be anonymized
        level = service.get_privacy_level(living_person, user_id=None)
        assert level == PrivacyLevel.ANONYMIZED

    def test_deceased_persons_public_data(self, service):
        """Deceased persons data can be public (no RGPD protection needed)."""
        deceased_person = Mock(spec=Person)
        deceased_person.birth = Mock()
        deceased_person.birth.date = "1900-01-01"
        deceased_person.death = Mock()
        deceased_person.death.date = "1980-01-01"

        level = service.get_privacy_level(deceased_person, user_id=None)
        assert level == PrivacyLevel.PUBLIC

    def test_100_year_rule_compliance(self, service):
        """Persons over 100 years treated as deceased (CNIL recommendation)."""
        very_old_person = Mock(spec=Person)
        very_old_person.birth = Mock()
        very_old_person.birth.date = "1920-01-01"  # 105 years old
        very_old_person.death = None

        is_living = service.is_person_living(very_old_person)
        assert is_living is False

        level = service.get_privacy_level(very_old_person, user_id=None)
        assert level == PrivacyLevel.PUBLIC
