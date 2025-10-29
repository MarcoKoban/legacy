# Configuration de l'API Frontend

## 🔗 URL de l'API

L'URL de l'API backend est maintenant configurée via les fichiers d'environnement Angular.

### Production (Fly.io)
```typescript
// src/environments/environment.prod.ts
export const environment = {
  production: true,
  apiUrl: 'https://geneweb-api.fly.dev/api/v1'
};
```

### Développement (Local)
```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1'
};
```

## 📝 Fichiers modifiés

Les fichiers suivants ont été mis à jour pour utiliser `environment.apiUrl` :

1. **`src/app/pages/list/list.component.ts`** - Liste des bases de données
   - Ancien: `http://localhost:8000/api/v1/database/databases`
   - Nouveau: `${environment.apiUrl}/database/databases`

2. **`src/app/pages/simple/simple.component.ts`** - Création de base de données
   - Ancien: `http://localhost:8000/api/v1/database/databases`
   - Nouveau: `${environment.apiUrl}/database/databases`

3. **`src/app/pages/auth/auth.component.ts`** - Authentification
   - Ancien: `http://localhost:8000/api/v1/auth/register`
   - Nouveau: `${environment.apiUrl}/auth/register`

## 🚀 Utilisation

### Build pour production (avec Fly.io)

```bash
cd front
ng build --configuration production
```

Cela utilisera automatiquement `https://geneweb-api.fly.dev/api/v1`

### Développement local

```bash
cd front
ng serve
```

Cela utilisera automatiquement `http://localhost:8000/api/v1`

## ✅ Test de la connexion

Pour tester si le frontend peut se connecter au backend :

1. **Lancer le frontend**
   ```bash
   cd front
   npm install
   ng serve
   ```

2. **Accéder à l'application**
   - Ouvrir http://localhost:4200
   - Aller sur la page "List" (liste des bases de données)
   - Si la page charge les bases de données, la connexion fonctionne ! ✅

3. **Vérifier dans la console du navigateur**
   - Ouvrir les DevTools (F12)
   - Onglet "Network"
   - Vérifier les requêtes vers `https://geneweb-api.fly.dev`

## 🐛 Dépannage

### Erreur CORS
Si vous voyez une erreur CORS dans la console :
```
Access to XMLHttpRequest at 'https://geneweb-api.fly.dev/api/v1/...' from origin 'http://localhost:4200' has been blocked by CORS policy
```

**Solution** : Le backend doit permettre `localhost:4200` dans la configuration CORS. Vérifier dans `geneweb_python/src/geneweb/api/main.py` :

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pour le développement
    # En production, restreindre aux domaines autorisés :
    # allow_origins=["https://votre-frontend.com", "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### L'API ne répond pas

1. **Vérifier que l'API est en ligne**
   ```bash
   curl https://geneweb-api.fly.dev/health/
   # Devrait retourner: {"status":"ok"}
   ```

2. **Vérifier le statut Fly.io**
   ```bash
   flyctl status --app geneweb-api
   # Health checks doivent être "passing"
   ```

3. **Consulter les logs**
   ```bash
   flyctl logs --app geneweb-api
   ```

### Changer l'URL de l'API

Pour changer l'URL de l'API (par exemple, si vous déployez sur un autre service) :

1. Modifier `src/environments/environment.prod.ts`
2. Rebuild le frontend : `ng build --configuration production`

## 📚 Endpoints disponibles

Avec `environment.apiUrl` configuré sur `https://geneweb-api.fly.dev/api/v1`, vous pouvez accéder à :

- **Health check** : `GET https://geneweb-api.fly.dev/health/`
- **Bases de données** : `GET https://geneweb-api.fly.dev/api/v1/database/databases`
- **Créer une DB** : `POST https://geneweb-api.fly.dev/api/v1/database/databases`
- **Auth Register** : `POST https://geneweb-api.fly.dev/api/v1/auth/register`
- **Documentation** : `GET https://geneweb-api.fly.dev/docs`

## 🎯 Prochaines étapes

1. ✅ Tester la page de liste des bases de données
2. ✅ Tester la création d'une nouvelle base de données
3. ✅ Vérifier que les requêtes arrivent bien sur Fly.io
4. 🔄 Mettre à jour les autres composants si nécessaire (add-family, etc.)

---

**Note** : En développement, assurez-vous que le backend local tourne sur `http://localhost:8000` !
