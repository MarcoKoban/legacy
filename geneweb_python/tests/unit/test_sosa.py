"""
Unit tests for Sosa genealogical numbering system.

The Sosa numbering system (also known as Ahnentafel) is a genealogical
numbering system used to identify a person's ancestors. The system assigns
numbers as follows:
- The root person (proband) is assigned number 1
- For any person numbered n:
  - Their father is numbered 2n
  - Their mother is numbered 2n+1

This test module validates the Python implementation against the OCaml
reference implementation, ensuring compatibility and correctness.

Test Plan Reference: SOSA-001 to SOSA-006
"""

import pytest

from geneweb.core.sosa import Sosa


@pytest.mark.unit
@pytest.mark.tdd
class TestSosaEquality:
    """Test Sosa number equality comparison (SOSA-001)."""

    def test_sosa_zero_equals_sosa_zero(self):
        """
        SOSA-001a: Compare Sosa.zero with Sosa.zero should return True.

        This tests the fundamental equality operation for Sosa numbers,
        ensuring that identical Sosa numbers are correctly identified as equal.
        """
        sosa_zero_1 = Sosa.zero()
        sosa_zero_2 = Sosa.zero()

        assert sosa_zero_1 == sosa_zero_2, "Sosa.zero should equal Sosa.zero"

    def test_sosa_one_equals_sosa_one(self):
        """
        SOSA-001b: Compare Sosa.one with Sosa.one should return True.

        This tests equality for the root person (proband) number,
        which is fundamental to the genealogical numbering system.
        """
        sosa_one_1 = Sosa.one()
        sosa_one_2 = Sosa.one()

        assert sosa_one_1 == sosa_one_2, "Sosa.one should equal Sosa.one"

    def test_sosa_zero_not_equals_sosa_one(self):
        """
        SOSA-001c: Compare Sosa.zero with Sosa.one should return False.

        This tests that different Sosa numbers are correctly identified
        as not equal, which is crucial for genealogical navigation.
        """
        sosa_zero = Sosa.zero()
        sosa_one = Sosa.one()

        assert sosa_zero != sosa_one, "Sosa.zero should not equal Sosa.one"
        assert not (sosa_zero == sosa_one), "Explicit inequality check"


@pytest.mark.unit
@pytest.mark.tdd
class TestSosaConversion:
    """Test integer to Sosa conversion (SOSA-002)."""

    def test_integer_zero_to_sosa(self):
        """
        SOSA-002a: Convert integer 0 to Sosa should equal Sosa.zero.

        This validates that the conversion from integer representation
        to Sosa object maintains semantic meaning.
        """
        sosa_from_int = Sosa.from_int(0)
        sosa_zero = Sosa.zero()

        assert sosa_from_int == sosa_zero, "Sosa.from_int(0) should equal Sosa.zero()"

    def test_integer_one_to_sosa(self):
        """
        SOSA-002b: Convert integer 1 to Sosa should equal Sosa.one.

        This validates conversion for the root person number,
        ensuring proper genealogical number system initialization.
        """
        sosa_from_int = Sosa.from_int(1)
        sosa_one = Sosa.one()

        assert sosa_from_int == sosa_one, "Sosa.from_int(1) should equal Sosa.one()"


@pytest.mark.unit
@pytest.mark.tdd
class TestSosaStringConversion:
    """Test string to Sosa conversion and formatting (SOSA-003)."""

    def test_string_zero_to_sosa(self):
        """
        SOSA-003a: Convert string "0" to Sosa should equal Sosa.zero.

        This validates string parsing functionality for genealogical
        data import from text files and user input.
        """
        sosa_from_str = Sosa.from_string("0")
        sosa_zero = Sosa.zero()

        assert (
            sosa_from_str == sosa_zero
        ), "Sosa.from_string('0') should equal Sosa.zero()"

    def test_sosa_zero_to_string(self):
        """
        SOSA-003b: Convert Sosa.zero to string should return "0".

        This validates string representation for display and export
        functionality in genealogical applications.
        """
        sosa_zero = Sosa.zero()

        assert str(sosa_zero) == "0", "str(Sosa.zero()) should return '0'"

    def test_complex_division_formatting(self):
        """
        SOSA-003c: Test complex divisions: 1000/1000, 2000/1000, 234000/1000.

        This validates mathematical operations on Sosa numbers for
        generation calculations and tree navigation algorithms.
        Expected results: "1", "2", "234"
        """
        # Test 1000/1000 = 1
        sosa_1000 = Sosa.from_int(1000)
        result_1 = sosa_1000.divide_by(1000)
        assert str(result_1) == "1", "1000/1000 should equal '1'"

        # Test 2000/1000 = 2
        sosa_2000 = Sosa.from_int(2000)
        result_2 = sosa_2000.divide_by(1000)
        assert str(result_2) == "2", "2000/1000 should equal '2'"

        # Test 234000/1000 = 234
        sosa_234000 = Sosa.from_int(234000)
        result_234 = sosa_234000.divide_by(1000)
        assert str(result_234) == "234", "234000/1000 should equal '234'"


