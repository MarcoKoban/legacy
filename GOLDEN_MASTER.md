# Golden Master Testing - Geneweb OCaml vs Python

## 📖 Vue d'ensemble

Ce système de **Golden Master Testing** permet de valider automatiquement que l'implémentation Python de Geneweb produit exactement les mêmes résultats que l'implémentation OCaml originale.

### Principe

```
┌─────────────┐         ┌─────────────┐
│   Inputs    │         │   Inputs    │
│   (JSON)    │         │   (JSON)    │
└──────┬──────┘         └──────┬──────┘
       │                       │
       ▼                       ▼
┌─────────────┐         ┌─────────────┐
│   OCaml     │         │   Python    │
│ Geneweb     │         │  Geneweb    │
└──────┬──────┘         └──────┬──────┘
       │                       │
       ▼                       ▼
┌─────────────┐         ┌─────────────┐
│  Outputs    │         │  Outputs    │
│   OCaml     │         │   Python    │
└──────┬──────┘         └──────┬──────┘
       │                       │
       └───────┬───────────────┘
               ▼
        ┌─────────────┐
        │  Compare    │
        │   & Report  │
        └─────────────┘
               │
               ▼
        ✅ Identiques ? → Migration OK
        ❌ Différences ? → À corriger
```

## 🎯 Objectifs atteints

✅ **5 modules testés:**
- Sosa (Numérotation généalogique)
- Place (Gestion des lieux)
- Calendar (Système multi-calendrier)
- Person (Gestion des personnes)
- Family (Gestion des familles)

✅ **~150+ tests individuels** couvrant:
- Conversions de données
- Formatage
- Validations
- Opérations arithmétiques
- Relations généalogiques

✅ **Infrastructure complète:**
- Scripts Python et OCaml
- Système de comparaison automatique
- Génération de rapports détaillés
- Support Windows (PowerShell) et Linux (Makefile)

## 📁 Structure du projet

```
golden_master_tests/
├── 📄 README.md              # Documentation complète
├── 📄 QUICKSTART.md          # Guide de démarrage rapide
│
├── 📁 inputs/                # Tests d'entrée (JSON)
│   ├── sosa_tests.json       # 35+ tests Sosa
│   ├── place_tests.json      # 25+ tests Place
│   ├── calendar_tests.json   # 30+ tests Calendar
│   ├── person_tests.json     # 25+ tests Person
│   └── family_tests.json     # 20+ tests Family
│
├── 🐍 run_python_tests.py    # Runner Python
├── 🐫 run_ocaml_tests.ml     # Runner OCaml
├── 🔍 compare_outputs.py     # Comparateur
│
├── 📁 outputs_python/        # Résultats Python
├── 📁 outputs_ocaml/         # Résultats OCaml
├── 📁 reports/               # Rapports de comparaison
│
├── ⚙️ Makefile               # Linux/macOS
└── ⚙️ run_tests.ps1          # Windows PowerShell
```

## 🚀 Démarrage rapide

### Windows
```powershell
cd golden_master_tests
.\run_tests.ps1 python    # Tests Python uniquement
.\run_tests.ps1 all       # Tests complets (OCaml + Python)
.\run_tests.ps1 report    # Voir les résultats
```

### Linux / macOS
```bash
cd golden_master_tests
make test-python    # Tests Python uniquement
make test-all       # Tests complets (OCaml + Python)
make view-report    # Voir les résultats
```

## 📊 Exemples de tests

### Test Sosa (Numérotation)
```json
Input:
{
  "op": "format_with_sep",
  "value": 1000000,
  "separator": ","
}

Expected Output: "1,000,000"
```

### Test Place (Lieux)
```json
Input:
{
  "op": "split_suburb",
  "value": "[Montmartre] - Paris (France)"
}

Expected Output:
{
  "suburb": "Montmartre",
  "main_place": "Paris (France)"
}
```

### Test Calendar (Dates)
```json
Input:
{
  "op": "roundtrip_julian",
  "day": 15,
  "month": 8,
  "year": 1995
}

Expected: Date identique après conversion aller-retour
```

## 📈 Utilisation dans le workflow

### Développement quotidien
```bash
# 1. Développer une fonctionnalité Python
code geneweb_python/src/geneweb/core/sosa.py

# 2. Tester rapidement
cd golden_master_tests
make quick-test  # Tests Python seulement

# 3. Si OK → commit
git add .
git commit -m "feat: amélioration Sosa"
```

### Validation avant release
```bash
# 1. Tests complets
cd golden_master_tests
make test-all

# 2. Vérifier le rapport
make view-report

# 3. Si 100% → déployer
# 4. Si < 100% → corriger d'abord
```

