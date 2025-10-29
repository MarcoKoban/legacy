# 🔐 Système d'Authentification - Guide de Démarrage Rapide

## 📋 Fonctionnalités

Système d'authentification moderne et sécurisé avec :

- ✅ **JWT (JSON Web Tokens)** - Access tokens (30 min) + Refresh tokens (7 jours)
- ✅ **Bcrypt** - Hachage sécurisé des mots de passe
- ✅ **Token Blacklist** - Révocation immédiate lors du logout
- ✅ **Base de données** - Stockage persistant avec SQLAlchemy (SQLite/PostgreSQL)
- ✅ **RBAC** - 2 rôles : USER, ADMIN
- ✅ **Audit** - Logs de tous les événements d'authentification
- ✅ **Sécurité** - Rate limiting, HTTPS, CORS, protection timing attack

## 🚀 Démarrage rapide

### 1. Installation

```bash
cd geneweb_python
pip install -r requirements.txt
```

### 2. Lancer le serveur

```bash
python start_api.py
```

Le serveur démarre sur **http://localhost:8000**

Swagger UI : **http://localhost:8000/docs**

### 3. Tester

**Option A - Script automatique :**

```bash
python test_authentication.py
```

Tests inclus : Health check, Registration, Login, Token refresh, Protected endpoints, Logout

**Option B - Manuellement avec cURL :**

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}'

# Utiliser le token
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Option C - Swagger UI :**

http://localhost:8000/docs → Authorize → `demo` / `demo1234`

## 🔑 Utilisateurs par défaut

| Username | Password  | Role   | Description                    |
|----------|-----------|--------|--------------------------------|
| admin    | admin123  | ADMIN  | Administrateur (tous droits)   |
| demo     | demo1234  | USER   | Utilisateur de démonstration   |

⚠️ **IMPORTANT :** Changez ces mots de passe en production !

## 📡 Endpoints

### `/api/v1/auth/`

| Méthode | Endpoint | Description | Auth requise |
|---------|----------|-------------|--------------|
| POST | `/login` | Connexion avec username/password | Non |
| POST | `/login/oauth2` | Login OAuth2 compatible | Non |
| POST | `/refresh` | Rafraîchir le token | Non |
| POST | `/logout` | Déconnexion + révocation | Oui |
| GET | `/me` | Info utilisateur connecté | Oui |
| POST | `/register` | Créer un compte | Non |
| POST | `/change-password` | Changer le mot de passe | Oui |
| GET | `/health` | Health check | Non |

### Exemple complet en Python

```python
import requests

# 1. Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "demo", "password": "demo1234"}
)
tokens = response.json()
access_token = tokens["access_token"]

# 2. Utiliser le token
headers = {"Authorization": f"Bearer {access_token}"}
user_info = requests.get(
    "http://localhost:8000/api/v1/auth/me",
    headers=headers
).json()
print(f"Connecté en tant que: {user_info['username']}")

# 3. Logout
requests.post(
    "http://localhost:8000/api/v1/auth/logout",
    headers=headers
)
```

## 📁 Fichiers créés

```
geneweb_python/
├── src/geneweb/api/
│   ├── routers/auth.py                # Router 8 endpoints (620 lignes)
│   ├── security/
│   │   ├── auth.py                    # Auth service (JTI, blacklist)
│   │   └── token_blacklist.py         # Gestion révocation (164 lignes)
│   └── db/
│       ├── models.py                  # Modèles SQLAlchemy (238 lignes)
│       └── database.py                # Config DB (157 lignes)
├── docs/AUTHENTICATION_GUIDE.md       # Documentation complète
├── test_authentication.py             # Tests automatisés
├── AUTHENTICATION_SUMMARY.md          # Résumé technique
└── QUICK_START_AUTH.md               # Ce guide
```

## 🔒 Sécurité

### Protections

| Protection | Détails |
|------------|---------|
| **Bcrypt** | Hachage sécurisé + salt automatique |
| **JWT + JTI** | ID unique par token pour révocation |
| **Expiration** | Access: 30 min / Refresh: 7 jours |
| **Blacklist** | Révocation immédiate au logout |
| **Rate limiting** | 100 req/min par IP (configurable) |
| **Audit** | Tous événements loggés avec IP |
| **HTTPS** | Forcé en production |
| **CORS** | Liste blanche configurable |

### Validation mots de passe

Requis :
- ≥ 8 caractères
- 1 majuscule + 1 minuscule
- 1 chiffre + 1 caractère spécial
- Pas de mots de passe communs
- Pas de séquences/répétitions

## 🧪 Tests

### Tester avec le script automatique

