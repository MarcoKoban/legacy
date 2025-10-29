# ============================================================================
# Golden Master Testing Suite - Makefile
# ============================================================================
# Auteur: Geneweb Project
# Description: Makefile pour exécuter les tests Golden Master (OCaml vs Python)
# ============================================================================

# Variables de configuration
GENEWEB_DIR = ../geneweb-oCaml
OCAML_RUNNER = run_ocaml_tests_fixed
PYTHON_RUNNER = run_python_tests_simple.py
COMPARE_SCRIPT = compare_ocaml_python.py
VALIDATE_SCRIPT = validate_golden_master.py
MAIN_SCRIPT = run_complete_golden_master.sh

# Répertoires
INPUT_DIR = inputs
OUTPUT_DIR_OCAML = outputs_ocaml
OUTPUT_DIR_PYTHON = outputs_python
REPORTS_DIR = reports

# Couleurs pour l'affichage
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

# ============================================================================
# Cibles principales
# ============================================================================

.PHONY: all test run clean fclean re help

# Cible par défaut
all: test

# Lance tous les tests Golden Master
test: banner
	@echo "$(BLUE)🧪 Lancement des tests Golden Master...$(NC)"
	@bash $(MAIN_SCRIPT)

# Alias pour test
run: test

# ============================================================================
# Compilation
# ============================================================================

.PHONY: compile compile-ocaml

# Compile le test runner OCaml
compile-ocaml:
	@echo "$(BLUE)🔨 Compilation du test runner OCaml...$(NC)"
	@bash -c 'cd $(GENEWEB_DIR) && eval $$(opam env) && \
		ocamlfind ocamlc -package yojson,unix,zarith -linkpkg \
		-I _build/default/lib/sosa/.geneweb_sosa.objs/byte \
		-o ../golden_master/$(OCAML_RUNNER).exe \
		../golden_master/$(OCAML_RUNNER).ml'
	@echo "$(GREEN)✓ Compilation terminée$(NC)"

compile: compile-ocaml

# ============================================================================
# Tests individuels
# ============================================================================

.PHONY: test-ocaml test-python compare validate

# Exécute uniquement les tests OCaml
test-ocaml: compile-ocaml
	@echo "$(BLUE)🧪 Exécution des tests OCaml...$(NC)"
	@mkdir -p $(OUTPUT_DIR_OCAML)
	@./$(OCAML_RUNNER).exe
	@echo "$(GREEN)✓ Tests OCaml terminés$(NC)"

# Exécute uniquement les tests Python
test-python:
	@echo "$(BLUE)🐍 Exécution des tests Python...$(NC)"
	@mkdir -p $(OUTPUT_DIR_PYTHON)
	@python3 $(PYTHON_RUNNER)
	@echo "$(GREEN)✓ Tests Python terminés$(NC)"

# Compare les résultats OCaml et Python
compare:
	@echo "$(BLUE)🔍 Comparaison des résultats...$(NC)"
	@python3 $(COMPARE_SCRIPT)

# Valide les résultats OCaml contre les valeurs attendues
validate:
	@echo "$(BLUE)✅ Validation des résultats OCaml...$(NC)"
	@python3 $(VALIDATE_SCRIPT)

# ============================================================================
# Nettoyage
# ============================================================================

.PHONY: clean-outputs clean-ocaml clean-reports

