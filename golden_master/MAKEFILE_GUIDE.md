# 📘 Guide d'utilisation du Makefile

## 🚀 Commandes principales

### Lancer les tests

```bash
# Lancer tous les tests (OCaml + Python + comparaison + validation)
make

# Alias pour make
make test
make run
```

**Ce qui se passe :**
1. ✅ Compile le test runner OCaml
2. ✅ Exécute les tests OCaml (6 fichiers de tests)
3. ✅ Exécute les tests Python (6 fichiers de tests)
4. ✅ Compare les résultats OCaml vs Python
5. ✅ Valide les résultats OCaml contre les valeurs attendues

**Résultat attendu :** `138/138 tests identiques` ✅

---

## 🧹 Commandes de nettoyage

### Nettoyage standard

```bash
make clean
```

**Supprime :**
- ✅ Fichiers JSON de sortie (`outputs_ocaml/*.json`, `outputs_python/*.json`)
- ✅ Exécutables OCaml (`.exe`, `.cmi`, `.cmo`, `.cmx`, `.o`)

**Garde :**
- ✅ Répertoires (`outputs_ocaml/`, `outputs_python/`, `reports/`)
- ✅ Fichiers sources (`.ml`, `.py`, `.sh`)

### Nettoyage complet

```bash
make fclean
```

**Supprime tout :**
- ✅ Fichiers JSON de sortie
- ✅ Exécutables OCaml
- ✅ Rapports de comparaison
- ✅ Répertoires de sortie complets

### Recompilation complète

```bash
make re
```

**Équivalent à :**
```bash
make fclean && make
```

---

## 🎯 Tests individuels

### Tests OCaml uniquement

```bash
make test-ocaml
```

**Actions :**
1. Compile le test runner OCaml
2. Exécute les tests OCaml
3. Génère `outputs_ocaml/*.json`

### Tests Python uniquement

```bash
make test-python
```

**Actions :**
1. Exécute les tests Python
2. Génère `outputs_python/*.json`

### Comparaison uniquement

```bash
make compare
```

**Prérequis :** Les fichiers `outputs_ocaml/*.json` et `outputs_python/*.json` doivent exister

**Action :** Compare les résultats et affiche un rapport détaillé

### Validation uniquement

```bash
make validate
```

**Prérequis :** Les fichiers `outputs_ocaml/*.json` doivent exister

**Action :** Valide les résultats OCaml contre les valeurs attendues dans `inputs/*.json`

---

## 🔨 Compilation

### Compiler le test runner OCaml

```bash
make compile
# ou
make compile-ocaml
```

**Génère :** `run_ocaml_tests_fixed.exe`

**Dépendances requises :**
- OCaml + opam
- Packages : `yojson`, `unix`, `zarith`
- Module geneweb compilé dans `../geneweb-oCaml/_build/`

---

## 📊 Utilitaires

### Afficher le statut

```bash
make status
```

**Affiche :**
- Nombre de fichiers de tests disponibles (`inputs/`)
- Nombre de résultats OCaml générés (`outputs_ocaml/`)
- Nombre de résultats Python générés (`outputs_python/`)

**Exemple de sortie :**
```
📊 Statut des tests Golden Master

Fichiers d'entrée:
  Tests disponibles: 7

Résultats OCaml:
  Fichiers générés: 6

Résultats Python:
  Fichiers générés: 6
```

### Créer les répertoires

```bash
make dirs
```

**Crée (si nécessaire) :**
- `inputs/`
- `outputs_ocaml/`
- `outputs_python/`
- `reports/`

### Afficher l'aide

```bash
make help
```

**Affiche :** Liste complète de toutes les commandes disponibles

---

## 🧹 Nettoyages sélectifs

### Supprimer uniquement les outputs

```bash
make clean-outputs
```

**Supprime :** `outputs_ocaml/*.json` et `outputs_python/*.json`

**Garde :** Exécutables et rapports

### Supprimer uniquement les exécutables OCaml

```bash
make clean-ocaml
```

**Supprime :** Tous les fichiers de compilation OCaml

**Garde :** Fichiers JSON et rapports

### Supprimer uniquement les rapports

```bash
make clean-reports
```

**Supprime :** `reports/*.txt` et `reports/*.json`

**Garde :** Outputs et exécutables

---

## 📋 Exemples de workflows

### Workflow de développement

```bash
# Lancer les tests
make

# Si échec, nettoyer et relancer
make clean
make

# Vérifier le statut
make status
```

### Workflow de debugging

```bash
# Tester uniquement OCaml
make test-ocaml

# Tester uniquement Python
make test-python

# Comparer manuellement
make compare
```

### Workflow de nettoyage

```bash
# Nettoyage standard (garde les répertoires)
make clean

# Nettoyage complet (supprime tout)
make fclean

# Recompiler après nettoyage
make re
```

---

## 🎨 Couleurs d'affichage

Le Makefile utilise des couleurs pour améliorer la lisibilité :

- 🔵 **Bleu** : Informations générales
- 🟢 **Vert** : Succès
- 🟡 **Jaune** : Nettoyage/avertissements
- 🔴 **Rouge** : Erreurs (si implémenté)

---

## 🛠️ Variables de configuration

Les variables suivantes peuvent être modifiées dans le Makefile :

| Variable | Valeur par défaut | Description |
|----------|-------------------|-------------|
| `GENEWEB_DIR` | `../geneweb-oCaml` | Répertoire du projet OCaml |
| `INPUT_DIR` | `inputs` | Répertoire des tests JSON |
| `OUTPUT_DIR_OCAML` | `outputs_ocaml` | Sortie OCaml |
| `OUTPUT_DIR_PYTHON` | `outputs_python` | Sortie Python |
| `REPORTS_DIR` | `reports` | Rapports de comparaison |

---

## ❓ Troubleshooting

### Erreur : "make: command not found"

**Solution :** Installer make dans WSL
```bash
sudo apt-get update
sudo apt-get install make
```

### Erreur de compilation OCaml

**Solution :** Recompiler geneweb
```bash
cd ../geneweb-oCaml
make clean && make distrib
```

### Erreur : "ocamlfind: command not found"

**Solution :** Installer OCaml et opam
```bash
sudo apt-get install ocaml opam
opam init
eval $(opam env)
opam install yojson zarith
```

### Les tests échouent après modification

**Solution :** Nettoyer complètement et relancer
```bash
make fclean
make
```

---

## 📚 Ressources

- **README.md** - Documentation complète du projet
- **STRUCTURE.md** - Structure détaillée du répertoire
- **run_complete_golden_master.sh** - Script bash sous-jacent
- **Makefile** - Code source des commandes

---

## 🎯 Résumé des commandes essentielles

| Commande | Usage |
|----------|-------|
| `make` | Lancer tous les tests |
| `make clean` | Nettoyer les fichiers générés |
| `make fclean` | Nettoyage complet |
| `make re` | Recompiler tout |
| `make help` | Afficher l'aide |
| `make status` | Voir le statut |
| `make test-ocaml` | Tests OCaml uniquement |
| `make test-python` | Tests Python uniquement |

---

**🎉 Bonne utilisation du Makefile !**
