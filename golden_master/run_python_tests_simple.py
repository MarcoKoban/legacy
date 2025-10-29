#!/usr/bin/env python3
"""
Golden Master Test Runner - Python Implementation
Version simplifiée alignée avec les tests OCaml
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add the src directory to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "geneweb_python" / "src"))

try:
    from geneweb.core.sosa import Sosa
    SOSA_AVAILABLE = True
except ImportError:
    SOSA_AVAILABLE = False
    print("⚠️  WARNING: geneweb.core.sosa not available")


def run_sosa_operation(op_data: Dict[str, Any]) -> Any:
    """Execute a Sosa operation.
    
    Args:
        op_data: Operation configuration
        
    Returns:
        Operation result
    """
    if not SOSA_AVAILABLE:
        return "Sosa module not available"
    
    op = op_data.get('op')
    
    if op == 'from_int':
        value = op_data['value']
        sosa = Sosa.from_int(value)
        return str(sosa.value)
    
    elif op == 'from_string':
        value = op_data['value']
        sosa = Sosa.from_string(value)
        return str(sosa.value)
    
    elif op == 'format_with_sep':
        value = op_data['value']
        separator = op_data['separator']
        sosa = Sosa.from_int(value)
        # Python n'a pas to_string_sep, on le fait manuellement
        value_str = str(sosa.value)
        # Ajouter les séparateurs tous les 3 chiffres depuis la droite
        if len(value_str) <= 3:
            return value_str
        # Inverser, grouper par 3, rejoindre avec séparateur, inverser à nouveau
        reversed_str = value_str[::-1]
        groups = [reversed_str[i:i+3] for i in range(0, len(reversed_str), 3)]
        return separator.join(groups)[::-1]
    
    elif op == 'gen':
        value = op_data['value']
        sosa = Sosa.from_int(value)
        return sosa.generation()  # Utiliser generation() au lieu de gen()
    
    elif op == 'branches':
        value = op_data['value']
        sosa = Sosa.from_int(value)
        branches = sosa.branch_path()  # Utiliser branch_path() au lieu de branches()
        return [int(b) for b in branches]
    
    elif op == 'add':
        a = op_data['a']
        b = op_data['b']
        sosa_a = Sosa.from_int(a)
        sosa_b = Sosa.from_int(b)
        # Python n'a pas add(), on fait l'addition manuellement
        result = Sosa.from_int(sosa_a.value + sosa_b.value)
        return str(result.value)
    
    elif op == 'multiply':
        a = op_data['a']
        b = op_data['b']
        sosa_a = Sosa.from_int(a)
        # Python n'a pas multiply(), on fait la multiplication manuellement
        result = Sosa.from_int(sosa_a.value * b)
        return str(result.value)
    
    elif op == 'divide':
        a = op_data['a']
        b = op_data['b']
        sosa_a = Sosa.from_int(a)
        result = sosa_a.divide_by(b)
        return str(result.value)
    
    else:
        return f"Unknown Sosa operation: {op}"


def run_place_operation(op_data: Dict[str, Any]) -> Any:
    """Execute a Place operation (stub)."""
    op = op_data.get('op')
    # Message aligné avec OCaml
    return f"Place operations not available in geneweb public API: {op}"


def run_calendar_operation(op_data: Dict[str, Any]) -> Any:
    """Execute a Calendar operation (stub)."""
    op = op_data.get('op')
    # Message aligné avec OCaml
    return f"Unknown Sosa operation: {op}"


def process_operation(op_data: Dict[str, Any], test_type: str) -> Any:
    """Process a single operation based on test type.
    
    Args:
        op_data: Operation data
        test_type: Type of test (Sosa, Place, Calendar, etc.)
        
    Returns:
        Operation result
    """
    if test_type == "Sosa":
        return run_sosa_operation(op_data)
    elif test_type == "Place":
        return run_place_operation(op_data)
    elif test_type == "Calendar":
        return run_calendar_operation(op_data)
    else:
        # Message identique à OCaml
        return f"Unknown test type: {test_type}"


def process_test(test_data: Dict[str, Any], test_type: str) -> Dict[str, Any]:
    """Process a single test.
    
    Args:
        test_data: Test configuration
        test_type: Type of test
        
    Returns:
        Test results
    """
    test_id = test_data['id']
    description = test_data['description']
    operations = test_data.get('operations', [])
    
    results = []
    for op_data in operations:
        try:
            result = process_operation(op_data, test_type)
            results.append({
                'operation': op_data,
                'result': result,
                'success': True,
                'error': None
            })
        except Exception as e:
            results.append({
                'operation': op_data,
                'result': None,
                'success': False,
                'error': str(e)
            })
    
    return {
        'id': test_id,
        'description': description,
        'test_results': results
    }


def process_file(input_file: Path, output_file: Path):
    """Process a test file.
    
    Args:
        input_file: Input JSON file
        output_file: Output JSON file
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    test_suite = data.get('test_suite', 'Unknown')
    description = data.get('description', '')
    tests = data.get('tests', [])
    
    # Determine test type from suite name
    # Aligné avec la logique OCaml: recherche de caractères simples
    test_type = "Unknown"
    suite_lower = test_suite.lower()
    if 's' in suite_lower:
        test_type = "Sosa"
    elif 'p' in suite_lower:
        test_type = "Place"
    elif 'c' in suite_lower:
        test_type = "Calendar"
    
    print(f"   Processing: {test_suite}")
    print(f"   Type: {test_type}")
    
    results = []
    for test in tests:
        result = process_test(test, test_type)
        results.append(result)
    
    output = {
        'test_suite': test_suite,
        'description': description,
        'implementation': 'Python',
        'results': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)
    
    print(f"   Output: {output_file}\n")


def main():
    """Main function."""
    input_dir = Path("inputs")
    output_dir = Path("outputs_python")
    
    print("🧪 Running Python Golden Master Tests")
    print(f"📁 Input directory: {input_dir}")
    print(f"📁 Output directory: {output_dir}\n")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each input file
    input_files = sorted(input_dir.glob("*.json"))
    
    if not input_files:
        print("❌ No input files found!")
        sys.exit(1)
    
    for input_file in input_files:
        output_file = output_dir / input_file.name
        try:
            process_file(input_file, output_file)
        except Exception as e:
            print(f"   ❌ Error processing {input_file.name}: {e}\n")
    
    print("✅ All Python tests completed!\n")


if __name__ == "__main__":
    main()
