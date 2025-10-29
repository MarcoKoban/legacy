# Documentation API Geneweb

Bienvenue dans la documentation de l'API Geneweb ! Cette API REST sécurisée permet de gérer des données généalogiques avec conformité RGPD complète.

## 📚 Documents disponibles

### 🚀 Guide de démarrage rapide
**[QUICK_START.md](./QUICK_START.md)**
- Installation et configuration rapide
- Premier exemple de code
- Concepts de base

### 📖 Documentation complète
**[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)**
- Architecture détaillée
- Tous les endpoints avec exemples
- Configuration avancée
- Sécurité et monitoring
- Exemples Python, JavaScript, cURL

### ⚡ Référence rapide
**[API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)**
- Liste condensée de tous les endpoints
- Codes d'erreur
- Exemples de requêtes
- Format parfait pour garder ouvert pendant le développement

### 🏗️ Architecture
**[ARCHITECTURE_API.md](./ARCHITECTURE_API.md)**
- Architecture technique
- Diagrammes de composants
- Flux de données
- Décisions de conception

## 🎯 Endpoints principaux

### Health Checks
```
GET  /health                 - Health check basique
GET  /health/live            - Liveness probe
GET  /health/ready           - Readiness probe
GET  /health/detailed        - Health check détaillé
GET  /metrics                - Métriques Prometheus
```

### Gestion des Personnes
```
POST   /api/v1/persons              - Créer une personne
GET    /api/v1/persons/{id}         - Récupérer une personne
GET    /api/v1/persons              - Lister les personnes
PUT    /api/v1/persons/{id}         - Mettre à jour
DELETE /api/v1/persons/{id}         - Supprimer (admin)
```

### Conformité RGPD
```
GET  /api/v1/persons/{id}/gdpr-export          - Exporter les données
POST /api/v1/persons/{id}/anonymize            - Anonymiser (admin)
POST /api/v1/persons/{id}/consent              - Gérer le consentement
GET  /api/v1/persons/{id}/data-processing-info - Info traitement
```

### Gestion de la Base de Données
```
GET  /api/v1/database/stats    - Statistiques
GET  /api/v1/database/health   - Santé de la DB
POST /api/v1/database/reload   - Recharger (admin)
POST /api/v1/database/commit   - Commiter (admin)
GET  /api/v1/database/info     - Informations
```

## 🔐 Authentification

Utilisez un header `Authorization` avec Bearer token :

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.geneweb.com/api/v1/persons
```

## 🚦 Rate Limiting

- **Standard** : 100 requêtes/minute par IP
- **Admin** : 1000 requêtes/minute

Headers de réponse :
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 📊 Codes de statut HTTP

| Code | Signification |
|------|---------------|
| 200 | OK - Succès |
| 201 | Created - Ressource créée |
| 204 | No Content - Suppression réussie |
| 400 | Bad Request - Données invalides |
| 401 | Unauthorized - Non authentifié |
| 403 | Forbidden - Permissions insuffisantes |
| 404 | Not Found - Ressource non trouvée |
| 422 | Unprocessable Entity - Validation échouée |
| 429 | Too Many Requests - Rate limit dépassé |
| 500 | Internal Server Error - Erreur serveur |
| 503 | Service Unavailable - Service indisponible |

## 🛠️ Exemples rapides

### Python
```python
import requests

BASE_URL = "https://api.geneweb.com"
headers = {"Authorization": "Bearer YOUR_API_KEY"}

# Créer une personne
response = requests.post(
    f"{BASE_URL}/api/v1/persons",
    headers=headers,
    json={
        "first_name": "Marie",
        "surname": "Curie",
        "sex": "female",
        "birth_date": "1867-11-07"
    }
)
person = response.json()
print(f"Personne créée : {person['person_id']}")

# Récupérer les stats de la DB
stats = requests.get(f"{BASE_URL}/api/v1/database/stats").json()
print(f"Personnes : {stats['person_count']}")
```

### JavaScript/TypeScript
```javascript
const BASE_URL = 'https://api.geneweb.com';
const headers = {
  'Authorization': 'Bearer YOUR_API_KEY',
  'Content-Type': 'application/json'
};

