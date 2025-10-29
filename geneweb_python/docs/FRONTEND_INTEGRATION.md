# Intégration Frontend - Backend Fly.io

Ce guide explique comment connecter votre frontend Angular à l'API déployée sur Fly.io.

## 🌐 URL de l'API

**URL de production** : `https://geneweb-api.fly.dev`

## 🔧 Configuration Frontend

### 1. Configuration Angular

Créer ou modifier `front/src/environments/environment.prod.ts` :

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://geneweb-api.fly.dev',
  apiVersion: 'v1'
};
```

Pour le développement local, garder `environment.ts` :

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',  // API locale
  apiVersion: 'v1'
};
```

### 2. Service HTTP Angular

Exemple de service pour consommer l'API :

```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Headers communs
  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    });
  }

  // Headers avec authentification
  private getAuthHeaders(token: string): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  // Health check
  healthCheck(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health/`);
  }

  // Exemple : Récupérer les personnes
  getPersons(): Observable<any> {
    const token = localStorage.getItem('auth_token');
    return this.http.get(`${this.apiUrl}/api/v1/persons/`, {
      headers: this.getAuthHeaders(token)
    });
  }

  // Exemple : Authentification
  login(username: string, password: string): Observable<any> {
    const body = new URLSearchParams();
    body.set('username', username);
    body.set('password', password);

    return this.http.post(`${this.apiUrl}/api/v1/auth/token`, body.toString(), {
      headers: new HttpHeaders({
        'Content-Type': 'application/x-www-form-urlencoded'
      })
    });
  }
}
```

### 3. Configuration CORS

L'API est déjà configurée pour accepter les requêtes CORS. Vérifier dans le backend :

```python
# src/geneweb/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, restreindre aux domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**⚠️ Important pour la production** : Restreindre `allow_origins` aux domaines de votre frontend :

```python
allow_origins=[
    "https://votre-frontend.com",
    "https://www.votre-frontend.com"
]
```

## 📡 Endpoints disponibles

### Authentification

```typescript
// Login
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded
Body: username=xxx&password=xxx

// Register
POST /api/v1/auth/register
Content-Type: application/json
Body: {
  "username": "user",
  "email": "user@example.com",
  "password": "securepass"
}

// Refresh token
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

### Personnes (Genealogy)

```typescript
// Lister les personnes
GET /api/v1/persons/
Authorization: Bearer <token>

// Créer une personne
POST /api/v1/persons/
Authorization: Bearer <token>
Body: { "first_name": "John", "last_name": "Doe", ... }

// Récupérer une personne
GET /api/v1/persons/{person_id}
Authorization: Bearer <token>

// Mettre à jour une personne
PUT /api/v1/persons/{person_id}
Authorization: Bearer <token>

// Supprimer une personne
DELETE /api/v1/persons/{person_id}
Authorization: Bearer <token>
```

### GDPR

```typescript
// Anonymiser une personne
POST /api/v1/gdpr/anonymize/{person_id}
Authorization: Bearer <token>

// Exporter les données
GET /api/v1/gdpr/export/{person_id}
Authorization: Bearer <token>

// Supprimer définitivement
DELETE /api/v1/gdpr/delete/{person_id}
Authorization: Bearer <token>
```

### Health & Monitoring

```typescript
// Health check simple
GET /health/
// Response: {"status": "ok"}

// Health check détaillé
GET /health/detailed
// Response: { "status": "healthy", "database": "connected", ... }

// Documentation interactive
GET /docs
```

## 🔐 Gestion de l'authentification

### Stocker le token

```typescript
// Après login réussi
login(username: string, password: string) {
  this.apiService.login(username, password).subscribe(
    response => {
      // Stocker le token
      localStorage.setItem('auth_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      
      // Rediriger l'utilisateur
      this.router.navigate(['/dashboard']);
    },
    error => {
      console.error('Login failed', error);
    }
  );
}
```

### Intercepteur HTTP (recommandé)

Créer un intercepteur pour ajouter automatiquement le token :

```typescript
import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = localStorage.getItem('auth_token');
    
    if (token) {
      const cloned = req.clone({
        headers: req.headers.set('Authorization', `Bearer ${token}`)
      });
      return next.handle(cloned);
    }
    
    return next.handle(req);
  }
}
```

Enregistrer dans `app.module.ts` :

```typescript
import { HTTP_INTERCEPTORS } from '@angular/common/http';

