#!/usr/bin/env python3
"""
Golden Master Test - Comparateur basique
Compare les sorties OCaml avec les valeurs attendues
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def compare_value(actual: Any, expected: Any) -> bool:
    """Compare deux valeurs en gérant différents types"""
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            return False
        return all(compare_value(a, e) for a, e in zip(actual, expected))
    
    # Conversion de types si nécessaire
    if isinstance(expected, int) and isinstance(actual, str):
        try:
            return int(actual) == expected
        except:
            return False
    if isinstance(expected, str) and isinstance(actual, int):
        try:
            return str(actual) == expected
        except:
            return False
    
    return actual == expected

def validate_test_results(output_file: Path) -> Dict[str, Any]:
    """Valide les résultats d'un fichier de test OCaml"""
    
    if not output_file.exists():
        return {
            "success": False,
            "error": f"Fichier de sortie non trouvé: {output_file}",
            "total_tests": 0,
            "passed": 0,
            "failed": 0
        }
    
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Charger le fichier d'entrée correspondant pour avoir les valeurs attendues
    input_file = Path("inputs") / output_file.name
    if not input_file.exists():
        return {
            "success": False,
            "error": f"Fichier d'entrée non trouvé: {input_file}",
            "total_tests": 0,
            "passed": 0,
            "failed": 0
        }
    
    with open(input_file, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    # Créer un index des opérations attendues
    expected_ops = {}
    for test in input_data.get("tests", []):
        test_id = test["id"]
        for op in test.get("operations", []):
            key = json.dumps(op, sort_keys=True)
            expected_ops[key] = op.get("expected")
    
    total_ops = 0
    passed_ops = 0
    failed_ops = 0
    failures = []
    
    for result in data.get("results", []):
        test_id = result["id"]
        test_desc = result["description"]
        
        for test_result in result.get("test_results", []):
            total_ops += 1
            operation = test_result["operation"]
            actual_result = test_result["result"]
            success = test_result["success"]
            
            # Trouver la valeur attendue
            op_key = json.dumps(operation, sort_keys=True)
            expected = expected_ops.get(op_key)
            
            if not success:
                failed_ops += 1
                failures.append({
                    "test_id": test_id,
                    "operation": operation,
                    "error": test_result.get("error", "Unknown error")
                })
            elif expected is not None and not compare_value(actual_result, expected):
                failed_ops += 1
                failures.append({
                    "test_id": test_id,
                    "operation": operation,
                    "expected": expected,
                    "actual": actual_result
                })
            else:
                passed_ops += 1
    
    return {
        "success": failed_ops == 0,
        "total_tests": total_ops,
        "passed": passed_ops,
        "failed": failed_ops,
        "failures": failures,
        "test_suite": data.get("test_suite", "Unknown")
    }

def print_results(results: Dict[str, Any]):
    """Affiche les résultats de manière formatée"""
    
    print(f"\n{Colors.BOLD}📊 Résultats: {results['test_suite']}{Colors.RESET}")
    print(f"{'=' * 70}")
    
    total = results['total_tests']
    passed = results['passed']
    failed = results['failed']
    
    if results['success']:
        print(f"{Colors.GREEN}✓ Tous les tests sont passés !{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ Certains tests ont échoué{Colors.RESET}")
    
    print(f"\nTotal: {total} | ", end="")
    print(f"{Colors.GREEN}Passés: {passed}{Colors.RESET} | ", end="")
    print(f"{Colors.RED}Échoués: {failed}{Colors.RESET}")
    
    if failed > 0 and 'failures' in results:
        print(f"\n{Colors.YELLOW}Détails des échecs:{Colors.RESET}")
        for i, failure in enumerate(results['failures'][:10], 1):  # Limiter à 10 premiers
            print(f"\n  {i}. Test: {failure['test_id']}")
            print(f"     Operation: {failure['operation'].get('op', 'unknown')}")
            if 'error' in failure:
                print(f"     {Colors.RED}Erreur: {failure['error']}{Colors.RESET}")
            else:
                print(f"     Attendu:  {failure.get('expected')}")
                print(f"     Obtenu:   {failure.get('actual')}")
        
        if len(results['failures']) > 10:
            print(f"\n  ... et {len(results['failures']) - 10} autres échecs")

def main():
    """Fonction principale"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 70)
    print("  🧪 Golden Master Test - Validation OCaml")
    print("=" * 70)
    print(f"{Colors.RESET}\n")
    
    output_dir = Path("outputs_ocaml")
    
    if not output_dir.exists():
        print(f"{Colors.RED}❌ Répertoire outputs_ocaml non trouvé{Colors.RESET}")
        print("   Exécutez d'abord les tests OCaml avec compile_and_run_ocaml_wsl.sh")
        sys.exit(1)
    
    # Trouver tous les fichiers de sortie
    output_files = list(output_dir.glob("*.json"))
    
    if not output_files:
        print(f"{Colors.RED}❌ Aucun fichier de sortie trouvé dans outputs_ocaml/{Colors.RESET}")
        sys.exit(1)
    
    # Valider chaque fichier
    all_passed = True
    total_all = 0
    passed_all = 0
    failed_all = 0
    
    for output_file in sorted(output_files):
        results = validate_test_results(output_file)
        print_results(results)
        
        if not results['success']:
            all_passed = False
        
        total_all += results['total_tests']
        passed_all += results['passed']
        failed_all += results['failed']
    
    # Résumé global
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}📈 RÉSUMÉ GLOBAL{Colors.RESET}")
    print(f"{'=' * 70}")
    print(f"Fichiers testés: {len(output_files)}")
    print(f"Total opérations: {total_all}")
    print(f"{Colors.GREEN}Succès: {passed_all}{Colors.RESET}")
    print(f"{Colors.RED}Échecs: {failed_all}{Colors.RESET}")
    
    if all_passed:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 TOUS LES TESTS GOLDEN MASTER SONT PASSÉS !{Colors.RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Certains tests ont échoué{Colors.RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
