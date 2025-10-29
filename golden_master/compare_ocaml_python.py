#!/usr/bin/env python3
"""
Comparateur Golden Master - OCaml vs Python
Compare les sorties des deux implémentations
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def compare_values(ocaml_val: Any, python_val: Any) -> Tuple[bool, str]:
    """Compare deux valeurs et retourne (match, message).
    
    Args:
        ocaml_val: Valeur OCaml
        python_val: Valeur Python
        
    Returns:
        Tuple (True si match, message de différence)
    """
    # Conversion de types si nécessaire
    if isinstance(ocaml_val, str) and isinstance(python_val, int):
        try:
            return str(python_val) == ocaml_val, f"Type mismatch: OCaml={ocaml_val!r}, Python={python_val!r}"
        except:
            pass
    
    if isinstance(ocaml_val, int) and isinstance(python_val, str):
        try:
            return ocaml_val == int(python_val), f"Type mismatch: OCaml={ocaml_val!r}, Python={python_val!r}"
        except:
            pass
    
    # Comparaison de listes
    if isinstance(ocaml_val, list) and isinstance(python_val, list):
        if len(ocaml_val) != len(python_val):
            return False, f"List length: OCaml={len(ocaml_val)}, Python={len(python_val)}"
        
        for i, (o, p) in enumerate(zip(ocaml_val, python_val)):
            match, msg = compare_values(o, p)
            if not match:
                return False, f"List[{i}]: {msg}"
        
        return True, ""
    
    # Comparaison directe
    if ocaml_val == python_val:
        return True, ""
    
    return False, f"OCaml={ocaml_val!r}, Python={python_val!r}"


def compare_test_file(ocaml_file: Path, python_file: Path) -> Dict[str, Any]:
    """Compare un fichier de test OCaml et Python.
    
    Args:
        ocaml_file: Fichier de sortie OCaml
        python_file: Fichier de sortie Python
        
    Returns:
        Dictionnaire avec les statistiques de comparaison
    """
    if not ocaml_file.exists():
        return {
            'success': False,
            'error': f'OCaml file not found: {ocaml_file}',
            'total': 0,
            'matched': 0,
            'mismatched': 0
        }
    
    if not python_file.exists():
        return {
            'success': False,
            'error': f'Python file not found: {python_file}',
            'total': 0,
            'matched': 0,
            'mismatched': 0
        }
    
    with open(ocaml_file, 'r', encoding='utf-8') as f:
        ocaml_data = json.load(f)
    
    with open(python_file, 'r', encoding='utf-8') as f:
        python_data = json.load(f)
    
    total = 0
    matched = 0
    mismatched = 0
    differences = []
    
    # Créer un index des résultats Python par test_id et operation
    python_results_map = {}
    for result in python_data.get('results', []):
        test_id = result['id']
        for test_result in result.get('test_results', []):
            operation = test_result['operation']
            op_key = json.dumps(operation, sort_keys=True)
            python_results_map[(test_id, op_key)] = test_result
    
    # Comparer avec OCaml
    for ocaml_result in ocaml_data.get('results', []):
        test_id = ocaml_result['id']
        
        for ocaml_test in ocaml_result.get('test_results', []):
            total += 1
            operation = ocaml_test['operation']
            op_key = json.dumps(operation, sort_keys=True)
            
            ocaml_value = ocaml_test['result']
            ocaml_success = ocaml_test['success']
            
            # Trouver le résultat Python correspondant
            python_test = python_results_map.get((test_id, op_key))
            
            if not python_test:
                mismatched += 1
                differences.append({
                    'test_id': test_id,
                    'operation': operation,
                    'error': 'No corresponding Python test found'
                })
                continue
            
            python_value = python_test['result']
            python_success = python_test['success']
            
            # Comparer les succès
            if ocaml_success != python_success:
                mismatched += 1
                differences.append({
                    'test_id': test_id,
                    'operation': operation,
                    'error': f'Success mismatch: OCaml={ocaml_success}, Python={python_success}'
                })
                continue
            
            # Si les deux ont échoué, c'est OK
            if not ocaml_success and not python_success:
                matched += 1
                continue
            
            # Comparer les valeurs
            match, msg = compare_values(ocaml_value, python_value)
            if match:
                matched += 1
            else:
                mismatched += 1
                differences.append({
                    'test_id': test_id,
                    'operation': operation,
                    'ocaml_value': ocaml_value,
                    'python_value': python_value,
                    'difference': msg
                })
    
    return {
        'success': mismatched == 0,
        'total': total,
        'matched': matched,
        'mismatched': mismatched,
        'differences': differences,
        'test_suite': ocaml_data.get('test_suite', 'Unknown')
    }


def print_comparison_results(results: Dict[str, Any], file_name: str):
    """Affiche les résultats de comparaison."""
    print(f"\n{Colors.BOLD}📊 {file_name}{Colors.RESET}")
    print(f"   Suite: {results['test_suite']}")
    print(f"{'=' * 70}")
    
    total = results['total']
    matched = results['matched']
    mismatched = results['mismatched']
    
    if results['success']:
        print(f"{Colors.GREEN}✓ OCaml et Python produisent les mêmes résultats !{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ Différences trouvées entre OCaml et Python{Colors.RESET}")
    
    print(f"\nTotal: {total} | ", end="")
    print(f"{Colors.GREEN}Identiques: {matched}{Colors.RESET} | ", end="")
    print(f"{Colors.RED}Différents: {mismatched}{Colors.RESET}")
    
    if mismatched > 0 and 'differences' in results:
        print(f"\n{Colors.YELLOW}Détails des différences:{Colors.RESET}")
        for i, diff in enumerate(results['differences'][:10], 1):
            print(f"\n  {i}. Test: {diff['test_id']}")
            print(f"     Operation: {diff['operation'].get('op', 'unknown')}")
            if 'error' in diff:
                print(f"     {Colors.RED}Erreur: {diff['error']}{Colors.RESET}")
            else:
                print(f"     OCaml:  {diff.get('ocaml_value')}")
                print(f"     Python: {diff.get('python_value')}")
                print(f"     Diff:   {diff.get('difference')}")
        
        if len(results['differences']) > 10:
            print(f"\n  ... et {len(results['differences']) - 10} autres différences")


def main():
    """Fonction principale."""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("=" * 70)
    print("  🔍 Golden Master Comparison - OCaml vs Python")
    print("=" * 70)
    print(f"{Colors.RESET}\n")
    
    ocaml_dir = Path("outputs_ocaml")
    python_dir = Path("outputs_python")
    
    if not ocaml_dir.exists():
        print(f"{Colors.RED}❌ Répertoire outputs_ocaml non trouvé{Colors.RESET}")
        sys.exit(1)
    
    if not python_dir.exists():
        print(f"{Colors.RED}❌ Répertoire outputs_python non trouvé{Colors.RESET}")
        sys.exit(1)
    
    # Trouver tous les fichiers OCaml
    ocaml_files = list(ocaml_dir.glob("*.json"))
    
    if not ocaml_files:
        print(f"{Colors.RED}❌ Aucun fichier OCaml trouvé{Colors.RESET}")
        sys.exit(1)
    
    all_match = True
    total_all = 0
    matched_all = 0
    mismatched_all = 0
    
    for ocaml_file in sorted(ocaml_files):
        python_file = python_dir / ocaml_file.name
        results = compare_test_file(ocaml_file, python_file)
        print_comparison_results(results, ocaml_file.name)
        
        if not results['success']:
            all_match = False
        
        total_all += results['total']
        matched_all += results['matched']
        mismatched_all += results['mismatched']
    
    # Résumé global
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}📈 RÉSUMÉ GLOBAL{Colors.RESET}")
    print(f"{'=' * 70}")
    print(f"Fichiers comparés: {len(ocaml_files)}")
    print(f"Total opérations: {total_all}")
    print(f"{Colors.GREEN}Identiques: {matched_all}{Colors.RESET}")
    print(f"{Colors.RED}Différences: {mismatched_all}{Colors.RESET}")
    
    if all_match:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 SUCCÈS ! OCaml et Python produisent les mêmes résultats !{Colors.RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Certaines différences ont été trouvées{Colors.RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
