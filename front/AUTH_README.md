# Système d'Authentification GeneWeb

## 📋 Vue d'ensemble

Le système d'authentification a été mis en place pour sécuriser l'accès à l'application GeneWeb. Tous les utilisateurs doivent se connecter avant d'accéder aux fonctionnalités.

## 🎯 Fonctionnalités

### Page d'Authentification (`/auth`)
- **Connexion** : Formulaire de login avec email et mot de passe
- **Inscription** : Formulaire de création de compte
- **Validation** : Vérification des champs (email, mot de passe min 8 caractères, etc.)
- **Messages** : Affichage des erreurs et succès
- **Design** : Interface moderne avec Tailwind CSS

### Protection des Routes
- Toutes les routes sont protégées par `authGuard`
- Redirection automatique vers `/auth` si non connecté
- Token JWT stocké dans `localStorage`

### Service d'Authentification
- `AuthService` : Gestion de l'authentification
  - `login()` : Connexion utilisateur
  - `register()` : Inscription utilisateur
  - `logout()` : Déconnexion
  - `isAuthenticated()` : Vérification du statut
  - `getToken()` : Récupération du token

## 🚀 Utilisation

### Démarrage
1. Lancer le frontend Angular : `npm start` (port 2316)
2. Lancer le backend Python : `cd geneweb_python && make run-api` (port 8000)

### Première connexion
1. Accéder à `http://localhost:2316`
2. Vous serez redirigé vers `/auth`
3. Cliquer sur l'onglet "Inscription"
4. Créer un compte avec :
   - Nom d'utilisateur
   - Email
   - Mot de passe (min 8 caractères)
5. Se connecter avec les identifiants créés

### Déconnexion
- Bouton "Déconnexion" en haut à droite de la page d'accueil
- Redirection automatique vers `/auth`

## ⚙️ Configuration Backend (À FAIRE)

Pour que l'authentification fonctionne, le backend Python doit implémenter les endpoints suivants :

### Endpoints requis

#### 1. POST `/api/v1/auth/register`
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```
**Réponse 201** :
```json
{
  "message": "User created successfully",
  "user": {
    "id": "uuid",
    "username": "string",
    "email": "string"
  }
}
```

#### 2. POST `/api/v1/auth/login`
```json
{
  "email": "string",
  "password": "string"
}
```
**Réponse 200** :
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "string",
    "email": "string"
  }
}
```

### Sécurité Backend
- Hasher les mots de passe (bcrypt, argon2)
- Générer des tokens JWT
- Valider les tokens sur les routes protégées
- Implémenter un refresh token si nécessaire

## 📁 Structure des Fichiers

```
front/src/app/
├── pages/
│   └── auth/
│       ├── auth.component.ts       # Logique d'authentification
│       ├── auth.component.html     # Template login/register
│       └── auth.component.css      # Styles
├── services/
│   └── auth.service.ts             # Service d'authentification
├── guards/
│   └── auth.guard.ts               # Protection des routes
└── app.routes.ts                   # Routes avec guards
```

## 🔐 Sécurité

### Frontend
- Stockage sécurisé du token dans `localStorage`
- Validation côté client des formulaires
- Protection CSRF via headers HTTP
- Nettoyage des données sensibles à la déconnexion

### À implémenter côté Backend
- Validation des emails
- Limitation des tentatives de connexion
- Expiration des tokens
- HTTPS en production
- Protection CORS
- Rate limiting

## 🐛 Debug

### Si la redirection ne fonctionne pas
1. Vérifier la console du navigateur
2. Vérifier que le token est bien dans `localStorage`
3. Effacer `localStorage` : `localStorage.clear()`

### Si les requêtes API échouent
1. Vérifier que le backend est lancé sur le port 8000
2. Vérifier les CORS dans la configuration backend
3. Consulter la console réseau (F12 > Network)

## 📝 TODO Backend

- [ ] Créer le router `/api/v1/auth`
- [ ] Implémenter l'endpoint `/register`
- [ ] Implémenter l'endpoint `/login`
- [ ] Ajouter la gestion des tokens JWT
- [ ] Créer le modèle User dans la base de données
- [ ] Hasher les mots de passe
- [ ] Ajouter la validation des emails
- [ ] Implémenter le middleware d'authentification

## 🎨 Personnalisation

Pour modifier l'apparence de la page de login :
- Éditer `auth.component.html` pour le HTML
- Éditer `auth.component.css` pour les styles
- Les classes Tailwind peuvent être modifiées directement dans le HTML

---

**Note** : Le système est actuellement configuré pour appeler `http://localhost:8000/api/v1/auth/*`. Modifier `auth.service.ts` si l'URL de l'API est différente.