// Créer une personne
const response = await fetch(`${BASE_URL}/api/v1/persons`, {
  method: 'POST',
  headers: headers,
  body: JSON.stringify({
    first_name: 'Marie',
    surname: 'Curie',
    sex: 'female',
    birth_date: '1867-11-07'
  })
});
const person = await response.json();
console.log(`Personne créée : ${person.person_id}`);

// Stats DB
const statsResponse = await fetch(`${BASE_URL}/api/v1/database/stats`);
const stats = await statsResponse.json();
console.log(`Personnes : ${stats.person_count}`);
```

### cURL
```bash
# Créer une personne
curl -X POST https://api.geneweb.com/api/v1/persons \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Marie",
    "surname": "Curie",
    "sex": "female",
    "birth_date": "1867-11-07"
  }'

# Récupérer une personne
curl -X GET https://api.geneweb.com/api/v1/persons/{id} \
  -H "Authorization: Bearer YOUR_API_KEY"

# Stats de la DB (public)
curl -X GET https://api.geneweb.com/api/v1/database/stats

# Health check
curl -X GET https://api.geneweb.com/health
```

## 🔒 Sécurité

L'API implémente de nombreuses mesures de sécurité :

- ✅ HTTPS obligatoire en production
- ✅ Headers de sécurité (CSP, HSTS, X-Frame-Options, etc.)
- ✅ Rate limiting anti-DDoS
- ✅ Validation des entrées
- ✅ Protection XSS, CSRF, Injection SQL
- ✅ CORS sécurisé
- ✅ Logging sécurisé (PII masqué)
- ✅ Conformité RGPD complète

Voir [API_DOCUMENTATION.md](./API_DOCUMENTATION.md#sécurité) pour les détails.

## 🌍 Environnements

### Production
```
URL: https://api.geneweb.com
Port: 443 (HTTPS)
```

### Développement
```
URL: http://localhost:8000
Port: 8000 (HTTP)
```

## 📦 Installation

### Prérequis
- Python 3.9+
- pip ou poetry

### Installation rapide
```bash
# Cloner le repository
git clone <repository-url>
cd geneweb_python

# Installer les dépendances
pip install -r requirements.txt

# Configurer
cp .env.example .env
nano .env

# Lancer en développement
python start_api.py --dev --reload
```

Voir [QUICK_START.md](./QUICK_START.md) pour plus de détails.

## 🧪 Tests

```bash
# Lancer tous les tests
pytest tests/

# Tests d'intégration uniquement
pytest tests/integration/

# Avec couverture
pytest --cov=src/geneweb/api tests/
```

## 📈 Monitoring

### Prometheus
L'API expose des métriques sur `/metrics` :
```
geneweb_http_requests_total
geneweb_http_request_duration_seconds
geneweb_rate_limit_hits_total
geneweb_security_events_total
```

### Health Checks
Pour Kubernetes/Docker :
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
```

## 🆘 Support

### Documentation
- [Guide complet](./API_DOCUMENTATION.md)
- [Référence rapide](./API_QUICK_REFERENCE.md)
- [Architecture](./ARCHITECTURE_API.md)
- [Quick Start](./QUICK_START.md)

### Code source
- [Guide développeur](../DEVELOPER_GUIDE.md)
- [Sécurité](../../SECURITY.md)
- [Intégration DB](../../DATABASE_INTEGRATION_GUIDE.md)

### Problèmes courants

**401 Unauthorized**
- Vérifiez que votre API key est valide
- Format : `Authorization: Bearer gw_your_key_here`

**429 Too Many Requests**
- Respectez le rate limit (100 req/min)
- Utilisez des exponential backoffs

**422 Validation Error**
- Vérifiez le format de vos données
- Consultez la documentation de l'endpoint

**503 Service Unavailable**
- La DB peut être en maintenance
- Vérifiez `/api/v1/database/health`

## 📝 Changelog

### Version 0.1.0 (Octobre 2025)
- ✅ Endpoints de gestion des personnes (CRUD)
- ✅ Conformité RGPD complète
- ✅ Gestion de base de données
- ✅ Health checks et monitoring
- ✅ Rate limiting
- ✅ Sécurité avancée
- ✅ Documentation complète

## 🤝 Contribution

Voir [CONTRIBUTING.md](../../CONTRIBUTING.md) pour les guidelines de contribution.

## 📄 License

Voir [LICENSE](../../LICENSE) pour les détails.

---

**Dernière mise à jour** : 19 octobre 2025  
**Version API** : 0.1.0
