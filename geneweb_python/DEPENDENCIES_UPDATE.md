# Mise à jour des dépendances - API Geneweb

## 📦 Nouvelles dépendances ajoutées dans `requirements.txt`

### Middleware et Infrastructure
- `starlette>=0.27.0` - Support pour BaseHTTPMiddleware et fonctionnalités middleware

### Performance et Sérialisation
- `orjson>=3.9.0` - Sérialisation JSON ultra-rapide pour les réponses API

### Validation et Sécurité
- `email-validator>=2.1.0` - Validation d'emails pour les modèles Pydantic

## 🧪 Dépendances de test ajoutées dans `requirements-dev.txt`

### Tests API
- `httpx>=0.25.0` - Client HTTP asynchrone pour les tests
- `fastapi[test]>=0.104.0` - Utilitaires de test FastAPI

## ✅ Validation des dépendances

Toutes les dépendances ont été installées avec succès et l'API fonctionne correctement :

- ✅ Import API réussi
- ✅ Configuration environnementale fonctionnelle  
- ✅ Middlewares de sécurité opérationnels
- ✅ Système de monitoring actif
- ✅ Logging sécurisé configuré

## 🚀 Commandes de mise à jour

```bash
# Installation des dépendances principales
pip install -r requirements.txt

# Installation des dépendances de développement
pip install -r requirements-dev.txt

# Test de l'API
python -c "from src.geneweb.api.main import app; print('✅ API ready')"
```

## 📝 Notes importantes

1. **orjson** - Améliore significativement les performances de sérialisation JSON
2. **starlette** - Version explicite pour garantir la compatibilité des middlewares
3. **email-validator** - Nécessaire pour la validation Pydantic des adresses email
4. **httpx** - Essential pour les tests asynchrones d'API

La mise à jour est compatible avec l'infrastructure existante et n'introduit aucune breaking change.