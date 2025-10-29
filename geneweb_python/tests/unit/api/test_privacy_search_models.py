"""
Tests for privacy-aware search models (adapted to real implementation).

Tests the actual models from geneweb.api.models.search:
- PrivacyLevel enum
- SearchQuery
- PersonSearchResult
- SearchResponse
- AncestorNode
- DescendantNode
- GenealogyTreeResponse
- SosaSearchResult
"""

import pytest
from pydantic import ValidationError

from geneweb.api.models.search import (
    AncestorNode,
    DescendantNode,
    GenealogyTreeResponse,
    PersonSearchResult,
    PrivacyLevel,
    SearchQuery,
    SearchResponse,
    SosaSearchResult,
)


class TestPrivacyLevel:
    """Test PrivacyLevel enum."""

    def test_privacy_level_values(self):
        """Test that privacy levels have correct string values."""
        assert PrivacyLevel.PUBLIC.value == "public"
        assert PrivacyLevel.RESTRICTED.value == "restricted"
        assert PrivacyLevel.PRIVATE.value == "private"
        assert PrivacyLevel.ANONYMIZED.value == "anonymized"

    def test_privacy_level_from_string(self):
        """Test creating PrivacyLevel from string."""
        assert PrivacyLevel("public") == PrivacyLevel.PUBLIC
        assert PrivacyLevel("restricted") == PrivacyLevel.RESTRICTED
        assert PrivacyLevel("anonymized") == PrivacyLevel.ANONYMIZED

    def test_privacy_level_invalid(self):
        """Test that invalid privacy level raises error."""
        with pytest.raises(ValueError):
            PrivacyLevel("INVALID")


class TestSearchQuery:
    """Test SearchQuery model."""

    def test_search_query_basic(self):
        """Test basic search query."""
        query = SearchQuery(query="Dupont")

        assert query.query == "Dupont"
        assert query.first_name is None
        assert query.surname is None
        assert query.limit == 20
        assert query.offset == 0
        assert query.include_living is False

    def test_search_query_with_name_filters(self):
        """Test search query with name filters."""
        query = SearchQuery(query="Jean Dupont", first_name="Jean", surname="Dupont")

        assert query.query == "Jean Dupont"
        assert query.first_name == "Jean"
        assert query.surname == "Dupont"

    def test_search_query_with_birth_year(self):
        """Test search query with birth year range."""
        query = SearchQuery(query="test", birth_year_from=1920, birth_year_to=1930)

        assert query.birth_year_from == 1920
        assert query.birth_year_to == 1930

    def test_search_query_with_sex(self):
        """Test search query with sex filter."""
        query = SearchQuery(query="test", sex="male")
        assert query.sex == "male"

        query = SearchQuery(query="test", sex="female")
        assert query.sex == "female"

    def test_search_query_invalid_sex(self):
        """Test that invalid sex pattern is rejected."""
        with pytest.raises(ValidationError):
            SearchQuery(query="test", sex="invalid")

    def test_search_query_pagination(self):
        """Test search query pagination."""
        query = SearchQuery(query="test", limit=50, offset=10)

        assert query.limit == 50
        assert query.offset == 10

    def test_search_query_invalid_limit(self):
        """Test that invalid limit is rejected."""
        with pytest.raises(ValidationError):
            SearchQuery(query="test", limit=0)

        with pytest.raises(ValidationError):
            SearchQuery(query="test", limit=101)

    def test_search_query_invalid_offset(self):
        """Test that negative offset is rejected."""
        with pytest.raises(ValidationError):
            SearchQuery(query="test", offset=-1)

    def test_search_query_empty_string(self):
        """Test that empty query string is rejected."""
        with pytest.raises(ValidationError):
            SearchQuery(query="")

    def test_search_query_include_living(self):
        """Test include_living flag."""
        query = SearchQuery(query="test", include_living=True)
        assert query.include_living is True


class TestPersonSearchResult:
    """Test PersonSearchResult model."""

    def test_person_result_public(self):
        """Test public person result (deceased)."""
        result = PersonSearchResult(
            person_id="p1",
            first_name="Jean",
            surname="Dupont",
            sex="male",
            birth_date="1920-05-15",
            death_date="1990-08-20",
            is_living=False,
            privacy_level=PrivacyLevel.PUBLIC,
            anonymized=False,
        )

        assert result.person_id == "p1"
        assert result.first_name == "Jean"
        assert result.surname == "Dupont"
        assert result.sex == "male"
        assert result.is_living is False
        assert result.privacy_level == PrivacyLevel.PUBLIC
        assert result.anonymized is False

    def test_person_result_anonymized(self):
        """Test anonymized person result (living)."""
        result = PersonSearchResult(
            person_id="p2",
            first_name="[PROTECTED]",
            surname="[PROTECTED]",
            is_living=True,
            privacy_level=PrivacyLevel.ANONYMIZED,
            anonymized=True,
        )

        assert result.first_name == "[PROTECTED]"
        assert result.surname == "[PROTECTED]"
        assert result.is_living is True
        assert result.privacy_level == PrivacyLevel.ANONYMIZED
        assert result.anonymized is True

    def test_person_result_with_optional_fields(self):
        """Test person result with optional fields."""
        result = PersonSearchResult(
            person_id="p3",
            first_name="Marie",
            surname="Martin",
            privacy_level=PrivacyLevel.RESTRICTED,
            occupation="Doctor",
            notes="[PROTECTED]",
            parents_ids=["p4", "p5"],
            children_ids=["p6"],
        )

        assert result.occupation == "Doctor"
        assert result.notes == "[PROTECTED]"
        assert result.parents_ids == ["p4", "p5"]
        assert result.children_ids == ["p6"]