@pytest.mark.unit
@pytest.mark.tdd
class TestSosaNumberFormatting:
    """Test number formatting with separators (SOSA-004)."""

    def test_format_with_comma_separator(self):
        """
        SOSA-004: Format numbers with comma separator.

        Test formatting of numbers 1, 10, 100, 1000, 10000, 100000, 1000000
        with comma separator. Expected results:
        "1", "10", "100", "1,000", "10,000", "100,000", "1,000,000"

        This validates genealogical display formatting for large Sosa numbers
        in user interfaces and reports.
        """
        test_cases = [
            (1, "1"),
            (10, "10"),
            (100, "100"),
            (1000, "1,000"),
            (10000, "10,000"),
            (100000, "100,000"),
            (1000000, "1,000,000"),
        ]

        for number, expected in test_cases:
            sosa = Sosa.from_int(number)
            formatted = sosa.format_with_separator(",")
            assert formatted == expected, (
                f"Sosa({number}).format_with_separator(',') should be "
                f"'{expected}', got '{formatted}'"
            )


# COVERAGE TESTS - Tests pour lignes non couvertes
class TestSosaCoverage:
    """Tests spécifiques pour atteindre 100% de coverage"""

    def test_negative_value_validation_line_36(self):
        """Test ligne 36: __post_init__ validation pour valeurs négatives"""
        with pytest.raises(ValueError, match="Sosa number must be non-negative"):
            Sosa(-1)

        with pytest.raises(ValueError, match="Sosa number must be non-negative"):
            Sosa(-42)

    def test_from_string_invalid_format_lines_91_92(self):
        """Test lignes 91-92: from_string avec format invalide"""
        with pytest.raises(ValueError, match="Cannot parse 'invalid' as Sosa number"):
            Sosa.from_string("invalid")

        with pytest.raises(ValueError, match="Cannot parse '12.34' as Sosa number"):
            Sosa.from_string("12.34")

        with pytest.raises(ValueError, match="Cannot parse 'abc123' as Sosa number"):
            Sosa.from_string("abc123")

        with pytest.raises(ValueError, match="Cannot parse '' as Sosa number"):
            Sosa.from_string("")

    def test_divide_by_zero_line_108(self):
        """Test ligne 108: divide_by avec diviseur zéro"""
        sosa = Sosa(10)
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            sosa.divide_by(0)

    def test_format_with_separator_negative_lines_132_133(self):
        """Test lignes 132-133: format_with_separator avec nombre négatif"""
        # Puisque Sosa ne devrait pas être négatif normalement, mais le code
        # gère ce cas, nous devons tester cette branche de code
        # En utilisant une méthode qui simule un nombre négatif

        # Créons temporairement un Sosa et utilisons l'héritage pour tester
        class TestableSosa(Sosa):
            def __init__(self, value):
                # Contourner la validation pour tester le formatage négatif
                object.__setattr__(self, "_value", value)

            @property
            def value(self):
                return self._value

        negative_sosa = TestableSosa(-1234)
        formatted = negative_sosa.format_with_separator(",")
        assert formatted == "-1,234"

        # Test avec un nombre négatif plus long
        negative_sosa_long = TestableSosa(-1234567)
        formatted_long = negative_sosa_long.format_with_separator(",")
        assert formatted_long == "-1,234,567"

    def test_eq_with_non_sosa_object_line_162(self):
        """Test ligne 162: __eq__ avec objet non-Sosa"""
        sosa = Sosa(42)

        # Test avec différents types d'objets
        assert sosa != 42  # int
        assert sosa != "42"  # str
        assert sosa != [42]  # list
        assert sosa != {"value": 42}  # dict
        assert sosa is not None  # None

    def test_hash_method_line_167(self):
        """Test ligne 167: __hash__ method"""
        sosa1 = Sosa(42)
        sosa2 = Sosa(42)
        sosa3 = Sosa(43)

        # Même valeur = même hash
        assert hash(sosa1) == hash(sosa2)

        # Valeurs différentes = hash différents
        assert hash(sosa1) != hash(sosa3)

        # Peut être utilisé dans un set
        sosa_set = {sosa1, sosa2, sosa3}
        assert len(sosa_set) == 2  # sosa1 et sosa2 sont identiques

    def test_repr_method_line_171(self):
        """Test ligne 171: __repr__ method"""
        test_cases = [
            (0, "Sosa(0)"),
            (1, "Sosa(1)"),
            (42, "Sosa(42)"),
            (12345, "Sosa(12345)"),
        ]

        for value, expected_repr in test_cases:
            sosa = Sosa(value)
            assert repr(sosa) == expected_repr, (
                f"repr(Sosa({value})) should be '{expected_repr}', "
                f"got '{repr(sosa)}'"
            )


