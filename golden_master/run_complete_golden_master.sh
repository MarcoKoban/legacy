#!/bin/bash
# Script complet pour le Golden Master Testing : OCaml + Python + Comparaison

set -e

PROJECT_ROOT="/mnt/c/Users/mrori/Bureau/Epitech/legacy/G-ING-900-PAR-9-1-legacy-22"
GENEWEB_DIR="$PROJECT_ROOT/geneweb-oCaml"
GOLDEN_MASTER_DIR="$PROJECT_ROOT/golden_master"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🧪 Golden Master Testing Suite - OCaml vs Python         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Nettoyer les variables d'environnement Windows opam
unset OPAM_LAST_ENV OPAM_SWITCH_PREFIX OCAMLTOP_INCLUDE_PATH CAML_LD_LIBRARY_PATH OCAML_TOPLEVEL_PATH

# Initialiser l'environnement opam Linux
eval $(opam env --set-switch)

cd "$GOLDEN_MASTER_DIR"

# Créer les dossiers de sortie
mkdir -p outputs_ocaml
mkdir -p outputs_python
mkdir -p reports

echo "📋 Étape 1/4: Compilation et exécution des tests OCaml"
echo "─────────────────────────────────────────────────────────────"

# Compiler le test runner OCaml
ocamlfind ocamlc -package yojson,unix,zarith -linkpkg \
    -I "$GENEWEB_DIR/_build/default/lib/sosa/.geneweb_sosa.objs/byte" \
    "$GENEWEB_DIR/_build/default/lib/sosa/geneweb_sosa.cma" \
    -o run_ocaml_tests_fixed.exe \
    run_ocaml_tests_fixed.ml

if [ $? -eq 0 ]; then
    echo "✓ Test runner OCaml compilé"
    ./run_ocaml_tests_fixed.exe
    echo "✓ Tests OCaml terminés"
else
    echo "❌ Erreur de compilation OCaml"
    exit 1
fi

echo ""
echo "🐍 Étape 2/4: Exécution des tests Python"
echo "─────────────────────────────────────────────────────────────"

python3 run_python_tests_simple.py

echo ""
echo "🔍 Étape 3/4: Comparaison OCaml vs Python"
echo "─────────────────────────────────────────────────────────────"

python3 compare_ocaml_python.py

COMPARISON_RESULT=$?

echo ""
echo "✅ Étape 4/4: Validation des résultats OCaml"
echo "─────────────────────────────────────────────────────────────"

python3 validate_golden_master.py

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  ✨ Tests terminés !                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"

exit $COMPARISON_RESULT
