"""Privacy-aware search service for genealogical data."""

import logging
from datetime import datetime
from typing import List, Optional

from ...core.person import Person
from ...db.database import Database
from ..models.search import (
    AncestorNode,
    DescendantNode,
    PersonSearchResult,
    PrivacyLevel,
    SearchQuery,
    SosaSearchResult,
)

logger = logging.getLogger(__name__)


class PrivacyAwareSearch:
    """Service de recherche avec protection de la vie privée."""

    def __init__(self, database: Database):
        self.db = database

    def is_person_living(self, person: Person) -> bool:
        """Détermine si une personne est vivante."""
        if person.death is not None:
            return False

        # Si pas de date de décès et date de naissance connue
        if person.birth is not None:
            try:
                # Parse birth date (format: YYYY-MM-DD ou YYYY)
                birth_year = None
                if hasattr(person.birth, "date") and person.birth.date:
                    birth_year = int(str(person.birth.date).split("-")[0])
                elif isinstance(person.birth, str):
                    birth_year = int(person.birth.split("-")[0])

                if birth_year:
                    current_year = datetime.now().year
                    age = current_year - birth_year
                    # Considérer vivant si moins de 100 ans
                    return age < 100
            except (ValueError, AttributeError):
                pass

        # Par défaut, considérer comme potentiellement vivante
        return True

    def get_privacy_level(
        self, person: Person, user_id: Optional[str] = None
    ) -> PrivacyLevel:
        """Détermine le niveau de confidentialité pour une personne."""
        is_living = self.is_person_living(person)

        if not is_living:
            # Personnes décédées : PUBLIC
            return PrivacyLevel.PUBLIC

        # Personnes vivantes : RESTRICTED par défaut
        # TODO: Vérifier si l'utilisateur est membre de la famille
        if user_id:
            # if self.is_family_member(user_id, person):
            #     return PrivacyLevel.RESTRICTED
            pass

        return PrivacyLevel.ANONYMIZED

    def anonymize_person(
        self, person: Person, privacy_level: PrivacyLevel
    ) -> PersonSearchResult:
        """Anonymise les données d'une personne selon le niveau de confidentialité."""
        is_living = self.is_person_living(person)

        if privacy_level == PrivacyLevel.PUBLIC:
            # Toutes les informations disponibles
            return PersonSearchResult(
                person_id=person.key,
                first_name=person.first_name or "Unknown",
                surname=person.surname or "Unknown",
                sex=person.sex.value if person.sex else None,
                birth_date=str(person.birth.date) if person.birth else None,
                birth_place=str(person.birth.place) if person.birth else None,
                death_date=str(person.death.date) if person.death else None,
                death_place=str(person.death.place) if person.death else None,
                is_living=is_living,
                privacy_level=privacy_level,
                anonymized=False,
                occupation=person.occupation if hasattr(person, "occupation") else None,
            )

        elif privacy_level == PrivacyLevel.RESTRICTED:
            # Informations limitées pour personnes vivantes
            return PersonSearchResult(
                person_id=person.key,
                first_name=person.first_name or "Unknown",
                surname=person.surname or "Unknown",
                sex=person.sex.value if person.sex else None,
                birth_date=(
                    str(person.birth.date).split("-")[0] if person.birth else None
                ),  # Année seulement
                birth_place=None,  # Pas de lieu
                death_date=None,
                death_place=None,
                is_living=True,
                privacy_level=privacy_level,
                anonymized=True,
            )

        else:  # ANONYMIZED
            # Données complètement anonymisées
            return PersonSearchResult(
                person_id=person.key,
                first_name="[Personne vivante]",
                surname="[Confidentiel]",
                sex=None,
                birth_date=None,
                birth_place=None,
                death_date=None,
                death_place=None,
                is_living=True,
                privacy_level=privacy_level,
                anonymized=True,
            )

    def search_persons(
        self, query: SearchQuery, user_id: Optional[str] = None
    ) -> List[PersonSearchResult]:
        """Recherche de personnes avec protection de la vie privée."""
        logger.info(
            f"Searching persons with query: {query.query}, "
            f"user: {user_id or 'anonymous'}"
        )

        all_persons = self.db.get_persons()
        results = []

        for person in all_persons:
            # Filtrage de base
            if not self._matches_query(person, query):
                continue

            # Vérifier si vivante
            is_living = self.is_person_living(person)

            # Filtrer les personnes vivantes si pas autorisé
            if is_living and not query.include_living:
                continue

            # Déterminer niveau de confidentialité
            privacy_level = self.get_privacy_level(person, user_id)

            # Anonymiser si nécessaire
            result = self.anonymize_person(person, privacy_level)
            results.append(result)

        # Pagination
        start = query.offset
        end = start + query.limit
        return results[start:end]

    def _matches_query(self, person: Person, query: SearchQuery) -> bool:
        """Vérifie si une personne correspond aux critères de recherche."""
        # Recherche texte libre
        search_text = query.query.lower()
        first_name = (person.first_name or "").lower()
        surname = (person.surname or "").lower()

        if search_text and search_text not in f"{first_name} {surname}":
            return False

        # Filtres spécifiques
        if query.first_name and query.first_name.lower() not in first_name:
            return False

        if query.surname and query.surname.lower() not in surname:
            return False

        if query.sex and person.sex and person.sex.value != query.sex:
            return False

        # Filtres de date de naissance
        if person.birth and query.birth_year_from:
            try:
                birth_year = int(str(person.birth.date).split("-")[0])
                if birth_year < query.birth_year_from:
                    return False
                if query.birth_year_to and birth_year > query.birth_year_to:
                    return False
            except (ValueError, AttributeError):
                pass

        return True

    def get_ancestors(
        self,
        person_id: str,
        max_generations: int = 5,
        user_id: Optional[str] = None,
    ) -> List[AncestorNode]:
        """Récupère les ancêtres d'une personne avec protection vie privée."""
        ancestors = []
        visited = set()

        def traverse(pid: str, generation: int):
            if generation > max_generations or pid in visited:
                return

            visited.add(pid)
            person = self.db.get_person(pid)
            if not person:
                return

            privacy_level = self.get_privacy_level(person, user_id)
            is_living = self.is_person_living(person)

            # Créer le nœud ancêtre
            node = AncestorNode(
                person_id=person.key,
                first_name=(
                    person.first_name
                    if privacy_level != PrivacyLevel.ANONYMIZED
                    else "[Confidentiel]"
                ),
                surname=(
                    person.surname
                    if privacy_level != PrivacyLevel.ANONYMIZED
                    else "[Confidentiel]"
                ),
                generation=generation,
                birth_date=(
                    str(person.birth.date)
                    if person.birth and privacy_level == PrivacyLevel.PUBLIC
                    else None
                ),
                death_date=(
                    str(person.death.date)
                    if person.death and privacy_level == PrivacyLevel.PUBLIC
                    else None
                ),
                is_living=is_living,
                privacy_level=privacy_level,
            )
            ancestors.append(node)

            # Parcourir les parents
            if hasattr(person, "parents") and person.parents:
                # TODO: Récupérer les IDs des parents depuis la famille
                pass

        traverse(person_id, 0)
        return ancestors

    def get_descendants(
        self,
        person_id: str,
        max_generations: int = 5,
        user_id: Optional[str] = None,
    ) -> List[DescendantNode]:
        """Récupère les descendants d'une personne avec protection vie privée."""
        descendants = []
        visited = set()

        def traverse(pid: str, generation: int):
            if generation > max_generations or pid in visited:
                return

            visited.add(pid)
            person = self.db.get_person(pid)
            if not person:
                return

            privacy_level = self.get_privacy_level(person, user_id)
            is_living = self.is_person_living(person)

            # Ne pas afficher les personnes vivantes non autorisées
            if is_living and privacy_level == PrivacyLevel.ANONYMIZED:
                return

            node = DescendantNode(
                person_id=person.key,
                first_name=(
                    person.first_name
                    if privacy_level != PrivacyLevel.ANONYMIZED
                    else "[Confidentiel]"
                ),
                surname=(
                    person.surname
                    if privacy_level != PrivacyLevel.ANONYMIZED
                    else "[Confidentiel]"
                ),
                generation=generation,
                birth_date=(
                    str(person.birth.date)
                    if person.birth and privacy_level == PrivacyLevel.PUBLIC
                    else None
                ),
                is_living=is_living,
                privacy_level=privacy_level,
                children_ids=[],
            )
            descendants.append(node)

            # Parcourir les enfants
            # TODO: Implémenter récupération des enfants

        traverse(person_id, 0)
        return descendants

    def search_by_sosa(
        self, sosa_number: int, root_person_id: str, user_id: Optional[str] = None
    ) -> Optional[SosaSearchResult]:
        """Recherche une personne par numéro Sosa."""
        # TODO: Implémenter la recherche Sosa
        # La numérotation Sosa : 1=personne de référence, 2=père, 3=mère, etc.
        logger.info(f"Searching for Sosa {sosa_number} from root {root_person_id}")
        return None