# Supprime les fichiers de sortie
clean-outputs:
	@echo "$(YELLOW)🧹 Nettoyage des fichiers de sortie...$(NC)"
	@rm -rf $(OUTPUT_DIR_OCAML)/*.json
	@rm -rf $(OUTPUT_DIR_PYTHON)/*.json
	@echo "$(GREEN)✓ Fichiers de sortie supprimés$(NC)"

# Supprime les exécutables OCaml et fichiers de compilation
clean-ocaml:
	@echo "$(YELLOW)🧹 Nettoyage des fichiers OCaml...$(NC)"
	@rm -f $(OCAML_RUNNER).exe
	@rm -f $(OCAML_RUNNER).cmi
	@rm -f $(OCAML_RUNNER).cmo
	@rm -f $(OCAML_RUNNER).cmx
	@rm -f $(OCAML_RUNNER).o
	@echo "$(GREEN)✓ Fichiers OCaml supprimés$(NC)"

# Supprime les rapports générés
clean-reports:
	@echo "$(YELLOW)🧹 Nettoyage des rapports...$(NC)"
	@rm -rf $(REPORTS_DIR)/*.txt
	@rm -rf $(REPORTS_DIR)/*.json
	@echo "$(GREEN)✓ Rapports supprimés$(NC)"

# Nettoyage standard (outputs + exécutables)
clean: clean-outputs clean-ocaml
	@echo "$(GREEN)✨ Nettoyage terminé$(NC)"

# Nettoyage complet (tout supprimer)
fclean: clean clean-reports
	@echo "$(YELLOW)🧹 Nettoyage complet...$(NC)"
	@rm -rf $(OUTPUT_DIR_OCAML)
	@rm -rf $(OUTPUT_DIR_PYTHON)
	@rm -rf $(REPORTS_DIR)
	@echo "$(GREEN)✨ Nettoyage complet terminé$(NC)"

# Recompile tout
re: fclean all

# ============================================================================
# Utilitaires
# ============================================================================

.PHONY: banner status dirs help

# Affiche la bannière
banner:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║     🧪 Golden Master Testing Suite - OCaml vs Python         ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""

# Affiche le statut des tests
status:
	@echo "$(BLUE)📊 Statut des tests Golden Master$(NC)"
	@echo ""
	@echo "$(YELLOW)Fichiers d'entrée:$(NC)"
	@ls -1 $(INPUT_DIR)/*.json 2>/dev/null | wc -l | xargs echo "  Tests disponibles:"
	@echo ""
	@echo "$(YELLOW)Résultats OCaml:$(NC)"
	@ls -1 $(OUTPUT_DIR_OCAML)/*.json 2>/dev/null | wc -l | xargs echo "  Fichiers générés:"
	@echo ""
	@echo "$(YELLOW)Résultats Python:$(NC)"
	@ls -1 $(OUTPUT_DIR_PYTHON)/*.json 2>/dev/null | wc -l | xargs echo "  Fichiers générés:"
	@echo ""

# Crée les répertoires nécessaires
dirs:
	@echo "$(BLUE)📁 Création des répertoires...$(NC)"
	@mkdir -p $(INPUT_DIR)
	@mkdir -p $(OUTPUT_DIR_OCAML)
	@mkdir -p $(OUTPUT_DIR_PYTHON)
	@mkdir -p $(REPORTS_DIR)
	@echo "$(GREEN)✓ Répertoires créés$(NC)"

# Affiche l'aide
help:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║           Golden Master Testing Suite - Aide                  ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Cibles principales:$(NC)"
	@echo "  $(YELLOW)make$(NC) ou $(YELLOW)make test$(NC)     - Lance tous les tests (OCaml + Python + comparaison)"
	@echo "  $(YELLOW)make run$(NC)              - Alias pour 'make test'"
	@echo "  $(YELLOW)make clean$(NC)            - Supprime les outputs et exécutables"
	@echo "  $(YELLOW)make fclean$(NC)           - Nettoyage complet (outputs + rapports + répertoires)"
	@echo "  $(YELLOW)make re$(NC)               - Recompile tout (fclean + test)"
	@echo ""
	@echo "$(GREEN)Tests individuels:$(NC)"
	@echo "  $(YELLOW)make test-ocaml$(NC)       - Exécute uniquement les tests OCaml"
	@echo "  $(YELLOW)make test-python$(NC)      - Exécute uniquement les tests Python"
	@echo "  $(YELLOW)make compare$(NC)          - Compare les résultats OCaml vs Python"
	@echo "  $(YELLOW)make validate$(NC)         - Valide les résultats OCaml"
	@echo ""
	@echo "$(GREEN)Compilation:$(NC)"
	@echo "  $(YELLOW)make compile$(NC)          - Compile le test runner OCaml"
	@echo "  $(YELLOW)make compile-ocaml$(NC)    - Compile le test runner OCaml"
	@echo ""
	@echo "$(GREEN)Nettoyage:$(NC)"
	@echo "  $(YELLOW)make clean-outputs$(NC)    - Supprime uniquement les fichiers JSON de sortie"
	@echo "  $(YELLOW)make clean-ocaml$(NC)      - Supprime uniquement les exécutables OCaml"
	@echo "  $(YELLOW)make clean-reports$(NC)    - Supprime uniquement les rapports"
	@echo ""
	@echo "$(GREEN)Utilitaires:$(NC)"
	@echo "  $(YELLOW)make status$(NC)           - Affiche le statut des tests"
	@echo "  $(YELLOW)make dirs$(NC)             - Crée les répertoires nécessaires"
	@echo "  $(YELLOW)make help$(NC)             - Affiche cette aide"
	@echo ""
	@echo "$(BLUE)Exemples d'utilisation:$(NC)"
	@echo "  $(YELLOW)make$(NC)                  - Lance tous les tests"
	@echo "  $(YELLOW)make test-ocaml$(NC)       - Teste uniquement OCaml"
	@echo "  $(YELLOW)make clean && make$(NC)    - Nettoie et relance les tests"
	@echo ""
