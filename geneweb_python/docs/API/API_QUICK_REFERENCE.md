# Référence rapide des Endpoints API Geneweb

## URL de base
- Production : `https://api.geneweb.com`
- Développement : `http://localhost:8000`

## Authentification

Tous les endpoints marqués 🔒 nécessitent une authentification via header :
```
Authorization: Bearer YOUR_API_KEY
```

Endpoints marqués 👑 nécessitent des privilèges administrateur.

---

## Health Checks

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/health` | GET | ⚪ | Health check basique |
| `/health/live` | GET | ⚪ | Liveness probe (Kubernetes) |
| `/health/ready` | GET | ⚪ | Readiness probe (Kubernetes) |
| `/health/detailed` | GET | ⚪ | Health check détaillé |
| `/metrics` | GET | ⚪ | Métriques Prometheus |

---

## Gestion des Personnes

### `/api/v1/persons`

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/` | POST | 🔒 | Créer une nouvelle personne |
| `/{person_id}` | GET | 🔒 | Récupérer une personne |
| `/` | GET | 🔒 | Lister les personnes (pagination) |
| `/{person_id}` | PUT | 🔒 | Mettre à jour une personne |
| `/{person_id}` | DELETE | 🔒👑 | Supprimer une personne |

### Paramètres communs

**POST /api/v1/persons** - Créer une personne
```json
{
  "first_name": "Jean",          // Requis
  "surname": "Dupont",            // Requis
  "sex": "male",                  // Requis: "male", "female", "unknown"
  "birth_date": "1990-05-15",     // Optionnel: format YYYY-MM-DD
  "birth_place": "Paris, France", // Optionnel
  "death_date": "2050-12-31",     // Optionnel
  "death_place": "Lyon, France",  // Optionnel
  "occupation": "Ingénieur",      // Optionnel
  "public_name": "Jean D.",       // Optionnel
  "qualifiers": ["Junior"],       // Optionnel
  "aliases": ["JD"],              // Optionnel
  "first_names_aliases": ["John"], // Optionnel
  "surname_aliases": ["Durant"],  // Optionnel
  "titles": ["M."],               // Optionnel
  "notes": "Notes",               // Optionnel
  "psources": "Sources"           // Optionnel
}
```

**GET /api/v1/persons** - Lister (pagination)
- `skip` (int) : Nombre d'éléments à ignorer (défaut: 0)
- `limit` (int) : Nombre d'éléments max (défaut: 100, max: 1000)

---

## Conformité RGPD

### `/api/v1/persons/{person_id}`

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/gdpr-export` | GET | 🔒 | Exporter toutes les données (droit d'accès) |
| `/anonymize` | POST | 🔒👑 | Anonymiser les données (droit à l'oubli) |
| `/consent` | POST | 🔒 | Gérer le consentement de traitement |
| `/data-processing-info` | GET | 🔒 | Obtenir les infos de traitement |

### Paramètres RGPD

**POST /consent** - Enregistrer le consentement
```json
{
  "consent_given": true,
  "processing_purposes": [
    "Recherche généalogique",
    "Conservation historique"
  ],
  "consent_version": "1.0"
}
```

**POST /anonymize** - Anonymiser une personne
```json
{
  "reason": "Demande de l'utilisateur (droit à l'oubli)",
  "keep_statistical_data": false
}
```

---

## Gestion de la Base de Données

### `/api/v1/database`

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/stats` | GET | ⚪* | Statistiques de la base de données |
| `/health` | GET | ⚪* | Vérifier la santé de la DB |
| `/reload` | POST | 🔒👑 | Recharger la DB depuis le disque |
| `/commit` | POST | 🔒👑 | Commiter les changements en attente |
| `/info` | GET | ⚪* | Informations de base sur la DB |

*⚪* : Auth optionnelle (détails complets si authentifié)

---

## Gestion Multi-Bases de Données

