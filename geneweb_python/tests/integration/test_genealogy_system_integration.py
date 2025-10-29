"""
Integration tests for the complete genealogical system.

This module tests the integration of all major features:
- Bidirectional relationships
- Sosa number inheritance
- Relationship validation
"""

from datetime import datetime

import pytest

from geneweb.core.event import Event
from geneweb.core.family import Family
from geneweb.core.person import Person, Sex
from geneweb.core.sosa import Sosa
from geneweb.core.validation import ValidationError


class TestGenealogySystemIntegration:
    """Test integration of all genealogical system features."""

    def test_complete_family_tree_with_validation_and_sosa(self):
        """Test complete family tree creation with all features enabled."""

        # Create family members with proper birth dates
        # Paternal grandparents (parents of father)
        grandparent_m_paternal = Person(
            "Grand",
            "Father",
            sex=Sex.MALE,
            birth=Event.from_datetime(datetime(1940, 1, 1)),
        )
        grandparent_f_paternal = Person(
            "Grand",
            "MotherP",
            sex=Sex.FEMALE,
            birth=Event.from_datetime(datetime(1942, 1, 1)),
        )

        # Maternal grandparents (parents of mother)
        grandparent_m_maternal = Person(
            "Grand",
            "FatherM",
            sex=Sex.MALE,
            birth=Event.from_datetime(datetime(1941, 1, 1)),
        )
        grandparent_f_maternal = Person(
            "Grand",
            "MotherM",
            sex=Sex.FEMALE,
            birth=Event.from_datetime(datetime(1943, 1, 1)),
        )

        parent_m = Person(
            "Father",
            "Person",
            sex=Sex.MALE,
            birth=Event.from_datetime(datetime(1970, 1, 1)),
        )
        parent_f = Person(
            "Mother",
            "Person",
            sex=Sex.FEMALE,
            birth=Event.from_datetime(datetime(1972, 1, 1)),
        )

        child1 = Person(
            "Child1",
            "Person",
            sex=Sex.MALE,
            birth=Event.from_datetime(datetime(1995, 1, 1)),
        )
        child2 = Person(
            "Child2",
            "Person",
            sex=Sex.FEMALE,
            birth=Event.from_datetime(datetime(1997, 1, 1)),
        )

        # Create paternal grandparent family (grandparents -> father)
        paternal_family = Family()
        paternal_family.add_father(grandparent_m_paternal, validate=True)
        paternal_family.add_mother(grandparent_f_paternal, validate=True)
        paternal_family.add_child(parent_m, validate=True)

        # Create maternal grandparent family (grandparents -> mother)
        maternal_family = Family()
        maternal_family.add_father(grandparent_m_maternal, validate=True)
        maternal_family.add_mother(grandparent_f_maternal, validate=True)
        maternal_family.add_child(parent_f, validate=True)

        # Create parent family
        parent_family = Family()
        parent_family.add_father(parent_m, validate=True)
        parent_family.add_mother(parent_f, validate=True)
        parent_family.add_child(child1, validate=True)
        parent_family.add_child(child2, validate=True)

        # Assign Sosa numbers starting from child1 as reference
        child1.add_sosa_and_propagate(Sosa(1))

        # Verify bidirectional relationships
        assert parent_m in child1.get_parents()
        assert parent_f in child1.get_parents()
        assert child1 in parent_m.get_children()
        assert child2 in parent_m.get_children()
        assert grandparent_m_paternal in parent_m.get_parents()
        assert grandparent_m_maternal in parent_f.get_parents()

        # Verify Sosa inheritance
        assert child1.has_sosa(Sosa(1))
        assert parent_m.has_sosa(Sosa(2))  # Father of 1
        assert parent_f.has_sosa(Sosa(3))  # Mother of 1
        assert grandparent_m_paternal.has_sosa(
            Sosa(4)
        )  # Father of 2 (paternal grandfather)
        assert grandparent_f_paternal.has_sosa(
            Sosa(5)
        )  # Mother of 2 (paternal grandmother)
        assert grandparent_m_maternal.has_sosa(
            Sosa(6)
        )  # Father of 3 (maternal grandfather)
        assert grandparent_f_maternal.has_sosa(
            Sosa(7)
        )  # Mother of 3 (maternal grandmother)

        # Verify family validation passes
        paternal_family.validate_family()
        maternal_family.validate_family()
        parent_family.validate_family()

    def test_validation_prevents_invalid_relationships(self):
        """Test that validation prevents various invalid relationships."""

        # Test self-parenting prevention
        person = Person("Self", "Parent", sex=Sex.MALE)
        family = Family()
        family.add_child(person, validate=False)  # Add as child first

        with pytest.raises(ValidationError, match="cannot be their own parent"):
            family.add_father(person, validate=True)

        # Test age gap validation
        too_young_parent = Person(
            "Young",
            "Parent",
            sex=Sex.MALE,
            birth=Event.from_datetime(datetime(1990, 1, 1)),
        )
        child = Person(
            "Child",
            "Person",
            sex=Sex.FEMALE,
            birth=Event.from_datetime(datetime(1995, 1, 1)),
        )

        invalid_family = Family()
        invalid_family.add_child(child, validate=False)

        with pytest.raises(ValidationError, match="too young to be parent"):
            invalid_family.add_father(too_young_parent, validate=True)

        # Test duplicate child prevention
        valid_parent = Person(
            "Valid",
            "Parent",
            sex=Sex.MALE,
            birth=Event.from_datetime(datetime(1970, 1, 1)),
        )
        child_for_dup_test = Person(
            "Child",
            "Dup",
            sex=Sex.FEMALE,
            birth=Event.from_datetime(datetime(1995, 1, 1)),
        )

        dup_family = Family()
        dup_family.add_father(valid_parent, validate=True)
        dup_family.add_child(child_for_dup_test, validate=True)

        with pytest.raises(ValidationError, match="already in this family"):
            dup_family.add_child(child_for_dup_test, validate=True)

    def test_complex_family_with_multiple_marriages(self):
        """Test complex family structure with multiple marriages and
        Sosa inheritance."""

        # Person with multiple marriages
        person_a = Person(
            "PersonA",
            "Multi",
            sex=Sex.MALE,
            birth=Event.from_datetime(datetime(1970, 1, 1)),
        )

        # First spouse and children
        spouse1 = Person(
            "Spouse1",
            "First",
            sex=Sex.FEMALE,
            birth=Event.from_datetime(datetime(1972, 1, 1)),
        )
        child1 = Person(
            "Child1",
            "First",
            sex=Sex.MALE,
            birth=Event.from_datetime(datetime(1995, 1, 1)),
        )
        child2 = Person(
            "Child2",
            "First",
            sex=Sex.FEMALE,
            birth=Event.from_datetime(datetime(1997, 1, 1)),
        )

        # Second spouse and children
        spouse2 = Person(
            "Spouse2",
            "Second",
            sex=Sex.FEMALE,
            birth=Event.from_datetime(datetime(1975, 1, 1)),
        )
        child3 = Person(
            "Child3",
            "Second",
            sex=Sex.MALE,
            birth=Event.from_datetime(datetime(2000, 1, 1)),
        )

        # Create first family
        family1 = Family()
        family1.add_father(person_a, validate=True)
        family1.add_mother(spouse1, validate=True)
        family1.add_child(child1, validate=True)
        family1.add_child(child2, validate=True)

        # Create second family
        family2 = Family()
        family2.add_father(person_a, validate=True)
        family2.add_mother(spouse2, validate=True)
        family2.add_child(child3, validate=True)

        # Verify bidirectional relationships
        spouses = person_a.get_spouses()
        assert spouse1 in spouses
        assert spouse2 in spouses
        assert len(spouses) == 2

        all_children = person_a.get_children()
        assert child1 in all_children
        assert child2 in all_children
        assert child3 in all_children
        assert len(all_children) == 3

        # Assign Sosa to child1 and verify propagation
        child1.add_sosa_and_propagate(Sosa(1))

        # Verify Sosa numbers
        assert child1.has_sosa(Sosa(1))
        assert person_a.has_sosa(Sosa(2))  # Father of 1
        assert spouse1.has_sosa(Sosa(3))  # Mother of 1

        # spouse2 and child3 should not have Sosa numbers from child1's tree
        assert not spouse2.has_any_sosa()
        assert not child3.has_any_sosa()

    def test_validation_can_be_bypassed_when_needed(self):
        """Test that validation can be bypassed for special cases or data migration."""

        # Create scenario that would normally be invalid
        person = Person("Invalid", "Scenario", sex=Sex.MALE)

        # This should work when validation is disabled
        family = Family()
        family.add_child(person, validate=False)
        family.add_father(person, validate=False)  # Self-parenting, normally invalid

        # Verify the invalid relationship was created
        assert person in family.children
        assert person in family.father
        assert family in person.families_as_child
        assert family in person.families_as_parent

        # But validation method should detect the issue
        with pytest.raises(ValidationError):
            family.validate_family()

    def test_system_performance_with_large_family_tree(self):
        """Test system performance with a larger family tree."""

        # Create a 4-generation family tree
        generations = []

        # Generation 1 (great-grandparents)
        gen1 = []
        for i in range(2):  # 2 great-grandparents
            person = Person(
                f"GreatGrandParent{i}",
                "Gen1",
                sex=Sex.MALE if i % 2 == 0 else Sex.FEMALE,
                birth=Event.from_datetime(datetime(1920 + i, 1, 1)),
            )
            gen1.append(person)
        generations.append(gen1)

        # Generation 2 (grandparents) - 2 people
        gen2 = []
        for i in range(2):
            person = Person(
                f"GrandParent{i}",
                "Gen2",
                sex=Sex.MALE if i % 2 == 0 else Sex.FEMALE,
                birth=Event.from_datetime(datetime(1950 + i, 1, 1)),
            )
            gen2.append(person)
        generations.append(gen2)

        # Generation 3 (parents) - 2 people
        gen3 = []
        for i in range(2):
            person = Person(
                f"Parent{i}",
                "Gen3",
                sex=Sex.MALE if i % 2 == 0 else Sex.FEMALE,
                birth=Event.from_datetime(datetime(1980 + i, 1, 1)),
            )
            gen3.append(person)
        generations.append(gen3)

        # Generation 4 (children) - 3 people
        gen4 = []
        for i in range(3):
            person = Person(
                f"Child{i}",
                "Gen4",
                sex=Sex.MALE if i % 2 == 0 else Sex.FEMALE,
                birth=Event.from_datetime(datetime(2000 + i, 1, 1)),
            )
            gen4.append(person)
        generations.append(gen4)

        # Create family relationships
        families = []

        # Great-grandparents -> grandparent
        family1 = Family()
        family1.add_father(gen1[0], validate=True)
        family1.add_mother(gen1[1], validate=True)
        family1.add_child(gen2[0], validate=True)
        families.append(family1)

        # Grandparents -> parent
        family2 = Family()
        family2.add_father(gen2[0], validate=True)
        family2.add_mother(gen2[1], validate=True)
        family2.add_child(gen3[0], validate=True)
        families.append(family2)

        # Parents -> children
        family3 = Family()
        family3.add_father(gen3[0], validate=True)
        family3.add_mother(gen3[1], validate=True)
        for child in gen4:
            family3.add_child(child, validate=True)
        families.append(family3)

        # Assign Sosa starting from first child
        gen4[0].add_sosa_and_propagate(Sosa(1))

        # Verify the tree structure
        assert len(gen4[0].get_parents()) == 2
        assert len(gen3[0].get_children()) == 3
        assert len(gen3[0].get_parents()) == 2

        # Verify Sosa propagation through 4 generations
        assert gen4[0].has_sosa(Sosa(1))  # Child
        assert gen3[0].has_sosa(Sosa(2))  # Father
        assert gen3[1].has_sosa(Sosa(3))  # Mother
        assert gen2[0].has_sosa(Sosa(4))  # Paternal Grandfather
        assert gen2[1].has_sosa(Sosa(5))  # Paternal Grandmother (corrected from 6)
        assert gen1[0].has_sosa(Sosa(8))  # Paternal Great-grandfather
        assert gen1[1].has_sosa(
            Sosa(9)
        )  # Paternal Great-grandmother (corrected from 12)

        # Validate all families
        for family in families:
            family.validate_family()  # Should not raise exceptions


if __name__ == "__main__":
    # Run integration tests
    tests = TestGenealogySystemIntegration()
    tests.test_complete_family_tree_with_validation_and_sosa()
    tests.test_validation_prevents_invalid_relationships()
    tests.test_complex_family_with_multiple_marriages()
    tests.test_validation_can_be_bypassed_when_needed()
    tests.test_system_performance_with_large_family_tree()
