# 🔧 Configuration Pre-commit - Guide Complet

## Pourquoi pre-commit ne s'installe pas automatiquement ?

### Explication technique

Pre-commit modifie les fichiers dans `.git/hooks/` qui sont :
- ❌ **Non versionnés** par Git (par design)
- 🔒 **Locaux** à chaque clone du dépôt
- ⚠️ **Ne peuvent pas** être synchronisés via `git pull/push`

**Raisons de sécurité** :
Git ne synchronise pas les hooks pour éviter l'exécution de code malveillant. Chaque développeur doit explicitement installer les hooks sur sa machine.

## Solutions proposées

### ✅ Solution 1 : Commande automatique (Recommandée)

Utilisez `make dev-setup` qui fait tout automatiquement :

```bash
cd geneweb_python
make dev-setup
```

**Ce que fait cette commande :**
1. ✅ Installe toutes les dépendances de développement
2. ✅ Configure automatiquement pre-commit
3. ✅ Vérifie que tout est correctement installé
4. ✅ Affiche les prochaines étapes

### ✅ Solution 2 : Script Python

Utilisez le script d'installation automatique :

```bash
python scripts/setup_dev.py
```

### ✅ Solution 3 : Installation manuelle

Si vous préférez le contrôle manuel :

```bash
# 1. Installer les dépendances
pip install -e ".[dev]"

# 2. Installer les hooks pre-commit
pre-commit install

# 3. Vérifier l'installation
pre-commit run --all-files
```

## Hooks configurés

Les hooks suivants s'exécutent **automatiquement** avant chaque commit :

### 1. 🎨 Black - Formatage automatique
- Reformate le code Python selon PEP8
- Ligne max : 88 caractères
- **Effet** : Votre code sera toujours bien formaté

### 2. 📦 isort - Organisation des imports
- Trie et organise les imports
- Sépare stdlib, third-party, et local
- **Effet** : Imports cohérents dans tout le projet

### 3. 🔍 flake8 - Vérification du style
- Vérifie le respect de PEP8
- Détecte les erreurs de style
- **Effet** : Code propre et sans erreurs

### 4. ✅ pytest - Tests automatiques
- Lance les tests avant le commit
- Empêche les commits avec tests cassés
- **Effet** : Garantit que le code fonctionne

### 5. 📋 Vérifications diverses
- YAML valide
- Pas de gros fichiers
- Pas de conflits de merge
- **Effet** : Commits propres et sûrs

## Utilisation quotidienne

### Commit normal

```bash
git add .
git commit -m "feat: ajouter nouvelle fonctionnalité"

# Les hooks s'exécutent automatiquement :
# check yaml...............Passed
# check for added large files...Passed
# black....................Passed
# isort....................Passed
# flake8...................Passed
# pytest...................Passed
```

### Si un hook échoue

```bash
git commit -m "fix: corriger bug"

# black....................Failed
# - hook id: black
# - files were modified by this hook

# Black a reformaté vos fichiers automatiquement !
# Ajoutez les changements et recommittez :
git add .
git commit -m "fix: corriger bug"
```

### Tester les hooks manuellement

```bash
# Tester sur les fichiers modifiés
pre-commit run

# Tester sur tous les fichiers
pre-commit run --all-files

# Tester un hook spécifique
pre-commit run black
pre-commit run pytest
```

### Bypass les hooks (déconseillé)

```bash
# En cas d'urgence uniquement !
git commit --no-verify -m "hotfix: emergency"
```

⚠️ **Attention** : Utilisez `--no-verify` uniquement en cas d'urgence absolue.

## Dépannage

### Les hooks ne s'exécutent pas

```bash
# Vérifier l'installation
pre-commit --version

# Réinstaller
pre-commit install --force

# Tester
pre-commit run --all-files
```

### Erreur "pre-commit: command not found"

```bash
# Installer pre-commit
pip install pre-commit

# OU utiliser make
make dev-setup
```

### Les tests sont trop lents

Si les tests ralentissent trop les commits, vous pouvez :

```bash
# Désactiver temporairement pytest dans les hooks
# Éditez .pre-commit-config.yaml et commentez le hook pytest

# OU exécutez les tests manuellement après
git commit --no-verify -m "wip: work in progress"
make test
```

## Meilleures pratiques

### ✅ À faire
- ✅ Toujours installer les hooks après avoir cloné
- ✅ Laisser les hooks s'exécuter normalement
- ✅ Corriger les erreurs signalées par les hooks
- ✅ Tester avec `pre-commit run` avant de committer

### ❌ À éviter
- ❌ Utiliser `--no-verify` systématiquement
- ❌ Ignorer les avertissements des hooks
- ❌ Committer du code non formaté
- ❌ Désactiver les hooks sans raison

## Intégration CI/CD

Les mêmes vérifications sont également exécutées en CI/CD :

```yaml
# .github/workflows/ci.yml
- name: Run pre-commit checks
  run: pre-commit run --all-files
```

Même si vous bypassez les hooks localement, la CI les vérifiera ! 🛡️

## Ressources

- [Documentation officielle pre-commit](https://pre-commit.com/)
- [Black documentation](https://black.readthedocs.io/)
- [isort documentation](https://pycqa.github.io/isort/)
- [flake8 documentation](https://flake8.pycqa.org/)
- [Guide du développeur complet](./DEVELOPER_GUIDE.md)

## Support

En cas de problème :
1. Consultez ce guide
2. Lisez le [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)
3. Demandez de l'aide à l'équipe
4. Créez une issue sur GitHub

---

**Mis à jour** : Octobre 2025
**Auteur** : Équipe Geneweb Python