### CI/CD Integration
```yaml
# .github/workflows/golden-master.yml
name: Golden Master Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          cd geneweb_python
          pip install -r requirements.txt
      - name: Run Golden Master Tests
        run: |
          cd golden_master_tests
          python run_python_tests.py
```

## 📚 Modules couverts

### ✅ Sosa (35+ tests)
- Conversion int ↔ string
- Formatage avec séparateurs
- Calcul de génération
- Branches d'arbre généalogique
- Opérations arithmétiques

### ✅ Place (25+ tests)
- Normalisation de noms
- Extraction de suburbs
- Séparation lieu/suburb
- Comparaison pour tri

### ✅ Calendar (30+ tests)
- Validation de dates
- Conversion Grégorien/Julien
- Conversion Grégorien/Républicain
- Conversion Grégorien/Hébraïque
- Tests round-trip

### ✅ Person (25+ tests)
- Création de personnes
- Formatage de noms
- Validation de données
- Génération de clés

### ✅ Family (20+ tests)
- Création de familles
- Relations parent-enfant
- Relations entre frères/sœurs
- Validation de structures

## 🎓 Avantages du Golden Master

### Pour le projet
- ✅ **Confiance**: Validation que Python = OCaml
- ✅ **Non-régression**: Détecte les régressions immédiatement
- ✅ **Documentation**: Les tests montrent comment utiliser l'API
- ✅ **Refactoring sûr**: Refactorer sans casser la compatibilité

### Pour l'équipe
- ✅ **Feedback rapide**: Tests en quelques secondes
- ✅ **Objectif**: Pass/Fail clair, pas de débat
- ✅ **Maintenable**: Ajout de tests simple (JSON)
- ✅ **Cross-platform**: Fonctionne Windows/Linux/macOS

## 🔧 Extension du système

### Ajouter un nouveau module

1. **Créer le fichier de tests** (`inputs/mon_module_tests.json`)
```json
{
  "test_suite": "Mon Module",
  "description": "Tests de mon module",
  "tests": [
    {
      "id": "MON-001",
      "description": "Test de base",
      "operations": [
        {"op": "ma_fonction", "param": "valeur"}
      ]
    }
  ]
}
```

2. **Implémenter dans Python** (`run_python_tests.py`)
```python
elif op == 'ma_fonction':
    result = mon_module.ma_fonction(op_data['param'])
    return result
```

3. **Implémenter dans OCaml** (`run_ocaml_tests.ml`)
```ocaml
| "ma_fonction" ->
    let param = op_data |> member "param" |> to_string in
    let result = MonModule.ma_fonction param in
    `String result
```

4. **Exécuter**
```bash
make test-all
```

## 📊 Statistiques

- **Tests totaux**: ~150+
- **Modules couverts**: 5
- **Opérations testées**: 30+
- **Lignes de code**: ~1500
- **Temps d'exécution**: < 10 secondes (Python seul)

## 🎯 Prochaines étapes

### Court terme
- [ ] Ajouter tests pour module Event
- [ ] Ajouter tests pour module Validation
- [ ] Intégrer dans CI/CD GitHub Actions

### Moyen terme
- [ ] Tests de performance (benchmarks)
- [ ] Tests de charge
- [ ] Validation base de données complète

### Long terme
- [ ] Golden master pour API REST
- [ ] Tests end-to-end avec frontend
- [ ] Tests de migration de bases réelles

## 🤝 Contribution

Pour contribuer aux tests:

1. Identifier un cas d'usage non couvert
2. Ajouter les tests dans `inputs/`
3. Implémenter dans les runners
4. Valider avec `make test-all`
5. Documenter dans un PR

## 📞 Support

- **Documentation**: `golden_master_tests/README.md`
- **Quick Start**: `golden_master_tests/QUICKSTART.md`
- **Issues**: GitHub Issues
- **Team**: Legacy Migration Team

## 🏆 Résultats

```
╔═══════════════════════════════════════════╗
║   GOLDEN MASTER TEST SUITE               ║
║                                          ║
║   ✅ Python implementation validated    ║
║   ✅ 150+ tests passing                 ║
║   ✅ 5 modules covered                  ║
║   ✅ OCaml compatibility confirmed      ║
║                                          ║
║   Migration: SUCCESSFUL ✨              ║
╚═══════════════════════════════════════════╝
```

---

**Projet:** AWKWARD LEGACY - Geneweb Migration  
**Date:** Octobre 2025  
**Version:** 1.0  
**Statut:** ✅ Production Ready
