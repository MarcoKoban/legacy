"""Search and genealogy routers with privacy protection."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse

from ...db.database import Database
from ..dependencies import get_database
from ..models.search import (
    GenealogyTreeResponse,
    SearchQuery,
    SearchResponse,
)
from ..services.privacy_search import PrivacyAwareSearch

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Search & Genealogy"])


def get_search_service(db: Database = Depends(get_database)) -> PrivacyAwareSearch:
    """Dependency to get privacy-aware search service."""
    return PrivacyAwareSearch(db)


@router.get("/api/v1/search/persons", response_model=SearchResponse)
async def search_persons(
    query: str = Query(..., min_length=1, max_length=200, description="Search query"),
    first_name: Optional[str] = Query(None, max_length=100),
    surname: Optional[str] = Query(None, max_length=100),
    birth_year_from: Optional[int] = Query(None, ge=1000, le=2100),
    birth_year_to: Optional[int] = Query(None, ge=1000, le=2100),
    birth_place: Optional[str] = Query(None, max_length=200),
    sex: Optional[str] = Query(None, pattern="^(male|female|unknown)$"),
    include_living: bool = Query(
        False, description="Include living persons (requires authorization)"
    ),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: Optional[str] = Query(None, description="User ID for authorization"),
    search_service: PrivacyAwareSearch = Depends(get_search_service),
):
    """
    Recherche de personnes avec anonymisation automatique.

    **Protection vie privée :**
    - Les personnes vivantes sont anonymisées par défaut
    - Les dates de naissance des vivants sont tronquées (année seulement)
    - Les lieux de naissance/décès des vivants sont masqués
    - L'accès complet nécessite une autorisation

    **Paramètres :**
    - `query`: Texte de recherche (nom, prénom)
    - `first_name`: Filtrer par prénom
    - `surname`: Filtrer par nom de famille
    - `birth_year_from`: Année de naissance minimale
    - `birth_year_to`: Année de naissance maximale
    - `birth_place`: Filtrer par lieu de naissance
    - `sex`: Filtrer par sexe (male/female/unknown)
    - `include_living`: Inclure les personnes vivantes (défaut: False)
    - `limit`: Nombre de résultats (max 100)
    - `offset`: Pagination

    **Retour :**
    - Liste de résultats avec niveau de confidentialité appliqué
    - Compteur de résultats anonymisés
    """
    try:
        logger.info(
            f"Search request: query='{query}', "
            f"include_living={include_living}, "
            f"user={user_id or 'anonymous'}"
        )

        search_query = SearchQuery(
            query=query,
            first_name=first_name,
            surname=surname,
            birth_year_from=birth_year_from,
            birth_year_to=birth_year_to,
            birth_place=birth_place,
            sex=sex,
            include_living=include_living,
            limit=limit,
            offset=offset,
        )

        results = search_service.search_persons(search_query, user_id)
        anonymized_count = sum(1 for r in results if r.anonymized)

        return SearchResponse(
            results=results,
            total=len(results),
            offset=offset,
            limit=limit,
            query=query,
            anonymized_count=anonymized_count,
        )

    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/api/v1/genealogy/ancestors/{person_id}")
async def get_ancestors(
    person_id: str,
    max_generations: int = Query(5, ge=1, le=10, description="Maximum generations"),
    user_id: Optional[str] = Query(None, description="User ID for authorization"),
    search_service: PrivacyAwareSearch = Depends(get_search_service),
):
    """
    Récupère les ancêtres d'une personne avec filtrage selon droits utilisateur.

    **Protection vie privée :**
    - Les ancêtres vivants sont filtrés ou anonymisés
    - Les informations sensibles sont masquées
    - L'accès dépend des autorisations utilisateur

    **Paramètres :**
    - `person_id`: ID de la personne racine
    - `max_generations`: Nombre maximum de générations (1-10)
    - `user_id`: ID utilisateur pour vérification des droits

    **Retour :**
    - Arbre des ancêtres avec protection vie privée
    - Statistiques (nombre de nœuds, génération max)
    """
    try:
        logger.info(
            f"Ancestors request: person_id={person_id},"
            f"max_gen={max_generations}, user={user_id or 'anonymous'}"
        )

        ancestors = search_service.get_ancestors(person_id, max_generations, user_id)
        anonymized_count = sum(
            1 for a in ancestors if a.privacy_level.value == "anonymized"
        )

        return GenealogyTreeResponse(
            root_person_id=person_id,
            tree_type="ancestors",
            nodes=ancestors,
            total_nodes=len(ancestors),
            max_generation=max((a.generation for a in ancestors), default=0),
            anonymized_count=anonymized_count,
        )

    except Exception as e:
        logger.error(f"Ancestors retrieval error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve ancestors")


@router.get("/api/v1/genealogy/descendants/{person_id}")
async def get_descendants(
    person_id: str,
    max_generations: int = Query(5, ge=1, le=10, description="Maximum generations"),
    user_id: Optional[str] = Query(None, description="User ID for authorization"),
    search_service: PrivacyAwareSearch = Depends(get_search_service),
):
    """
    Récupère les descendants d'une personne avec protection des personnes vivantes.

    **Protection vie privée :**
    - Les descendants vivants sont automatiquement filtrés
    - Seules les personnes décédées ou autorisées sont affichées
    - Les informations sensibles sont masquées

    **Paramètres :**
    - `person_id`: ID de la personne racine
    - `max_generations`: Nombre maximum de générations (1-10)
    - `user_id`: ID utilisateur pour vérification des droits

    **Retour :**
    - Arbre des descendants avec protection vie privée
    - Les personnes vivantes non autorisées sont exclues
    """
    try:
        logger.info(
            f"Descendants request: person_id={person_id}, "
            f"max_gen={max_generations}, user={user_id or 'anonymous'}"
        )

        descendants = search_service.get_descendants(
            person_id, max_generations, user_id
        )
        anonymized_count = sum(
            1 for d in descendants if d.privacy_level.value == "anonymized"
        )

        return GenealogyTreeResponse(
            root_person_id=person_id,
            tree_type="descendants",
            nodes=descendants,
            total_nodes=len(descendants),
            max_generation=max((d.generation for d in descendants), default=0),
            anonymized_count=anonymized_count,
        )

    except Exception as e:
        logger.error(f"Descendants retrieval error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve descendants")


@router.get("/api/v1/genealogy/sosa/{sosa_number}")
async def get_person_by_sosa(
    sosa_number: int = Path(..., ge=1, description="Sosa number"),
    root_person_id: str = Query(..., description="Root person ID"),
    user_id: Optional[str] = Query(None, description="User ID for authorization"),
    search_service: PrivacyAwareSearch = Depends(get_search_service),
):
    """
    Recherche une personne par numéro Sosa avec accès conditionnel.

    **Numérotation Sosa :**
    - 1 = Personne de référence (de cujus)
    - 2 = Père
    - 3 = Mère
    - 4 = Grand-père paternel
    - 5 = Grand-mère paternelle
    - Etc. (2n = père, 2n+1 = mère)

    **Protection vie privée :**
    - L'accès dépend du statut (vivant/décédé)
    - Les personnes vivantes nécessitent une autorisation
    - Les informations sont filtrées selon les droits

    **Paramètres :**
    - `sosa_number`: Numéro Sosa (≥1)
    - `root_person_id`: ID de la personne racine (Sosa 1)
    - `user_id`: ID utilisateur pour vérification des droits

    **Retour :**
    - Informations de la personne avec protection vie privée
    - Relation généalogique
    """
    try:
        logger.info(
            f"Sosa search: number={sosa_number}, "
            f"root={root_person_id}, user={user_id or 'anonymous'}"
        )

        result = search_service.search_by_sosa(sosa_number, root_person_id, user_id)

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Person with Sosa number {sosa_number} not found",
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sosa search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Sosa search failed")


@router.get("/api/v1/genealogy/tree/{person_id}")
async def get_genealogy_tree(
    person_id: str,
    tree_type: str = Query(
        "full", pattern="^(ancestors|descendants|full)$", description="Type of tree"
    ),
    max_generations: int = Query(5, ge=1, le=10, description="Maximum generations"),
    user_id: Optional[str] = Query(None, description="User ID for authorization"),
    search_service: PrivacyAwareSearch = Depends(get_search_service),
):
    """
    Récupère un arbre généalogique personnalisé selon les autorisations.

    **Types d'arbres :**
    - `ancestors`: Arbre ascendant uniquement
    - `descendants`: Arbre descendant uniquement
    - `full`: Arbre complet (ascendants + descendants)

    **Protection vie privée :**
    - L'arbre est automatiquement filtré selon les droits
    - Les personnes vivantes sont protégées
    - Les branches sensibles peuvent être masquées

    **Paramètres :**
    - `person_id`: ID de la personne racine
    - `tree_type`: Type d'arbre (ancestors/descendants/full)
    - `max_generations`: Nombre maximum de générations
    - `user_id`: ID utilisateur pour vérification des droits

    **Retour :**
    - Arbre généalogique complet avec protection vie privée
    - Statistiques de l'arbre
    """
    try:
        logger.info(
            f"Tree request: person_id={person_id}, type={tree_type}, "
            f"user={user_id or 'anonymous'}"
        )

        nodes = []

        if tree_type in ["ancestors", "full"]:
            ancestors = search_service.get_ancestors(
                person_id, max_generations, user_id
            )
            nodes.extend(ancestors)

        if tree_type in ["descendants", "full"]:
            descendants = search_service.get_descendants(
                person_id, max_generations, user_id
            )
            nodes.extend(descendants)

        anonymized_count = sum(
            1 for n in nodes if n.privacy_level.value == "anonymized"
        )

        return GenealogyTreeResponse(
            root_person_id=person_id,
            tree_type=tree_type,
            nodes=nodes,
            total_nodes=len(nodes),
            max_generation=max((n.generation for n in nodes), default=0),
            anonymized_count=anonymized_count,
        )

    except Exception as e:
        logger.error(f"Tree retrieval error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve tree")


@router.get("/api/v1/search/privacy-info")
async def get_privacy_info():
    """
    Informations sur les règles de protection de la vie privée.

    **Niveaux de confidentialité :**

    1. **PUBLIC** : Personnes décédées
       - Toutes les informations disponibles
       - Dates et lieux complets
       - Notes et occupations

    2. **RESTRICTED** : Membres de la famille autorisés
       - Nom et prénom complets
       - Année de naissance uniquement
       - Pas de lieux
       - Données sensibles masquées

    3. **ANONYMIZED** : Personnes vivantes non autorisées
       - "[Personne vivante]"
       - "[Confidentiel]"
       - Aucune donnée personnelle

    **Critères "Vivant" :**
    - Aucune date de décès ET (âge < 100 ans OU date de naissance inconnue)

    **Règles d'accès :**
    - Par défaut : Seules les personnes décédées sont visibles
    - `include_living=true` : Nécessite une autorisation
    - Membres de la famille : Accès RESTRICTED
    - Autres : Accès ANONYMIZED
    """
    return JSONResponse(
        content={
            "privacy_levels": {
                "public": {
                    "description": "Personnes décédées - Informations complètes",
                    "data_visible": [
                        "Nom complet",
                        "Dates complètes",
                        "Lieux",
                        "Occupation",
                        "Notes",
                    ],
                },
                "restricted": {
                    "description": "Membres famille - Informations limitées",
                    "data_visible": ["Nom complet", "Année de naissance", "Sexe"],
                },
                "anonymized": {
                    "description": "Personnes vivantes - Anonymisé",
                    "data_visible": ["Aucune donnée personnelle"],
                },
            },
            "living_criteria": "Pas de date de décès ET "
            "(âge < 100 ans OU date inconnue)",
            "default_access": "PUBLIC pour décédés, ANONYMIZED pour vivants",
        }
    )
