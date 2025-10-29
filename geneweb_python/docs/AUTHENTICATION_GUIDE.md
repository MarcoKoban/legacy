# Guide d'Authentification - Documentation Complète

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Endpoints API](#endpoints-api)
- [Exemples d'utilisation](#exemples-dutilisation)
- [Configuration](#configuration)
- [Sécurité](#sécurité)
- [Dépannage](#dépannage)

## 🔐 Vue d'ensemble

Système d'authentification JWT moderne pour Geneweb avec :

| Technologie | Usage |
|-------------|-------|
| **JWT** | Tokens stateless avec JTI pour révocation |
| **Bcrypt** | Hachage mots de passe (salt auto) |
| **SQLAlchemy** | Stockage users/sessions/blacklist |
| **FastAPI** | Framework API avec OpenAPI/Swagger |
| **Pydantic** | Validation données |

### Caractéristiques

✅ Access tokens (30 min) + Refresh tokens (7 jours)  
✅ Token blacklist pour révocation instantanée  
✅ 4 rôles RBAC : VIEWER, FAMILY, EDITOR, ADMIN  
✅ Audit complet avec logs cryptographiques  
✅ Rate limiting anti-brute force  
✅ HTTPS enforcement production  
✅ Validation force mots de passe  

## 🏗️ Architecture

### Structure JWT

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "jti": "unique-token-id",       // Pour blacklist
    "sub": "user-uuid",              // User ID
    "username": "demo",
    "role": "family",
    "permissions": ["view_public_persons", ...],
    "exp": 1234567890,               // Expiration timestamp
    "iat": 1234567800,               // Issued at
    "type": "access"                 // access | refresh
  },
  "signature": "HMACSHA256(...)"
}
```

### Flow d'authentification

```
Client                          API                         Database
  │                              │                              │
  ├──POST /login────────────────>│                              │
  │  {user, pwd}                 │                              │
  │                              ├──Query user─────────────────>│
  │                              │<─────────────────────────────┤
  │                              │  Verify bcrypt hash          │
  │                              │  Generate JWT (JTI)          │
  │                              ├──Create session─────────────>│
  │<─────────────────────────────┤                              │
  │  {access_token, refresh}     │                              │
  │                              │                              │
  ├──GET /persons───────────────>│                              │
  │  Authorization: Bearer xxx   │                              │
  │                              │  Verify JWT signature        │
  │                              ├──Check blacklist────────────>│
  │                              │<─────────────────────────────┤
  │                              │  Check permissions           │
  │<─────────────────────────────┤                              │
  │  {data}                      │                              │
  │                              │                              │
  ├──POST /logout───────────────>│                              │
  │  Authorization: Bearer xxx   │                              │
  │                              ├──Add to blacklist───────────>│
  │<─────────────────────────────┤                              │
  │  {success}                   │                              │
```

## 🔌 Endpoints API

### POST /api/v1/auth/login

Authentifie et retourne tokens JWT.

**Request:**
```json
{
  "username": "demo",
  "password": "demo1234"
}
```

**Response 200:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "550e8400-...",
    "username": "demo",
    "email": "demo@geneweb.local",
    "role": "family"
  }
}
```

**Errors:**
- `401` - Credentials invalides
- `403` - Compte désactivé/verrouillé
- `429` - Rate limit dépassé

---

### POST /api/v1/auth/refresh

Rafraîchit access token avec refresh token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response 200:**
```json
{
  "access_token": "eyJ...",      // Nouveau
  "refresh_token": "eyJ...",      // Nouveau (rotation)
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### POST /api/v1/auth/logout

Révoque token (blacklist).

**Headers:**
```
Authorization: Bearer eyJ...
```

**Response 200:**
```json
{
  "message": "Successfully logged out",
  "detail": "Token has been revoked"
}
```

---

### GET /api/v1/auth/me

Info utilisateur connecté.

**Headers:**
```
Authorization: Bearer eyJ...
```

**Response 200:**
```json
{
  "id": "550e8400-...",
  "username": "demo",
  "email": "demo@geneweb.local",
  "full_name": "Demo User",
  "role": "family",
  "is_active": true,
  "created_at": "2025-10-23T10:00:00Z",
  "last_login": "2025-10-23T14:30:00Z"
}
```

---

### POST /api/v1/auth/register

Créer nouveau compte.

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "password": "SecureP@ssw0rd!",
  "role": "user"
}
```

**Response 201:**
```json
{
  "id": "660e8400-...",
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true
}
```

**Errors:**
- `409` - Username/email déjà utilisé
- `400` - Mot de passe trop faible

---

### POST /api/v1/auth/change-password

Changer mot de passe.

**Headers:**
```
Authorization: Bearer eyJ...
```

**Request:**
```json
{
  "current_password": "OldP@ss",
  "new_password": "NewP@ss123!",
  "confirm_password": "NewP@ss123!"
}
```

**Response 200:**
```json
{
  "message": "Password changed successfully"
}
```

## 💻 Exemples d'utilisation

### Python (requests)

```python
import requests

API = "http://localhost:8000/api/v1/auth"

# 1. Login
r = requests.post(f"{API}/login", json={
    "username": "demo",
    "password": "demo1234"
})
tokens = r.json()
token = tokens["access_token"]

# 2. Requête authentifiée
headers = {"Authorization": f"Bearer {token}"}
user = requests.get(f"{API}/me", headers=headers).json()
print(f"Connecté: {user['username']}")

# 3. Rafraîchir
r = requests.post(f"{API}/refresh", json={
    "refresh_token": tokens["refresh_token"]
})
token = r.json()["access_token"]

# 4. Logout
requests.post(f"{API}/logout", headers=headers)
```

### JavaScript (fetch)

```javascript
const API = "http://localhost:8000/api/v1/auth";

// 1. Login
const login = await fetch(`${API}/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "demo",
    password: "demo1234"
  })
});
const { access_token, refresh_token } = await login.json();

