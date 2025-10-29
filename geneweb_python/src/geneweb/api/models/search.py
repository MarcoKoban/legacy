"""Search and genealogy models with privacy protection."""

from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class PrivacyLevel(str, Enum):
    """Privacy levels for person data."""

    PUBLIC = "public"  # Toutes les informations visibles
    RESTRICTED = "restricted"  # Informations limitées (personnes vivantes)
    PRIVATE = "private"  # Minimum d'informations
    ANONYMIZED = "anonymized"  # Données complètement anonymisées


class SearchQuery(BaseModel):
    """Search query model."""

    query: str = Field(..., min_length=1, max_length=200, description="Search text")
    first_name: Optional[str] = Field(None, max_length=100)
    surname: Optional[str] = Field(None, max_length=100)
    birth_year_from: Optional[int] = Field(None, ge=1000, le=2100)
    birth_year_to: Optional[int] = Field(None, ge=1000, le=2100)
    birth_place: Optional[str] = Field(None, max_length=200)
    sex: Optional[str] = Field(None, pattern="^(male|female|unknown)$")
    include_living: bool = Field(
        default=False, description="Include living persons (requires authorization)"
    )
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PersonSearchResult(BaseModel):
    """Person search result with privacy protection."""

    person_id: str
    first_name: str
    surname: str
    sex: Optional[str] = None
    birth_date: Optional[str] = None
    birth_place: Optional[str] = None
    death_date: Optional[str] = None
    death_place: Optional[str] = None
    is_living: bool = False
    privacy_level: PrivacyLevel
    anonymized: bool = False

    # Informations supplémentaires (si autorisées)
    occupation: Optional[str] = None
    notes: Optional[str] = None
    parents_ids: Optional[List[str]] = None
    children_ids: Optional[List[str]] = None


class SearchResponse(BaseModel):
    """Search results response."""

    results: List[PersonSearchResult]
    total: int
    offset: int
    limit: int
    query: str
    anonymized_count: int = 0


class AncestorNode(BaseModel):
    """Ancestor node in genealogy tree."""

    person_id: str
    first_name: str
    surname: str
    generation: int
    sosa_number: Optional[int] = None
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    is_living: bool = False
    privacy_level: PrivacyLevel
    father_id: Optional[str] = None
    mother_id: Optional[str] = None


class DescendantNode(BaseModel):
    """Descendant node in genealogy tree."""

    person_id: str
    first_name: str
    surname: str
    generation: int
    birth_date: Optional[str] = None
    is_living: bool = False
    privacy_level: PrivacyLevel
    children_ids: List[str] = []


class GenealogyTreeResponse(BaseModel):
    """Genealogy tree response."""

    root_person_id: str
    tree_type: str  # "ancestors", "descendants", "full"
    nodes: List[Union[AncestorNode, DescendantNode]]
    total_nodes: int
    max_generation: int
    anonymized_count: int = 0


class SosaSearchResult(BaseModel):
    """Sosa number search result."""

    sosa_number: int
    person_id: str
    first_name: str
    surname: str
    generation: int
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    is_living: bool = False
    privacy_level: PrivacyLevel
    relationship: str  # "root", "father", "mother", "grandfather", etc.
