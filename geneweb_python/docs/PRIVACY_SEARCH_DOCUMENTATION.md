# Système de Recherche Généalogique avec Protection de la Vie Privée

## 📋 Vue d'Ensemble

Le système de recherche généalogique implémente une protection automatique de la vie privée pour toutes les requêtes, garantissant que les données sensibles des personnes vivantes sont protégées selon la réglementation RGPD.

## 🔒 Niveaux de Confidentialité

### 1. PUBLIC
**Appliqué aux** : Personnes décédées

**Données visibles** :
- Nom et prénom complets
- Dates de naissance et décès complètes
- Lieux de naissance et décès
- Occupation
- Notes biographiques
- Liens familiaux

**Exemple** :
```json
{
  "person_id": "P001",
  "first_name": "Jean",
  "surname": "Dupont",
  "birth_date": "1920-05-15",
  "birth_place": "Paris, France",
  "death_date": "1995-12-20",
  "privacy_level": "public",
  "anonymized": false
}
```

### 2. RESTRICTED
**Appliqué aux** : Personnes vivantes, membres de la famille autorisés

**Données visibles** :
- Nom et prénom complets
- Année de naissance uniquement (pas la date complète)
- Sexe
- Statut "vivant"

**Données masquées** :
- Jour et mois de naissance
- Lieu de naissance
- Occupation
- Notes
- Adresses

**Exemple** :
```json
{
  "person_id": "P002",
  "first_name": "Marie",
  "surname": "Martin",
  "birth_date": "1990",
  "birth_place": null,
  "privacy_level": "restricted",
  "anonymized": true,
  "is_living": true
}
```

### 3. ANONYMIZED
**Appliqué aux** : Personnes vivantes, accès non autorisé