# SOSA-005: Generation calculation from Sosa
class TestSosaGenerationCalculation:
    """
    Test generation calculation for Sosa numbers.

    In genealogical trees:
    - Generation 1: Sosa 1 (the proband/root person)
    - Generation 2: Sosa 2-3 (parents)
    - Generation 3: Sosa 4-7 (grandparents)
    - Generation 4: Sosa 8-15 (great-grandparents)
    etc.

    Formula: generation = floor(log2(sosa_number)) + 1
    """

    def test_generation_calculation_for_sosa_1_to_15(self):
        """Test SOSA-005: Calculate generation for each Sosa number 1-15"""
        # Expected generations based on genealogical tree structure
        expected_generations = [1, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4]

        for sosa_number in range(1, 16):
            sosa = Sosa(sosa_number)
            expected_generation = expected_generations[sosa_number - 1]
            actual_generation = sosa.generation()

            assert actual_generation == expected_generation, (
                f"Sosa({sosa_number}).generation() should be {expected_generation}, "
                f"got {actual_generation}"
            )

    def test_generation_edge_cases(self):
        """Test generation calculation for edge cases"""
        test_cases = [
            (1, 1),  # Root person
            (2, 2),  # Father
            (3, 2),  # Mother
            (4, 3),  # Paternal grandfather
            (7, 3),  # Maternal grandmother
            (8, 4),  # Great-grandfather
            (15, 4),  # Great-grandmother
            (16, 5),  # 2nd great-grandfather
            (31, 5),  # 2nd great-grandmother
            (32, 6),  # 3rd great-grandfather
        ]

        for sosa_number, expected_generation in test_cases:
            sosa = Sosa(sosa_number)
            actual_generation = sosa.generation()

            assert actual_generation == expected_generation, (
                f"Sosa({sosa_number}).generation() should be {expected_generation}, "
                f"got {actual_generation}"
            )

    def test_generation_large_numbers(self):
        """Test generation calculation for large Sosa numbers"""
        test_cases = [
            (64, 7),  # 4th great-grandfather
            (128, 8),  # 5th great-grandfather
            (256, 9),  # 6th great-grandfather
            (512, 10),  # 7th great-grandfather
            (1024, 11),  # 8th great-grandfather
        ]

        for sosa_number, expected_generation in test_cases:
            sosa = Sosa(sosa_number)
            actual_generation = sosa.generation()

            assert actual_generation == expected_generation, (
                f"Sosa({sosa_number}).generation() should be {expected_generation}, "
                f"got {actual_generation}"
            )

    def test_generation_zero_special_case(self):
        """Test generation calculation for Sosa 0 (special case)"""
        sosa_zero = Sosa(0)
        # Sosa 0 is a special case, should return 0 or handle appropriately
        generation = sosa_zero.generation()

        # Sosa 0 représente "pas d'ancêtre" donc génération 0
        assert generation == 0, f"Sosa(0).generation() should be 0, got {generation}"


