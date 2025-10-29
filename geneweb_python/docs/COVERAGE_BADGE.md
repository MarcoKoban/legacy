# Badge de Couverture de Code Automatique

## 📊 Fonctionnement

Le badge de couverture de code dans le README principal est **automatiquement mis à jour** après chaque exécution de tests.

### Quand le badge est mis à jour

Le badge est automatiquement mis à jour après :
- `make test` - Tous les tests
- `make test-fast` - Tests rapides (sans E2E)
- `make coverage` - Rapport de couverture détaillé

### Comment ça marche

1. **Pytest génère coverage.xml** pendant les tests
2. **Le script Python** (`scripts/update_coverage_badge.py`) :
   - Lit le fichier `coverage.xml`
   - Extrait le pourcentage de couverture
   - Génère un badge avec la couleur appropriée
   - Met à jour le `README.md` à la racine du projet

### Couleurs du badge

| Couverture | Couleur | Badge |
|------------|---------|-------|
| ≥ 90% | Vert vif (brightgreen) | ![90%](https://img.shields.io/badge/Coverage-90.0%25-brightgreen.svg) |
| 75-89% | Vert (green) | ![75%](https://img.shields.io/badge/Coverage-75.0%25-green.svg) |
| 60-74% | Jaune (yellow) | ![60%](https://img.shields.io/badge/Coverage-60.0%25-yellow.svg) |
| 40-59% | Orange (orange) | ![40%](https://img.shields.io/badge/Coverage-40.0%25-orange.svg) |
| < 40% | Rouge (red) | ![30%](https://img.shields.io/badge/Coverage-30.0%25-red.svg) |

### Mise à jour manuelle

Si vous voulez mettre à jour le badge manuellement :

```bash
cd geneweb_python
python3 scripts/update_coverage_badge.py
```

### Lien du badge

Le badge pointe vers le rapport HTML de couverture :
```
geneweb_python/htmlcov/index.html
```

Pour consulter le rapport détaillé de couverture :

```bash
# Ouvrir le rapport HTML dans le navigateur
cd geneweb_python
xdg-open htmlcov/index.html  # Linux
# ou
open htmlcov/index.html      # macOS
```

### Structure des fichiers

```
G-ING-900-PAR-9-1-legacy-22/
├── README.md                              # Badge de couverture ici
└── geneweb_python/
    ├── coverage.xml                       # Données de couverture
    ├── htmlcov/
    │   └── index.html                     # Rapport détaillé
    └── scripts/
        └── update_coverage_badge.py       # Script de mise à jour
```

### Intégration dans le workflow

Le workflow recommandé pour les développeurs :

```bash
# 1. Développer une feature avec TDD
# 2. Lancer les tests
make test

# 3. Le badge est automatiquement mis à jour
# 4. Vérifier le rapport de couverture si nécessaire
xdg-open htmlcov/index.html

# 5. Commiter les changements (y compris le README.md mis à jour)
git add .
git commit -m "feat: add new feature with tests"
```

### Objectifs de couverture

**Objectifs du projet :**
- 🎯 **Global** : ≥ 90%
- 🎯 **Core modules** : ≥ 95%
- 🎯 **API modules** : ≥ 90%
- 🎯 **Database** : ≥ 90%

**État actuel** : 75.5% (vert) ✅

### Désactiver la mise à jour automatique

Si vous voulez désactiver temporairement la mise à jour automatique, commentez les lignes dans le Makefile :

```makefile
test:
	pytest
	# @python3 scripts/update_coverage_badge.py || true
```

### Dépannage

**Le badge ne se met pas à jour ?**

1. Vérifiez que `coverage.xml` existe :
   ```bash
   ls -l geneweb_python/coverage.xml
   ```

2. Exécutez le script manuellement :
   ```bash
   cd geneweb_python
   python3 scripts/update_coverage_badge.py
   ```

3. Vérifiez les permissions :
   ```bash
   chmod +x scripts/update_coverage_badge.py
   ```

**Le pourcentage semble incorrect ?**

- Assurez-vous d'avoir exécuté tous les tests :
  ```bash
  make test
  ```
- Vérifiez le rapport détaillé :
  ```bash
  xdg-open geneweb_python/htmlcov/index.html
  ```

### Notes importantes

- ⚠️ Le badge est généré **localement** (pas via un service externe)
- ✅ Le lien pointe vers le rapport HTML local
- 📝 Le `README.md` à la racine **doit être commité** après les tests
- 🔄 Le badge reflète toujours la dernière exécution de tests locale
