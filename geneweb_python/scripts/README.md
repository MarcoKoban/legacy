# Scripts d'automatisation

Ce dossier contient des scripts pour automatiser certaines tâches de développement.

## setup_dev.py

Script de post-installation qui configure automatiquement l'environnement de développement.

### Utilisation

```bash
# Après l'installation des dépendances
python scripts/setup_dev.py
```

### Ce qu'il fait

1. ✅ Vérifie que vous êtes dans un dépôt Git
2. ✅ Installe automatiquement les hooks pre-commit
3. ✅ Affiche des instructions claires pour la suite

### Intégration avec pip

Ce script peut être appelé automatiquement après `pip install -e ".[dev]"` en ajoutant une section dans `pyproject.toml` :

```toml
[project.scripts]
setup-dev = "scripts.setup_dev:main"
```

## update_coverage_badge.py

Script qui met à jour automatiquement le badge de couverture dans le README.

### Utilisation

```bash
python scripts/update_coverage_badge.py
```

## Autres scripts

D'autres scripts utilitaires peuvent être ajoutés ici pour automatiser :
- La génération de documentation
- Les migrations de base de données
- Les tâches de maintenance
- etc.