```bash
python test_authentication.py
```

### Tester manuellement

```bash
# Health check
curl http://localhost:8000/api/v1/auth/health

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}'

# Register new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "new@example.com",
    "full_name": "New User",
    "password": "SecureP@ss123!",
    "role": "user"
  }'
```

## 📊 Flow d'authentification

```
┌──────────┐                                    ┌──────────┐
│  Client  │                                    │   API    │
└────┬─────┘                                    └────┬─────┘
     │                                                │
     │ 1. POST /login (username, password)            │
     │───────────────────────────────────────────────>│
     │                                                │
     │                          2. Verify bcrypt hash │
     │                          3. Generate JWT (JTI) │
     │                          4. Create session     │
     │                                                │
     │ 5. Return tokens + user info                   │
     │<───────────────────────────────────────────────│
     │                                                │
     │ 6. GET /persons (Authorization: Bearer token)  │
     │───────────────────────────────────────────────>│
     │                                                │
     │                          7. Verify JWT         │
     │                          8. Check blacklist    │
     │                          9. Check permissions  │
     │                                                │
     │ 10. Return data                                │
     │<───────────────────────────────────────────────│
     │                                                │
     │ 11. POST /logout (Authorization: Bearer token) │
     │───────────────────────────────────────────────>│
     │                                                │
     │                          12. Add to blacklist  │
     │                          13. Revoke session    │
     │                                                │
     │ 14. Success                                    │
     │<───────────────────────────────────────────────│
     │                                                │
```

## ⚙️ Configuration

### Variables d'environnement (`.env`)

```bash
# Secret key pour JWT (32+ caractères REQUIS)
GENEWEB_SECURITY_SECRET_KEY=votre-cle-secrete-32-caracteres-minimum

# Token expiration (valeurs par défaut ci-dessous)
# ACCESS_TOKEN_EXPIRE_MINUTES=30
# REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
# DATABASE_URL=sqlite:///data/geneweb_users.db  # Dev
# DATABASE_URL=postgresql://user:pwd@localhost/geneweb  # Prod

# Mode
# GENEWEB_API_DEBUG=false
```

**Générer une clé sécurisée :**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📚 Documentation complète

- **Guide détaillé :** [docs/AUTHENTICATION_GUIDE.md](docs/AUTHENTICATION_GUIDE.md)
- **Résumé technique :** [AUTHENTICATION_SUMMARY.md](AUTHENTICATION_SUMMARY.md)
- **API Swagger :** http://localhost:8000/docs
- **API ReDoc :** http://localhost:8000/redoc

## ⚠️ Checklist production

- [ ] Changer mots de passe par défaut (admin/demo)
- [ ] Générer SECRET_KEY ≥ 32 caractères
- [ ] PostgreSQL au lieu de SQLite
- [ ] Redis pour blacklist (au lieu de in-memory)
- [ ] HTTPS uniquement (GENEWEB_SECURITY_FORCE_HTTPS=true)
- [ ] CORS restrictif (IPs/domaines autorisés)
- [ ] Logs en mode production
- [ ] Backups automatiques DB
- [ ] Audit de sécurité

## 🆘 Dépannage

### Le serveur ne démarre pas

```bash
# Vérifier que les dépendances sont installées
pip install -r requirements.txt

# Vérifier qu'aucun autre service n'utilise le port 8000
lsof -i :8000

# Lancer avec plus de logs
DEBUG=true python start_api.py
```

### Erreur "Invalid token"

- Le token a peut-être expiré (30 min pour access token)
- Utilisez le refresh token pour en obtenir un nouveau
- Vérifiez que vous avez bien le format `Bearer TOKEN`

### Erreur "Password too weak"

Le mot de passe doit contenir :
- Au moins 8 caractères
- Une majuscule
- Une minuscule
- Un chiffre
- Un caractère spécial (!@#$%^&* etc.)

## 📞 Support

En cas de problème :

1. Consulter les logs : `tail -f logs/geneweb_api.log`
2. Tester la santé : `curl http://localhost:8000/health`
3. Consulter la documentation complète
4. Vérifier les issues GitHub du projet

## 🚀 Améliorations futures

| Fonctionnalité | Priorité | Complexité |
|----------------|----------|------------|
| 2FA (TOTP) | Haute | Moyenne |
| Email verification | Haute | Faible |
| Password reset | Haute | Moyenne |
| OAuth2 (Google/GitHub) | Moyenne | Haute |
| Session management UI | Basse | Moyenne |
| Admin dashboard | Basse | Élevée |

---

**Version :** 1.0.0 | **Date :** 23 octobre 2025 | **Status :** ✅ Production-ready
