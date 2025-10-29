# Guide de Démarrage Rapide - API Geneweb

## Installation Express (5 minutes)

### 1. Prérequis
```bash
# Vérifier Python version (3.9+ requis)
python --version

# Installer Git si nécessaire
sudo apt install git  # Ubuntu/Debian
brew install git       # macOS
```

### 2. Installation
```bash
# Cloner le projet
git clone <repository-url>
cd geneweb_python

# Installer les dépendances
pip install -r requirements.txt

# Configuration rapide
cp .env.example .env
```

### 3. Configuration minimale pour démarrer
```bash
# Éditer .env avec les paramètres de base
nano .env

# Paramètres essentiels pour le développement :
GENEWEB_API_DEBUG=true
GENEWEB_SECURITY_FORCE_HTTPS=false
GENEWEB_SECURITY_SECRET_KEY=dev-secret-key-change-me-in-production
GENEWEB_SECURITY_ENCRYPTION_KEY=dev-encryption-key-change-me-too
```

### 4. Premier démarrage
```bash
# Mode développement (HTTP autorisé)
python start_api.py --dev --reload

# L'API sera accessible sur : http://localhost:8000
```

### 5. Test rapide
```bash
# Test de santé
curl http://localhost:8000/health

# Documentation interactive
# Ouvrir dans le navigateur : http://localhost:8000/docs
```

## Tests des Fonctionnalités

### Health Checks
```bash
# Santé basique
curl http://localhost:8000/health

# Probe de vivacité
curl http://localhost:8000/health/live

# Probe de disponibilité
curl http://localhost:8000/health/ready

# Santé détaillée (depuis localhost)
curl http://localhost:8000/health/detailed
```

### Métriques (si activées)
```bash
# Métriques Prometheus
curl http://localhost:8000/metrics
```

### Test de sécurité
```bash
# Vérifications de sécurité
python start_api.py --check-only

# Test des headers de sécurité
curl -I http://localhost:8000/health
```

## Configuration Production

### 1. Certificats SSL
```bash
# Générer des certificats de test
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Ou utiliser Let's Encrypt
certbot certonly --standalone -d api.geneweb.com
```

### 2. Configuration production
```bash
# .env production
GENEWEB_API_DEBUG=false
GENEWEB_SECURITY_FORCE_HTTPS=true
GENEWEB_API_SSL_CERTFILE=/path/to/cert.pem
GENEWEB_API_SSL_KEYFILE=/path/to/key.pem

# Secrets sécurisés (générer des valeurs aléatoires)
GENEWEB_SECURITY_SECRET_KEY=your-super-secure-32-char-secret
GENEWEB_SECURITY_ENCRYPTION_KEY=your-super-secure-32-char-encrypt-key

# CORS restreint
GENEWEB_SECURITY_CORS_ORIGINS=["https://your-frontend.com"]
```

### 3. Démarrage production
```bash
# Avec SSL
python start_api.py --host 0.0.0.0 --port 8000 --workers 4
```

## Docker Express

### 1. Avec Docker
```bash
# Construction
docker build -t geneweb-api .

# Exécution simple
docker run -p 8000:8000 -e GENEWEB_API_DEBUG=true geneweb-api
```

### 2. Avec Docker Compose
```bash
# Démarrage complet (API + DB + Monitoring)
docker-compose up -d

# Vérifier les logs
docker-compose logs -f geneweb-api

# Arrêter
docker-compose down
```

## Résolution de Problèmes

### Erreurs communes

#### 1. Port déjà utilisé
```bash
# Trouver le processus utilisant le port 8000
lsof -i :8000

# Tuer le processus
kill -9 <PID>

# Ou utiliser un autre port
python start_api.py --port 8001
```

#### 2. Certificats SSL
```bash
# Vérifier les certificats
openssl x509 -in cert.pem -text -noout

# Permissions des fichiers
chmod 600 key.pem
chmod 644 cert.pem
```

#### 3. Dépendances manquantes
```bash
# Réinstaller les dépendances
pip install --upgrade -r requirements.txt

# Ou avec un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### 4. Variables d'environnement
```bash
# Vérifier que .env est lu
python -c "from geneweb.api.config import settings; print(settings.debug)"

# Forcer le rechargement
export GENEWEB_API_DEBUG=true
```

### Logs de débogage
```bash
# Logs en temps réel
tail -f /var/log/geneweb/api.log

# Logs avec filtrage
python start_api.py --dev | grep ERROR

# Augmenter le niveau de log
export GENEWEB_LOG_LOG_LEVEL=DEBUG
```

## Développement

### Configuration IDE
```bash
# Pour VSCode - extensions recommandées
# - Python
# - Pylance
# - Black Formatter
# - isort

# Configuration des outils de développement
pip install -r requirements-dev.txt
pre-commit install
```

### Tests et qualité de code
```bash
# Linting
flake8 src/ start_api.py

# Formatage
black src/ start_api.py
isort src/ start_api.py

# Tests de sécurité
python start_api.py --check-only

# Tests unitaires (quand disponibles)
pytest tests/
```

## Prochaines étapes

1. **Lecture de la documentation complète** : [`docs/API/API_DOCUMENTATION.md`](API_DOCUMENTATION.md)
2. **Configuration de la base de données** : PostgreSQL recommandé
3. **Ajout d'endpoints métier** : Personnes, familles, événements
4. **Configuration du monitoring** : Prometheus + Grafana
5. **Déploiement production** : Reverse proxy, certificats, monitoring

## Support

- **Documentation complète** : [`docs/API/API_DOCUMENTATION.md`](API_DOCUMENTATION.md)
- **Sécurité** : [`SECURITY.md`](../SECURITY.md)
- **Configuration** : [`.env.example`](../.env.example)
- **Docker** : [`docker-compose.yml`](../docker-compose.yml)

---

🚀 **L'API Geneweb est maintenant prête à l'emploi !**