# SOSA-006: Branch path calculation
class TestSosaBranchPathCalculation:
    """
    Test branch path calculation for Sosa numbers.

    The branch path represents the navigation from the root person to a specific
    ancestor in the genealogical tree using binary representation:
    - 0 = go to father (even Sosa numbers)
    - 1 = go to mother (odd Sosa numbers)

    Algorithm:
    1. Convert Sosa number to binary
    2. Remove the leftmost bit (generation marker)
    3. Read remaining bits from left to right
    4. Each bit represents father (0) or mother (1) choice
    """

    def test_branch_path_for_sosa_38(self):
        """Test SOSA-006: Calculate branch path for Sosa 38"""
        # Sosa 38 en binaire: 100110
        # Après suppression du bit de génération: 00110
        # Chemin: [0,0,1,1,0] (père, père, mère, mère, père)
        sosa = Sosa(38)
        expected_path = [0, 0, 1, 1, 0]
        actual_path = sosa.branch_path()

        assert actual_path == expected_path, (
            f"Sosa({38}).branch_path() should be {expected_path}, " f"got {actual_path}"
        )

    def test_branch_path_basic_cases(self):
        """Test branch path calculation for basic cases"""
        test_cases = [
            # (sosa_number, expected_path)
            (1, []),  # Root person - no path
            (2, [0]),  # Father
            (3, [1]),  # Mother
            (4, [0, 0]),  # Paternal grandfather
            (5, [0, 1]),  # Paternal grandmother
            (6, [1, 0]),  # Maternal grandfather
            (7, [1, 1]),  # Maternal grandmother
            (8, [0, 0, 0]),  # Great-grandfather (father's father's father)
            (9, [0, 0, 1]),  # Great-grandmother (father's father's mother)
        ]

        for sosa_number, expected_path in test_cases:
            sosa = Sosa(sosa_number)
            actual_path = sosa.branch_path()

            assert actual_path == expected_path, (
                f"Sosa({sosa_number}).branch_path() should be {expected_path}, "
                f"got {actual_path}"
            )

    def test_branch_path_complex_cases(self):
        """Test branch path calculation for complex ancestor paths"""
        test_cases = [
            # (sosa_number, expected_path, description)
            (10, [0, 1, 0], "Great-grandfather (father of mother of father)"),
            (11, [0, 1, 1], "Great-grandmother (mother of mother of father)"),
            (12, [1, 0, 0], "Great-grandfather (father of father of mother)"),
            (13, [1, 0, 1], "Great-grandmother (mother of father of mother)"),
            (15, [1, 1, 1], "All mothers path"),
            (16, [0, 0, 0, 0], "All fathers path (4 generations)"),
            (31, [1, 1, 1, 1], "All mothers path (4 generations)"),
        ]

        for sosa_number, expected_path, description in test_cases:
            sosa = Sosa(sosa_number)
            actual_path = sosa.branch_path()

            assert actual_path == expected_path, (
                f"Sosa({sosa_number}).branch_path() for {description} "
                f"should be {expected_path}, got {actual_path}"
            )

    def test_branch_path_edge_cases(self):
        """Test branch path calculation for edge cases"""
        # Test Sosa 0 - special case
        sosa_zero = Sosa(0)
        path_zero = sosa_zero.branch_path()
        assert path_zero == [], f"Sosa(0).branch_path() should be [], got {path_zero}"

        # Test large Sosa number
        sosa_large = Sosa(64)  # 1000000 in binary -> [0,0,0,0,0,0]
        expected_large = [0, 0, 0, 0, 0, 0]
        actual_large = sosa_large.branch_path()
        assert actual_large == expected_large, (
            f"Sosa(64).branch_path() should be {expected_large}, " f"got {actual_large}"
        )

    def test_branch_path_binary_logic(self):
        """Test that branch path correctly interprets binary representation"""
        # Vérifier quelques cas où on connaît la représentation binaire
        test_cases = [
            # Sosa 12 = 1100 binary -> remove first 1 -> 100 -> [1,0,0]
            (12, [1, 0, 0]),
            # Sosa 20 = 10100 binary -> remove first 1 -> 0100 -> [0,1,0,0]
            (20, [0, 1, 0, 0]),
            # Sosa 25 = 11001 binary -> remove first 1 -> 1001 -> [1,0,0,1]
            (25, [1, 0, 0, 1]),
        ]

        for sosa_number, expected_path in test_cases:
            sosa = Sosa(sosa_number)
            actual_path = sosa.branch_path()

            # Vérifier aussi en mode debug avec la représentation binaire
            binary_repr = bin(sosa_number)[2:]  # Remove '0b' prefix
            assert actual_path == expected_path, (
                f"Sosa({sosa_number}) binary={binary_repr} "
                f"branch_path() should be {expected_path}, got {actual_path}"
            )
