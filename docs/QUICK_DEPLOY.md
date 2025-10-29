# 🚀 Guide de déploiement rapide

Guide rapide pour déployer l'application Geneweb en production.

## ⚡ Déploiement rapide

### Frontend (2 minutes)

```bash
cd front
npm install
npm run deploy
```

➡️ **Site en ligne** : https://geneweb.surge.sh

### Backend (3 minutes)

```bash
cd geneweb_python
fly auth login
fly deploy
```

➡️ **API en ligne** : https://geneweb-api.fly.dev

## 🔧 Configuration initiale (une seule fois)

### 1. Surge.sh (Frontend)

```bash
# Se connecter
npx surge login

# Récupérer le token pour GitHub Actions
npx surge token
```

Ajouter le token dans GitHub : **Settings** → **Secrets** → **Actions** → `SURGE_TOKEN`

### 2. Fly.io (Backend)

```bash
# Installer Fly CLI
curl -L https://fly.io/install.sh | sh

# Se connecter
fly auth login
```

### 3. CORS - Autoriser le frontend

Éditer `geneweb_python/fly.toml` ligne 24 :
```toml
GENEWEB_SECURITY_CORS_ORIGINS = '["https://geneweb.surge.sh","http://localhost:4200"]'
```

## 📝 Workflow quotidien

### Déployer une mise à jour du frontend

```bash
cd front
npm run deploy
```

### Déployer une mise à jour du backend

```bash
cd geneweb_python
fly deploy
```

### Déploiement automatique (via GitHub)

- **Push sur main** → Déploiement automatique du frontend
- **Merge PR sur main** → Déploiement automatique du frontend

## 🔗 URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | https://geneweb.surge.sh | Application Angular |
| Backend API | https://geneweb-api.fly.dev | API FastAPI |
| API Docs | https://geneweb-api.fly.dev/docs | Documentation Swagger |
| Health Check | https://geneweb-api.fly.dev/health | Statut du backend |

## 📖 Documentation complète

Pour plus de détails, consultez [DEPLOYMENT.md](./DEPLOYMENT.md)