// Sauvegarder
localStorage.setItem("token", access_token);
localStorage.setItem("refresh", refresh_token);

// 2. Requête authentifiée
const user = await fetch(`${API}/me`, {
  headers: { "Authorization": `Bearer ${access_token}` }
}).then(r => r.json());

// 3. Auto-refresh sur 401
async function fetchWithRefresh(url, options) {
  let r = await fetch(url, options);
  
  if (r.status === 401) {
    // Rafraîchir le token
    const refresh = await fetch(`${API}/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        refresh_token: localStorage.getItem("refresh")
      })
    });
    const tokens = await refresh.json();
    localStorage.setItem("token", tokens.access_token);
    
    // Réessayer avec nouveau token
    options.headers.Authorization = `Bearer ${tokens.access_token}`;
    r = await fetch(url, options);
  }
  
  return r;
}
```

### cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}' \
  | jq -r '.access_token' > token.txt

# Utiliser token
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $(cat token.txt)"

# Logout
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $(cat token.txt)"
```

## ⚙️ Configuration

### Variables d'environnement

Créer `.env` dans `geneweb_python/` :

```bash
# Secret JWT (32+ caractères OBLIGATOIRE)
GENEWEB_SECURITY_SECRET_KEY=your-32-char-secret-key-here

# Optionnel (valeurs par défaut)
# GENEWEB_SECURITY_RATE_LIMIT_PER_MINUTE=100
# GENEWEB_SECURITY_RATE_LIMIT_BURST=20
# GENEWEB_SECURITY_FORCE_HTTPS=false  # true en prod
# GENEWEB_API_DEBUG=false
# GENEWEB_API_HOST=0.0.0.0
# GENEWEB_API_PORT=8000
```

### Durée des tokens

Défini dans `src/geneweb/api/security/auth.py` :

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30   # 30 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7       # 7 jours
```

### Générer clé secrète

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Exemple: xN5jK_vHp2Qr8wLm3nB6yT9cA1fD4gE7
```

## 🔒 Sécurité

### Protections implémentées

| Protection | Description |
|------------|-------------|
| **Bcrypt** | Hachage avec cost=12, salt auto |
| **JWT JTI** | ID unique pour révocation |
| **Blacklist** | In-memory (dev), Redis recommandé (prod) |
| **Rate limiting** | 100 req/min, burst 20 |
| **HTTPS** | Forcé en prod (redirect HTTP→HTTPS) |
| **CORS** | Whitelist configurable |
| **Timing attack** | Délai aléatoire sur endpoints auth |
| **Audit** | Tous événements loggés |

### Validation mots de passe

Critères requis :
- ✅ Longueur ≥ 8 caractères
- ✅ 1 majuscule (A-Z)
- ✅ 1 minuscule (a-z)
- ✅ 1 chiffre (0-9)
- ✅ 1 caractère spécial (!@#$%^&*)
- ✅ Pas de mots de passe communs (password, 123456...)
- ✅ Pas de séquences (abc, 123, qwerty)
- ✅ Pas de répétitions excessives (aaaa)


### Bonnes pratiques

**Client :**
- ✅ Stocker refresh token en httpOnly cookie (pas localStorage)
- ✅ Implémenter auto-refresh avant expiration
- ✅ Nettoyer tokens au logout
- ✅ Rediriger sur /login si 401

**Serveur :**
- ✅ SECRET_KEY ≥ 32 caractères (généré aléatoirement)
- ✅ PostgreSQL en production (pas SQLite)
- ✅ Redis pour blacklist (scalabilité)
- ✅ HTTPS uniquement (force_https=true)
- ✅ CORS restrictif (domaines autorisés uniquement)
- ✅ Monitoring alertes tentatives login échouées

## 🆘 Dépannage

### Erreur "Invalid token"

**Causes :**
- Token expiré (30 min pour access)
- Token révoqué (logout)
- Signature invalide

**Solution :**
```python
# Utiliser refresh token
r = requests.post("/api/v1/auth/refresh", 
    json={"refresh_token": refresh_token})
new_token = r.json()["access_token"]
```

### Erreur "Account is locked"

**Cause :** Trop de tentatives échouées

**Solution :**
- Attendre expiration du verrouillage
- Contacter admin pour déblocage manuel

### Erreur "Password too weak"

**Requis :**
- 8+ caractères
- Majuscule + minuscule + chiffre + spécial
- Pas de mots communs

**Exemple valide :**
```
MyP@ssw0rd2025!
```

### Debug

```bash
# Vérifier santé service
curl http://localhost:8000/api/v1/auth/health

# Logs
tail -f logs/geneweb_api.log

# Test complet
python test_authentication.py
```

---

## 📚 Ressources

- **Swagger UI :** http://localhost:8000/docs
- **ReDoc :** http://localhost:8000/redoc
- **Code source :** `geneweb_python/src/geneweb/api/routers/auth.py`
- **Tests :** `geneweb_python/test_authentication.py`

---

**Dernière mise à jour :** 23 octobre 2025  
**Version :** 1.0.0  
**Status :** Production-ready