providers: [
  { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
]
```

## 🧪 Tests de l'API

### Test avec curl

```bash
# Health check
curl https://geneweb-api.fly.dev/health/

# Login
curl -X POST "https://geneweb-api.fly.dev/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"

# Appel authentifié
TOKEN="votre_token_ici"
curl "https://geneweb-api.fly.dev/api/v1/persons/" \
  -H "Authorization: Bearer $TOKEN"
```

### Test avec Postman

1. Créer une nouvelle collection "Geneweb API"
2. Configurer une variable `baseUrl = https://geneweb-api.fly.dev`
3. Ajouter un dossier "Auth" avec les endpoints de connexion
4. Ajouter les autres endpoints organisés par ressource

## ⚠️ Gestion des erreurs

### Codes de statut HTTP

```typescript
// Intercepteur pour gérer les erreurs
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';

intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
  return next.handle(req).pipe(
    catchError(error => {
      switch(error.status) {
        case 401:
          // Token expiré ou invalide
          this.router.navigate(['/login']);
          break;
        case 403:
          // Accès refusé
          console.error('Access denied');
          break;
        case 429:
          // Rate limit dépassé
          console.error('Too many requests, please slow down');
          break;
        case 500:
          // Erreur serveur
          console.error('Server error');
          break;
      }
      return throwError(error);
    })
  );
}
```

## 🚀 Déploiement du Frontend

### Option 1 : Vercel (Recommandé pour Angular)

```bash
# Installer Vercel CLI
npm i -g vercel

# Dans le dossier front/
cd front
vercel

# Configurer les variables d'environnement
vercel env add PRODUCTION_API_URL
# Entrer: https://geneweb-api.fly.dev
```

### Option 2 : Netlify

```bash
# Installer Netlify CLI
npm i -g netlify-cli

# Build
npm run build -- --configuration production

# Deploy
netlify deploy --prod --dir=dist/geneweb-front
```

### Option 3 : Fly.io (même plateforme que le backend)

```bash
cd front

# Créer un Dockerfile pour le frontend
cat > Dockerfile <<EOF
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build -- --configuration production

FROM nginx:alpine
COPY --from=build /app/dist/geneweb-front /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF

# Déployer
flyctl launch
flyctl deploy
```

## 📊 Monitoring de l'API depuis le Frontend

### Service de monitoring

```typescript
@Injectable({
  providedIn: 'root'
})
export class ApiHealthService {
  private healthCheckInterval: any;
  public apiStatus$ = new BehaviorSubject<'online' | 'offline'>('online');

  constructor(private http: HttpClient) {
    this.startHealthCheck();
  }

  startHealthCheck() {
    this.healthCheckInterval = setInterval(() => {
      this.http.get('https://geneweb-api.fly.dev/health/')
        .pipe(timeout(5000))
        .subscribe(
          () => this.apiStatus$.next('online'),
          () => this.apiStatus$.next('offline')
        );
    }, 30000); // Check toutes les 30 secondes
  }

  ngOnDestroy() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
  }
}
```

### Afficher le statut dans l'UI

```typescript
// Component
export class AppComponent {
  apiStatus$ = this.healthService.apiStatus$;

  constructor(private healthService: ApiHealthService) {}
}
```

```html
<!-- Template -->
<div class="api-status" [class.offline]="(apiStatus$ | async) === 'offline'">
  <span *ngIf="(apiStatus$ | async) === 'online'">🟢 API Online</span>
  <span *ngIf="(apiStatus$ | async) === 'offline'">🔴 API Offline</span>
</div>
```

## 🔒 Sécurité

### Bonnes pratiques

1. **Ne jamais exposer les tokens dans l'URL**
   ```typescript
   // ❌ Mauvais
   GET /api/persons?token=xxx
   
   // ✅ Bon
   GET /api/persons
   Authorization: Bearer xxx
   ```

2. **Valider les entrées côté frontend ET backend**

3. **Utiliser HTTPS uniquement en production**

4. **Implémenter un refresh token automatique**
   ```typescript
   if (error.status === 401) {
     // Token expiré, essayer de le rafraîchir
     return this.refreshToken().pipe(
       switchMap(newToken => {
         // Réessayer la requête avec le nouveau token
         return next.handle(this.addToken(req, newToken));
       })
     );
   }
   ```

5. **Nettoyer les tokens à la déconnexion**
   ```typescript
   logout() {
     localStorage.removeItem('auth_token');
     localStorage.removeItem('refresh_token');
     this.router.navigate(['/login']);
   }
   ```

## 📝 Variables d'environnement Frontend

### Angular

Créer `front/src/environments/environment.fly.ts` :

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://geneweb-api.fly.dev',
  apiVersion: 'v1',
  enableDebug: false,
  apiTimeout: 30000  // 30 secondes
};
```

### Build pour la production

```bash
ng build --configuration production
# ou
ng build --prod
```

## 🎯 Checklist d'intégration

- [ ] Configurer l'URL de l'API dans environment.prod.ts
- [ ] Créer les services Angular pour consommer l'API
- [ ] Implémenter l'intercepteur d'authentification
- [ ] Gérer les erreurs HTTP (401, 403, 429, 500)
- [ ] Tester tous les endpoints depuis le frontend
- [ ] Implémenter le refresh token
- [ ] Ajouter un indicateur de statut de l'API
- [ ] Configurer CORS correctement
- [ ] Déployer le frontend
- [ ] Tester l'application complète en production

## 📚 Ressources

- [Documentation API (Swagger)](https://geneweb-api.fly.dev/docs)
- [Angular HttpClient](https://angular.io/guide/http)
- [JWT Authentication](https://jwt.io/)
- [CORS Explained](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

---

**Contact** : Pour toute question sur l'API, consulter la documentation Swagger ou les logs Fly.io.
