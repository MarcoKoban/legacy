# 🚀 Déploiement Geneweb API - Guide Rapide

Ce document résume le déploiement de l'API Geneweb sur Fly.io.

## ✅ Statut du déploiement

- **Application** : `geneweb-api`
- **URL** : https://geneweb-api.fly.dev
- **Région** : Amsterdam (ams)
- **Statut** : ✅ Déployée et fonctionnelle
- **Health checks** : ✅ 2/2 passing
- **Base de données** : ✅ PostgreSQL connectée

## 🔗 URLs importantes

- **API Production** : https://geneweb-api.fly.dev
- **Health Check** : https://geneweb-api.fly.dev/health/
- **Documentation API** : https://geneweb-api.fly.dev/docs
- **Dashboard Fly.io** : https://fly.io/apps/geneweb-api/monitoring

## 📁 Fichiers de configuration

| Fichier | Description |
|---------|-------------|
| `fly.toml` | Configuration Fly.io (ports, région, env vars) |
| `Dockerfile.fly` | Image Docker optimisée pour Fly.io |
| `fly_start.py` | Script de démarrage personnalisé |
| `.dockerignore` | Fichiers exclus du build Docker |
| `generate_secrets.py` | Générateur de clés de sécurité |

## 🎯 Commandes essentielles

### Déployer

```bash
cd geneweb_python
flyctl deploy
```

### Voir les logs

```bash
flyctl logs --app geneweb-api
```

### Vérifier l'état

```bash
flyctl status --app geneweb-api
```

### Gérer les secrets

```bash
# Lister
flyctl secrets list --app geneweb-api

# Définir
flyctl secrets set KEY=value --app geneweb-api
```

## 🔐 Secrets configurés

Les secrets suivants sont déjà configurés sur Fly.io :

- ✅ `GENEWEB_SECURITY_SECRET_KEY`
- ✅ `GENEWEB_SECURITY_ENCRYPTION_KEY`
- ✅ `DATABASE_URL` (auto-configuré)

## 🗄️ Base de données

- **Nom** : `geneweb-db`
- **Type** : PostgreSQL
- **Région** : Amsterdam (ams)
- **Connexion** : Interne Fly.io (*.flycast)

### Commandes DB

```bash
# Se connecter à la DB
flyctl postgres connect --app geneweb-db

# Voir les infos
flyctl postgres db list --app geneweb-db
```

## 📊 Coûts

**Actuel : 0€/mois** (tier gratuit Fly.io)

- 1 machine shared-cpu-1x (256MB RAM)
- 1 volume de 1GB
- 1 PostgreSQL (256MB RAM, 1GB storage)

## 🔧 Frontend - Configuration

### URL à utiliser dans le frontend

```typescript
// environment.prod.ts
export const environment = {
  production: true,
  apiUrl: 'https://geneweb-api.fly.dev'
};
```

### Test rapide

```bash
# Health check
curl https://geneweb-api.fly.dev/health/

# Devrait retourner
{"status":"ok"}
```

## 📚 Documentation complète

- **Déploiement Fly.io** : Voir [DEPLOYMENT_FLY.md](./DEPLOYMENT_FLY.md)
- **Intégration Frontend** : Voir [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md)

## 🐛 Problèmes résolus

### ✅ Health check 400 Bad Request
**Cause** : TrustedHostMiddleware bloquait Fly.io  
**Solution** : Détection automatique via `FLY_APP_NAME`

### ✅ Health check 429 Too Many Requests
**Cause** : Rate limiting sur `/health/`  
**Solution** : Exclusion de `/health/` du rate limiting

### ✅ Port mismatch
**Cause** : Application sur 8000, Fly.io attend 8080  
**Solution** : Port fixé à 8080 partout

### ✅ Région Frankfurt (cdg) - IPv6
**Cause** : Problèmes infrastructure Fly.io  
**Solution** : Migration vers Amsterdam (ams)

## 📞 Support

- **Logs** : `flyctl logs --app geneweb-api`
- **Status Fly.io** : https://status.flyio.net/
- **Documentation** : https://fly.io/docs/

## 🎓 Pour aller plus loin

### Scaling

```bash
# Augmenter le nombre d'instances
flyctl scale count 2 --app geneweb-api

# Augmenter la RAM
flyctl scale vm shared-cpu-2x --app geneweb-api
```

### Monitoring

```bash
# Dashboard web
flyctl dashboard --app geneweb-api

# Métriques
curl https://geneweb-api.fly.dev/metrics
```

### Rollback

```bash
# Lister les versions
flyctl releases --app geneweb-api

# Revenir en arrière
flyctl releases rollback <version> --app geneweb-api
```

## ✨ Prochaines étapes

1. **Configurer le frontend** pour utiliser `https://geneweb-api.fly.dev`
2. **Tester l'intégration** complète frontend-backend
3. **Configurer CORS** pour restreindre aux domaines autorisés
4. **Mettre en place des sauvegardes** DB automatiques
5. **Configurer le monitoring** (alertes, métriques)

---

**Déploiement réalisé** : 23 octobre 2025  
**Version** : 15  
**Statut** : ✅ Production Ready