**Données visibles** :
- ID de la personne (pour structure de l'arbre)
- Indication "[Personne vivante]"

**Toutes données personnelles masquées** :
- Nom remplacé par "[Confidentiel]"
- Aucune date
- Aucun lieu
- Aucune information personnelle

**Exemple** :
```json
{
  "person_id": "P003",
  "first_name": "[Personne vivante]",
  "surname": "[Confidentiel]",
  "privacy_level": "anonymized",
  "anonymized": true,
  "is_living": true
}
```

## 🔍 Endpoints de Recherche

### 1. Recherche de Personnes
```http
GET /api/v1/search/persons
```

**Paramètres** :
- `query` (required) : Texte de recherche
- `first_name` (optional) : Filtrer par prénom
- `surname` (optional) : Filtrer par nom
- `birth_year_from` (optional) : Année min
- `birth_year_to` (optional) : Année max
- `birth_place` (optional) : Lieu de naissance
- `sex` (optional) : male|female|unknown
- `include_living` (optional) : Inclure vivants (défaut: false)
- `limit` (optional) : Résultats max (défaut: 20, max: 100)
- `offset` (optional) : Pagination (défaut: 0)
- `user_id` (optional) : ID utilisateur pour autorisation

**Exemple** :
```bash
curl "http://localhost:8000/api/v1/search/persons?query=Dupont&include_living=false&limit=10"
```

**Réponse** :
```json
{
  "results": [
    {
      "person_id": "P001",
      "first_name": "Jean",
      "surname": "Dupont",
      "birth_date": "1920-05-15",
      "privacy_level": "public",
      "anonymized": false
    }
  ],
  "total": 1,
  "offset": 0,
  "limit": 10,
  "query": "Dupont",
  "anonymized_count": 0
}
```

### 2. Arbre des Ancêtres
```http
GET /api/v1/genealogy/ancestors/{person_id}
```

**Paramètres** :
- `person_id` (path) : ID de la personne racine
- `max_generations` (optional) : Max générations (défaut: 5, max: 10)
- `user_id` (optional) : ID utilisateur

**Exemple** :
```bash
curl "http://localhost:8000/api/v1/genealogy/ancestors/P001?max_generations=3"
```

**Réponse** :
```json
{
  "root_person_id": "P001",
  "tree_type": "ancestors",
  "nodes": [
    {
      "person_id": "P001",
      "first_name": "Jean",
      "surname": "Dupont",
      "generation": 0,
      "privacy_level": "public"
    },
    {
      "person_id": "P002",
      "first_name": "Pierre",
      "surname": "Dupont",
      "generation": 1,
      "privacy_level": "public"
    }
  ],
  "total_nodes": 2,
  "max_generation": 1,
  "anonymized_count": 0
}
```

### 3. Arbre des Descendants
```http
GET /api/v1/genealogy/descendants/{person_id}
```

**Protection spéciale** : Les descendants vivants sont automatiquement filtrés ou anonymisés.

**Paramètres** : Identiques à `/ancestors/`

**Exemple** :
```bash
curl "http://localhost:8000/api/v1/genealogy/descendants/P001?max_generations=2"
```

### 4. Recherche par Numéro Sosa
```http
GET /api/v1/genealogy/sosa/{sosa_number}
```

**Numérotation Sosa** :
- 1 = Personne de référence (de cujus)
- 2 = Père
- 3 = Mère
- 4 = Grand-père paternel
- 5 = Grand-mère paternelle
- 6 = Grand-père maternel
- 7 = Grand-mère maternelle
- Formule : 2n = père, 2n+1 = mère

**Paramètres** :
- `sosa_number` (path) : Numéro Sosa (≥1)
- `root_person_id` (query) : ID personne racine
- `user_id` (optional) : ID utilisateur

**Exemple** :
```bash
curl "http://localhost:8000/api/v1/genealogy/sosa/2?root_person_id=P001"
```

### 5. Arbre Généalogique Complet
```http
GET /api/v1/genealogy/tree/{person_id}
```

**Paramètres** :
- `person_id` (path) : ID de la personne racine
- `tree_type` (optional) : ancestors|descendants|full (défaut: full)
- `max_generations` (optional) : Max générations (défaut: 5)
- `user_id` (optional) : ID utilisateur

**Exemple** :
```bash
curl "http://localhost:8000/api/v1/genealogy/tree/P001?tree_type=full&max_generations=3"
```

### 6. Informations sur les Règles de Confidentialité
```http
GET /api/v1/search/privacy-info
```

Retourne les règles de protection de la vie privée appliquées par l'API.

**Exemple** :
```bash
curl "http://localhost:8000/api/v1/search/privacy-info"
```

## 🛡️ Règles de Protection

### Critère "Personne Vivante"
Une personne est considérée comme vivante si :
- **Aucune date de décès** enregistrée
- ET (âge < 100 ans OU date de naissance inconnue)

### Filtrage Automatique
1. **Par défaut** (`include_living=false`) :
   - Seules les personnes décédées sont retournées
   - Les personnes vivantes sont complètement exclues

2. **Avec `include_living=true`** :
   - Les personnes vivantes sont incluses
   - Mais automatiquement anonymisées selon le niveau d'autorisation

### Anonymisation Progressive
```
Utilisateur non authentifié
    ↓
ANONYMIZED (données masquées)
    ↓
Utilisateur authentifié
    ↓
RESTRICTED (données limitées)
    ↓
Membre de la famille
    ↓
PUBLIC (si décédé) ou RESTRICTED (si vivant)
```

## 📊 Statistiques et Métriques

Chaque réponse inclut :
- `total_nodes` : Nombre total de nœuds dans l'arbre
- `anonymized_count` : Nombre de personnes anonymisées
- `max_generation` : Profondeur maximale de l'arbre

## 🔐 Sécurité et Conformité RGPD

### Article 9 RGPD - Données Sensibles
- Les données de santé sont toujours masquées
- Les données biométriques ne sont jamais exposées
- Les origines ethniques sont protégées

### Droit à l'Oubli (Article 17)
- Les personnes vivantes peuvent demander l'anonymisation complète
- Les données peuvent être supprimées sur demande

### Minimisation des Données (Article 5)
- Seules les données nécessaires sont retournées
- Le niveau de détail dépend de l'autorisation

## 🧪 Exemples d'Utilisation

### Recherche Simple
```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/search/persons",
    params={
        "query": "Dupont",
        "include_living": False,
        "limit": 20
    }
)

results = response.json()
print(f"Trouvé {results['total']} personnes")
print(f"{results['anonymized_count']} personnes anonymisées")
```

### Arbre Généalogique
```python
response = requests.get(
    "http://localhost:8000/api/v1/genealogy/tree/P001",
    params={
        "tree_type": "ancestors",
        "max_generations": 5
    }
)

tree = response.json()
print(f"Arbre avec {tree['total_nodes']} personnes")
print(f"Sur {tree['max_generation']} générations")
```

### Recherche avec Filtres
```python
response = requests.get(
    "http://localhost:8000/api/v1/search/persons",
    params={
        "query": "Martin",
        "birth_year_from": 1900,
        "birth_year_to": 1950,
        "sex": "male",
        "birth_place": "Paris"
    }
)
```

## 📝 Notes Techniques

### Performance
- Les recherches sont optimisées pour les grandes bases
- La pagination est recommandée pour les résultats > 100
- Les arbres sont limités à 10 générations maximum

### Caching
- Les résultats anonymisés peuvent être mis en cache
- Les données PUBLIC peuvent être cachées plus longtemps
- Les données RESTRICTED/ANONYMIZED ne doivent pas être cachées

### Logging
- Toutes les recherches sont loggées avec l'ID utilisateur
- Les accès aux données sensibles sont tracés
- Conformité audit RGPD

## 🚀 Intégration dans l'Application

Les endpoints sont automatiquement intégrés dans FastAPI :

```python
# Dans main.py
from .routers import search
app.include_router(search.router)
```

Les services sont disponibles via dependency injection :

```python
from fastapi import Depends
from ..services.privacy_search import PrivacyAwareSearch

@router.get("/my-endpoint")
async def my_endpoint(
    search_service: PrivacyAwareSearch = Depends(get_search_service)
):
    # Utiliser search_service
    pass
```

---

**Date** : 20 octobre 2025
**Version API** : v1
**Conformité** : RGPD Article 5, 9, 17