### `/api/v1/database/databases`

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/` | GET | ⚪* | Lister toutes les bases de données |
| `/active` | GET | ⚪* | Obtenir la base de données active |
| `/` | POST | 🔒👑 | Créer une nouvelle base de données |
| `/{name}/activate` | POST | 🔒👑 | Activer une base de données |
| `/{name}/rename` | PATCH | 🔒👑 | Renommer une base de données |
| `/{name}` | DELETE | 🔒👑 | Supprimer une base de données |

*⚪* : Auth optionnelle (détails complets si authentifié)

### Paramètres Multi-DB

**POST /databases** - Créer une nouvelle base
```json
{
  "name": "nouvelle_famille",       // Requis: nom sans .gwb
  "set_active": false               // Optionnel: activer après création
}
```

**PATCH /databases/{name}/rename** - Renommer une base
```json
{
  "new_name": "famille_archives",   // Requis: nouveau nom
  "rename_files": true              // Optionnel: renommer fichiers disque
}
```

**DELETE /databases/{name}** - Supprimer une base
- `delete_files` (bool) : Supprimer aussi les fichiers (défaut: false)

### Réponses Multi-DB

**GET /databases**
```json
{
  "databases": [
    {
      "name": "family_tree",
      "path": "/data/family_tree.gwb",
      "active": true,
      "person_count": 1523,
      "family_count": 892,
      "read_only": false,
      "pending_patches": 5
    }
  ],
  "active_database": "family_tree"
}
```

**PATCH /databases/{name}/rename**
```json
{
  "success": true,
  "message": "Database renamed from 'old_name' to 'new_name' successfully",
  "old_name": "old_name",
  "new_name": "new_name",
  "files_renamed": true,
  "database": { /* ... */ }
}
```

---

### Réponses Database

**GET /stats**
```json
{
  "person_count": 1523,
  "family_count": 892,
  "pending_patches": 5,
  "read_only": false,
  "last_update": "2025-10-19T14:00:00Z"
}
```

**GET /health**
```json
{
  "status": "healthy",        // "healthy", "read_only", "unhealthy"
  "message": "Base de données opérationnelle",
  "stats": { /* ... */ },
  "timestamp": "2025-10-19T14:05:00Z"
}
```

**POST /reload**
```json
{
  "success": true,
  "message": "Base de données rechargée avec succès",
  "stats": { /* ... */ },
  "reloaded_at": "2025-10-19T14:10:00Z"
}
```

**POST /commit**
```json
{
  "success": true,
  "message": "5 patches committés avec succès",
  "patches_committed": 5,
  "committed_at": "2025-10-19T14:15:00Z"
}
```

---

## Codes d'erreur HTTP

### Succès (2xx)
- **200 OK** : Requête réussie
- **201 Created** : Ressource créée
- **204 No Content** : Suppression réussie

### Erreurs Client (4xx)
- **400 Bad Request** : Données invalides
- **401 Unauthorized** : Non authentifié
- **403 Forbidden** : Permissions insuffisantes
- **404 Not Found** : Ressource non trouvée
- **409 Conflict** : Conflit (ex: DB en lecture seule)
- **422 Unprocessable Entity** : Erreur de validation
- **429 Too Many Requests** : Rate limit dépassé

### Erreurs Serveur (5xx)
- **500 Internal Server Error** : Erreur interne
- **503 Service Unavailable** : Service indisponible

### Format des erreurs
```json
{
  "detail": "Message d'erreur",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-10-19T14:30:00Z",
  "path": "/api/v1/persons"
}
```

---

## Rate Limiting

- **Limite standard** : 100 requêtes/minute par IP
- **Limite admin** : 1000 requêtes/minute

### Headers de réponse
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Réponse rate limit dépassé (429)
```json
{
  "detail": "Trop de requêtes. Réessayez dans 45 secondes.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 45
}
```

---

## Exemples rapides

### cURL

```bash
# Créer une personne
curl -X POST https://api.geneweb.com/api/v1/persons \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Jean","surname":"Dupont","sex":"male"}'

# Récupérer une personne
curl -X GET https://api.geneweb.com/api/v1/persons/{id} \
  -H "Authorization: Bearer YOUR_API_KEY"

# Lister les personnes
curl -X GET "https://api.geneweb.com/api/v1/persons?limit=10" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Stats de la DB
curl -X GET https://api.geneweb.com/api/v1/database/stats

# Health check
curl -X GET https://api.geneweb.com/health
```

### Python

```python
import requests

BASE_URL = "https://api.geneweb.com"
headers = {"Authorization": "Bearer YOUR_API_KEY"}

# Créer une personne
response = requests.post(
    f"{BASE_URL}/api/v1/persons",
    headers=headers,
    json={"first_name": "Jean", "surname": "Dupont", "sex": "male"}
)
person = response.json()

# Stats DB
response = requests.get(f"{BASE_URL}/api/v1/database/stats")
stats = response.json()
```

### JavaScript

```javascript
const BASE_URL = 'https://api.geneweb.com';
const headers = {'Authorization': 'Bearer YOUR_API_KEY'};

// Créer une personne
const response = await fetch(`${BASE_URL}/api/v1/persons`, {
  method: 'POST',
  headers: {...headers, 'Content-Type': 'application/json'},
  body: JSON.stringify({
    first_name: 'Jean',
    surname: 'Dupont',
    sex: 'male'
  })
});
const person = await response.json();

// Stats DB
const statsResponse = await fetch(`${BASE_URL}/api/v1/database/stats`);
const stats = await statsResponse.json();
```

---

## Liens utiles

- [Documentation complète](./API_DOCUMENTATION.md)
- [Guide de sécurité](../../SECURITY.md)
- [Guide de développement](../DEVELOPER_GUIDE.md)
- [Intégration DB](../../DATABASE_INTEGRATION_GUIDE.md)

---

*Dernière mise à jour : 19 octobre 2025*
