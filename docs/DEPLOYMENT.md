# Guide de déploiement - Geneweb Application

Ce document décrit comment déployer le frontend Angular et le backend Python de l'application Geneweb.

## 📋 Table des matières

- [Architecture de déploiement](#architecture-de-déploiement)
- [Déploiement Frontend (Surge.sh)](#déploiement-frontend-surgesh)
- [Déploiement Backend (Fly.io)](#déploiement-backend-flyio)
- [Configuration CORS](#configuration-cors)
- [CI/CD GitHub Actions](#cicd-github-actions)
- [Dépannage](#dépannage)

## 🏗️ Architecture de déploiement

```
┌─────────────────────────────────────┐
│   Frontend - Angular 17             │
│   https://geneweb.surge.sh          │
│   Hébergement: Surge.sh             │
└──────────────┬──────────────────────┘
               │ API Calls (HTTPS)
               │
┌──────────────▼──────────────────────┐
│   Backend - FastAPI (Python)        │
│   https://geneweb-api.fly.dev       │
│   Hébergement: Fly.io               │
└─────────────────────────────────────┘
```

## 🎨 Déploiement Frontend (Surge.sh)

### Prérequis

- Node.js 18+
- npm
- Compte Surge.sh

### Déploiement manuel

1. **Installation des dépendances**
   ```bash
   cd front
   npm install
   ```

2. **Build de production**
   ```bash
   npm run build:prod
   ```

3. **Déploiement**
   ```bash
   npm run deploy
   ```
   
   L'application sera déployée sur : **https://geneweb.surge.sh**

### Configuration

#### Fichiers de configuration

- **`package.json`** : Scripts de build et déploiement
  ```json
  {
    "scripts": {
      "build:prod": "ng build --configuration production",
      "predeploy": "npm run build:prod && ./prepare-surge.sh",
      "deploy": "npx surge dist/front/browser geneweb.surge.sh"
    }
  }
  ```

- **`prepare-surge.sh`** : Script de préparation
  - Crée `200.html` à partir de `index.html` pour le routing SPA
  
- **`src/assets/CNAME`** : Définit le domaine personnalisé
  ```
  geneweb.surge.sh
  ```

### Changement de domaine

Pour changer le domaine Surge :

1. Modifier `src/assets/CNAME`
2. Modifier le script `deploy` dans `package.json`
3. Redéployer avec `npm run deploy`

## 🐍 Déploiement Backend (Fly.io)

### Prérequis

- Compte Fly.io
- Fly CLI installé : https://fly.io/docs/hands-on/install-flyctl/

### Déploiement manuel

1. **Se connecter à Fly.io**
   ```bash
   fly auth login
   ```

2. **Déployer l'application**
   ```bash
   cd geneweb_python
   fly deploy
   ```

   L'API sera accessible sur : **https://geneweb-api.fly.dev**

### Configuration

#### `fly.toml`

Configuration principale de l'application Fly.io :

```toml
app = 'geneweb-api'
primary_region = 'ams'

[build]
  dockerfile = 'Dockerfile.fly'

[env]
  GENEWEB_API_PORT = '8080'
  GENEWEB_SECURITY_CORS_ORIGINS = '["https://geneweb.surge.sh","http://localhost:4200"]'
  # ... autres variables
```

#### Variables d'environnement importantes

- `GENEWEB_API_PORT` : Port d'écoute (8080)
- `GENEWEB_SECURITY_CORS_ORIGINS` : Origines autorisées pour CORS
- `GENEWEB_API_WORKERS` : Nombre de workers Uvicorn (2)

### Secrets

Pour ajouter des secrets (clés API, tokens, etc.) :

```bash
fly secrets set SECRET_KEY=your-secret-key
fly secrets set ENCRYPTION_KEY=your-encryption-key
```

## 🔐 Configuration CORS

### Frontend autorisé

Le backend autorise les requêtes depuis :
- `https://geneweb.surge.sh` (production)
- `http://localhost:4200` (développement Angular)
- `http://localhost:2316` (développement local)

### Modifier les origines CORS

#### Option 1 : Modifier le code (défaut)

Éditer `geneweb_python/src/geneweb/api/config.py` :

```python
cors_origins: List[str] = Field(
    default=[
        "http://localhost:2316",
        "http://localhost:4200",
        "https://geneweb.surge.sh",
        # Ajouter vos domaines ici
    ],
)
```

#### Option 2 : Variable d'environnement Fly.io

Modifier `geneweb_python/fly.toml` :

```toml
GENEWEB_SECURITY_CORS_ORIGINS = '["https://geneweb.surge.sh","http://localhost:4200","https://nouveau-domaine.com"]'
```

Puis redéployer :
```bash
cd geneweb_python
fly deploy
```

## 🔄 CI/CD GitHub Actions

### Déploiement automatique du Frontend

Le workflow `.github/workflows/deploy-surge.yml` déploie automatiquement le frontend sur Surge.sh lors :
- D'un **push sur main**
- D'une **Pull Request mergée sur main**

#### Configuration du workflow

```yaml
name: Deploy Frontend to Surge

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
    types: [closed]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Build and Deploy
        run: |
          cd front
          npm ci
          npm run build:prod
          ./prepare-surge.sh
          npx surge dist/front/browser geneweb.surge.sh --token ${{ secrets.SURGE_TOKEN }}
```

### Configuration des secrets GitHub

1. Aller sur **GitHub** → **Settings** → **Secrets and variables** → **Actions**
2. Ajouter le secret **SURGE_TOKEN** :
   - Récupérer le token : `npx surge token`
   - Valeur : votre token Surge

### Déploiement automatique du Backend

Le backend peut être déployé automatiquement avec Fly.io :

1. Créer un token Fly.io :
   ```bash
   fly tokens create deploy
   ```

2. Ajouter le secret `FLY_API_TOKEN` dans GitHub

3. Créer `.github/workflows/deploy-backend.yml` :
   ```yaml
   name: Deploy Backend to Fly.io
   
   on:
     push:
       branches:
         - main
       paths:
         - 'geneweb_python/**'
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: superfly/flyctl-actions/setup-flyctl@master
         - run: flyctl deploy --remote-only
           working-directory: ./geneweb_python
           env:
             FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
   ```

## 🐛 Dépannage

### Erreur CORS sur le frontend

**Symptôme** : `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution** :
1. Vérifier que le domaine frontend est dans la liste CORS du backend
2. Vérifier `fly.toml` ligne `GENEWEB_SECURITY_CORS_ORIGINS`
3. Redéployer le backend : `fly deploy`

### Build frontend échoue

**Symptôme** : Erreurs `localStorage is not defined` lors du build

**Explication** : Ce sont des warnings SSR/prerendering, pas des erreurs bloquantes.

**Solution** : Le build continue et fonctionne. Pour supprimer les warnings, désactiver le prerendering dans `angular.json` :
```json
"prerender": false
```

### Surge déploiement échoue

**Symptôme** : `Error: Invalid credentials`

**Solution** :
1. Se reconnecter : `npx surge login`
2. Vérifier le token : `npx surge token`
3. Mettre à jour le secret GitHub `SURGE_TOKEN`

### Fly.io app ne démarre pas

**Vérifier les logs** :
```bash
fly logs
```

**Vérifier le status** :
```bash
fly status
```

**Redémarrer l'app** :
```bash
fly apps restart geneweb-api
```

## 📊 Monitoring et logs

### Frontend (Surge.sh)

Surge ne fournit pas de logs. Pour monitorer :
- Utiliser Google Analytics ou Plausible
- Ajouter Sentry pour le tracking d'erreurs

### Backend (Fly.io)

**Voir les logs en temps réel** :
```bash
fly logs
```

**Voir les métriques** :
```bash
fly dashboard geneweb-api
```

**Health check** :
- Health endpoint : `https://geneweb-api.fly.dev/health`
- Metrics : `https://geneweb-api.fly.dev/metrics`

## 🔗 URLs de production

- **Frontend** : https://geneweb.surge.sh
- **Backend API** : https://geneweb-api.fly.dev
- **API Documentation** : https://geneweb-api.fly.dev/docs
- **Health Check** : https://geneweb-api.fly.dev/health

## 📚 Ressources

- [Surge.sh Documentation](https://surge.sh/help/)
- [Fly.io Documentation](https://fly.io/docs/)
- [Angular Deployment Guide](https://angular.io/guide/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

## 🆘 Support

Pour toute question sur le déploiement :
1. Consulter cette documentation
2. Vérifier les logs (`fly logs` pour le backend)
3. Vérifier les GitHub Actions pour le frontend
4. Contacter l'équipe de développement