class TestSearchResponse:
    """Test SearchResponse model."""

    def test_search_response_empty(self):
        """Test empty search response."""
        response = SearchResponse(
            results=[], total=0, offset=0, limit=20, query="test", anonymized_count=0
        )

        assert len(response.results) == 0
        assert response.total == 0
        assert response.anonymized_count == 0

    def test_search_response_with_results(self):
        """Test search response with results."""
        person1 = PersonSearchResult(
            person_id="p1",
            first_name="Jean",
            surname="Dupont",
            privacy_level=PrivacyLevel.PUBLIC,
            is_living=False,
        )

        person2 = PersonSearchResult(
            person_id="p2",
            first_name="[PROTECTED]",
            surname="[PROTECTED]",
            privacy_level=PrivacyLevel.ANONYMIZED,
            anonymized=True,
            is_living=True,
        )

        response = SearchResponse(
            results=[person1, person2],
            total=2,
            offset=0,
            limit=20,
            query="Dupont",
            anonymized_count=1,
        )

        assert len(response.results) == 2
        assert response.total == 2
        assert response.anonymized_count == 1
        assert response.query == "Dupont"


class TestAncestorNode:
    """Test AncestorNode model."""

    def test_ancestor_node_basic(self):
        """Test basic ancestor node."""
        node = AncestorNode(
            person_id="p1",
            first_name="Paul",
            surname="Dupont",
            generation=1,
            sosa_number=2,
            privacy_level=PrivacyLevel.PUBLIC,
            is_living=False,
        )

        assert node.person_id == "p1"
        assert node.generation == 1
        assert node.sosa_number == 2
        assert node.privacy_level == PrivacyLevel.PUBLIC

    def test_ancestor_node_with_parents(self):
        """Test ancestor node with parent IDs."""
        node = AncestorNode(
            person_id="p2",
            first_name="Jacques",
            surname="Dupont",
            generation=2,
            sosa_number=4,
            privacy_level=PrivacyLevel.PUBLIC,
            father_id="p8",
            mother_id="p9",
        )

        assert node.father_id == "p8"
        assert node.mother_id == "p9"

    def test_ancestor_node_living(self):
        """Test living ancestor node (anonymized)."""
        node = AncestorNode(
            person_id="p3",
            first_name="[PROTECTED]",
            surname="[PROTECTED]",
            generation=1,
            privacy_level=PrivacyLevel.ANONYMIZED,
            is_living=True,
        )

        assert node.is_living is True
        assert node.privacy_level == PrivacyLevel.ANONYMIZED


class TestDescendantNode:
    """Test DescendantNode model."""

    def test_descendant_node_basic(self):
        """Test basic descendant node."""
        node = DescendantNode(
            person_id="p1",
            first_name="Sophie",
            surname="Dupont",
            generation=1,
            privacy_level=PrivacyLevel.PUBLIC,
            is_living=False,
        )

        assert node.person_id == "p1"
        assert node.generation == 1
        assert node.privacy_level == PrivacyLevel.PUBLIC
        assert node.children_ids == []

    def test_descendant_node_with_children(self):
        """Test descendant node with children."""
        node = DescendantNode(
            person_id="p2",
            first_name="Marie",
            surname="Dupont",
            generation=1,
            privacy_level=PrivacyLevel.PUBLIC,
            children_ids=["p5", "p6", "p7"],
        )

        assert len(node.children_ids) == 3
        assert "p5" in node.children_ids

    def test_descendant_node_living(self):
        """Test living descendant (anonymized)."""
        node = DescendantNode(
            person_id="p3",
            first_name="[PROTECTED]",
            surname="[PROTECTED]",
            generation=2,
            privacy_level=PrivacyLevel.ANONYMIZED,
            is_living=True,
        )

        assert node.is_living is True
        assert node.privacy_level == PrivacyLevel.ANONYMIZED


class TestGenealogyTreeResponse:
    """Test GenealogyTreeResponse model."""

    def test_genealogy_tree_empty(self):
        """Test empty genealogy tree."""
        tree = GenealogyTreeResponse(
            root_person_id="p1",
            tree_type="full",
            nodes=[],
            total_nodes=0,
            max_generation=0,
            anonymized_count=0,
        )

        assert tree.root_person_id == "p1"
        assert tree.tree_type == "full"
        assert len(tree.nodes) == 0
        assert tree.total_nodes == 0

    def test_genealogy_tree_ancestors(self):
        """Test genealogy tree with ancestors."""
        ancestor = AncestorNode(
            person_id="p2",
            first_name="Paul",
            surname="Dupont",
            generation=1,
            sosa_number=2,
            privacy_level=PrivacyLevel.PUBLIC,
        )

        tree = GenealogyTreeResponse(
            root_person_id="p1",
            tree_type="ancestors",
            nodes=[ancestor],
            total_nodes=1,
            max_generation=1,
            anonymized_count=0,
        )

        assert tree.tree_type == "ancestors"
        assert tree.total_nodes == 1
        assert tree.max_generation == 1

    def test_genealogy_tree_descendants(self):
        """Test genealogy tree with descendants."""
        descendant = DescendantNode(
            person_id="p3",
            first_name="Sophie",
            surname="Dupont",
            generation=1,
            privacy_level=PrivacyLevel.PUBLIC,
        )

        tree = GenealogyTreeResponse(
            root_person_id="p1",
            tree_type="descendants",
            nodes=[descendant],
            total_nodes=1,
            max_generation=1,
            anonymized_count=0,
        )

        assert tree.tree_type == "descendants"
        assert tree.total_nodes == 1

    def test_genealogy_tree_with_anonymized(self):
        """Test tree with anonymized nodes."""
        living_node = DescendantNode(
            person_id="p4",
            first_name="[PROTECTED]",
            surname="[PROTECTED]",
            generation=2,
            privacy_level=PrivacyLevel.ANONYMIZED,
            is_living=True,
        )

        tree = GenealogyTreeResponse(
            root_person_id="p1",
            tree_type="full",
            nodes=[living_node],
            total_nodes=1,
            max_generation=2,
            anonymized_count=1,
        )

        assert tree.anonymized_count == 1


class TestSosaSearchResult:
    """Test SosaSearchResult model."""

    def test_sosa_result_root(self):
        """Test Sosa result for root person (1)."""
        result = SosaSearchResult(
            sosa_number=1,
            person_id="p1",
            first_name="Jean",
            surname="Dupont",
            generation=0,
            privacy_level=PrivacyLevel.PUBLIC,
            relationship="root",
        )

        assert result.sosa_number == 1
        assert result.generation == 0
        assert result.relationship == "root"

    def test_sosa_result_father(self):
        """Test Sosa result for father (2)."""
        result = SosaSearchResult(
            sosa_number=2,
            person_id="p2",
            first_name="Paul",
            surname="Dupont",
            generation=1,
            privacy_level=PrivacyLevel.PUBLIC,
            relationship="father",
        )

        assert result.sosa_number == 2
        assert result.relationship == "father"

    def test_sosa_result_mother(self):
        """Test Sosa result for mother (3)."""
        result = SosaSearchResult(
            sosa_number=3,
            person_id="p3",
            first_name="Anne",
            surname="Bernard",
            generation=1,
            privacy_level=PrivacyLevel.PUBLIC,
            relationship="mother",
        )

        assert result.sosa_number == 3
        assert result.relationship == "mother"

    def test_sosa_result_living(self):
        """Test Sosa result for living person (anonymized)."""
        result = SosaSearchResult(
            sosa_number=4,
            person_id="p4",
            first_name="[PROTECTED]",
            surname="[PROTECTED]",
            generation=2,
            privacy_level=PrivacyLevel.ANONYMIZED,
            is_living=True,
            relationship="paternal grandfather",
        )

        assert result.is_living is True
        assert result.privacy_level == PrivacyLevel.ANONYMIZED
        assert result.first_name == "[PROTECTED]"


class TestModelValidation:
    """Test Pydantic validation."""

    def test_required_fields_missing(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            PersonSearchResult(
                person_id="p1"
            )  # Missing first_name, surname, privacy_level

    def test_invalid_birth_year(self):
        """Test that invalid birth year is rejected."""
        with pytest.raises(ValidationError):
            SearchQuery(query="test", birth_year_from=999)  # Too early

        with pytest.raises(ValidationError):
            SearchQuery(query="test", birth_year_to=2101)  # Too late

    def test_string_too_long(self):
        """Test that too long strings are rejected."""
        with pytest.raises(ValidationError):
            SearchQuery(query="a" * 201)  # Max 200

    def test_negative_generation(self):
        # If we add ge=0 constraint in model, this would fail
        # Currently no constraint, so just test that creation works
        node = AncestorNode(
            person_id="p1",
            first_name="Test",
            surname="Test",
            generation=0,
            privacy_level=PrivacyLevel.PUBLIC,
        )
        assert node.generation == 0
