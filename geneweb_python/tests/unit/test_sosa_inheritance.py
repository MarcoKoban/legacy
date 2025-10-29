"""
Tests for Sosa number inheritance and propagation in Family/Person
relationships.
"""

import pytest

from geneweb.core.family import Family
from geneweb.core.person import Person, Sex
from geneweb.core.sosa import Sosa


class TestSosaInheritance:
    """Test Sosa number inheritance and propagation."""

    def test_sosa_utility_methods(self):
        """Test Sosa utility methods for parent/child calculations."""
        # Test father_sosa
        sosa1 = Sosa(1)
        assert sosa1.father_sosa() == Sosa(2)

        sosa5 = Sosa(5)
        assert sosa5.father_sosa() == Sosa(10)

        # Test mother_sosa
        assert sosa1.mother_sosa() == Sosa(3)
        assert sosa5.mother_sosa() == Sosa(11)

        # Test child_sosa
        sosa2 = Sosa(2)
        sosa3 = Sosa(3)
        assert sosa2.child_sosa() == Sosa(1)
        assert sosa3.child_sosa() == Sosa(1)

        sosa10 = Sosa(10)
        sosa11 = Sosa(11)
        assert sosa10.child_sosa() == Sosa(5)
        assert sosa11.child_sosa() == Sosa(5)

        # Test invalid child_sosa
        with pytest.raises(ValueError):
            Sosa(0).child_sosa()
        with pytest.raises(ValueError):
            Sosa(1).child_sosa()

        # Test is_father_sosa / is_mother_sosa
        assert Sosa(2).is_father_sosa()
        assert Sosa(4).is_father_sosa()
        assert not Sosa(3).is_father_sosa()
        assert not Sosa(1).is_father_sosa()
        assert not Sosa(0).is_father_sosa()

        assert Sosa(3).is_mother_sosa()
        assert Sosa(5).is_mother_sosa()
        assert not Sosa(2).is_mother_sosa()
        assert not Sosa(1).is_mother_sosa()
        assert not Sosa(0).is_mother_sosa()

    def test_person_sosa_management(self):
        """Test Person's Sosa number management methods."""
        person = Person(first_name="John", surname="Doe", sex=Sex.MALE)

        # Initially no Sosa
        assert person.get_primary_sosa() is None
        assert len(person.get_all_sosa_numbers()) == 0

        # Add first Sosa
        sosa1 = Sosa(1)
        person.add_sosa(sosa1)
        assert person.get_primary_sosa() == sosa1
        assert person.has_sosa(sosa1)
        assert len(person.get_all_sosa_numbers()) == 1

        # Add second Sosa (higher number)
        sosa5 = Sosa(5)
        person.add_sosa(sosa5)
        assert person.get_primary_sosa() == sosa1  # Should remain 1 (smaller)
        assert person.has_sosa(sosa5)
        assert len(person.get_all_sosa_numbers()) == 2

        # Add smaller Sosa
        sosa0 = Sosa(0)
        person.add_sosa(sosa0)
        assert (
            person.get_primary_sosa() == sosa1
        )  # Should remain 1 (0 is not valid primary)

        # Test duplicate adding
        person.add_sosa(sosa1)  # Should not duplicate
        assert len(person.get_all_sosa_numbers()) == 3  # 0, 1, 5

    def test_calculate_parent_sosa_numbers(self):
        """Test calculation of parent Sosa numbers from child."""
        person = Person(first_name="Child", surname="Doe", sex=Sex.MALE)

        # Add Sosa 1 (root person)
        person.add_sosa(Sosa(1))
        father_sosa_list, mother_sosa_list = person.calculate_parent_sosa_numbers()

        assert len(father_sosa_list) == 1
        assert len(mother_sosa_list) == 1
        assert father_sosa_list[0] == Sosa(2)
        assert mother_sosa_list[0] == Sosa(3)

        # Add Sosa 5 (multiple Sosa)
        person.add_sosa(Sosa(5))
        father_sosa_list, mother_sosa_list = person.calculate_parent_sosa_numbers()

        assert len(father_sosa_list) == 2
        assert len(mother_sosa_list) == 2
        assert Sosa(2) in father_sosa_list
        assert Sosa(10) in father_sosa_list
        assert Sosa(3) in mother_sosa_list
        assert Sosa(11) in mother_sosa_list

    def test_calculate_child_sosa_numbers(self):
        """Test calculation of child Sosa numbers from parent."""
        person = Person(first_name="Parent", surname="Doe", sex=Sex.MALE)

        # Add parent Sosa numbers
        person.add_sosa(Sosa(2))  # Father of Sosa 1
        person.add_sosa(Sosa(6))  # Father of Sosa 3

        child_sosa_list = person.calculate_child_sosa_numbers()

        assert len(child_sosa_list) == 2
        assert Sosa(1) in child_sosa_list
        assert Sosa(3) in child_sosa_list

        # Test with invalid parent Sosa (should be ignored)
        person.add_sosa(Sosa(1))  # Not a valid parent Sosa
        child_sosa_list = person.calculate_child_sosa_numbers()
        assert len(child_sosa_list) == 2  # Still only 2

    def test_sosa_propagation_simple_family(self):
        """Test Sosa propagation in a simple family structure."""
        # Create family with root person (Sosa 1)
        family = Family()
        father = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        mother = Person(first_name="Jane", surname="Doe", sex=Sex.FEMALE)
        child = Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE)

        # Set child as Sosa 1 (root of genealogy)
        child.add_sosa(Sosa(1))

        # Add to family - should propagate Sosa automatically
        family.add_child(child)
        family.add_father(father)
        family.add_mother(mother)

        # Check propagation
        assert father.has_sosa(Sosa(2))
        assert mother.has_sosa(Sosa(3))
        assert father.get_primary_sosa() == Sosa(2)
        assert mother.get_primary_sosa() == Sosa(3)

    def test_sosa_propagation_down_the_tree(self):
        """Test Sosa propagation from parents to children."""
        # Create grandparents with Sosa numbers
        family = Family()
        grandfather = Person(first_name="Grand", surname="Father", sex=Sex.MALE)
        grandmother = Person(first_name="Grand", surname="Mother", sex=Sex.FEMALE)

        # Set grandparent Sosa numbers
        grandfather.add_sosa(Sosa(2))  # Father of root person
        grandmother.add_sosa(Sosa(3))  # Mother of root person

        # Add grandparents to family
        family.add_father(grandfather)
        family.add_mother(grandmother)

        # Add child (parent of root person) - should get Sosa 1
        parent = Person(first_name="Parent", surname="Name", sex=Sex.MALE)
        family.add_child(parent)

        # Check propagation
        assert parent.has_sosa(Sosa(1))
        assert parent.get_primary_sosa() == Sosa(1)

    def test_sosa_propagation_multiple_children(self):
        """Test Sosa propagation with multiple children."""
        # Create family
        family = Family()
        father = Person(first_name="Father", surname="Smith", sex=Sex.MALE)
        mother = Person(first_name="Mother", surname="Smith", sex=Sex.FEMALE)

        # Father is grandfather (Sosa 4), Mother is grandmother (Sosa 5)
        father.add_sosa(Sosa(4))
        mother.add_sosa(Sosa(5))

        family.add_father(father)
        family.add_mother(mother)

        # Add children - both should get Sosa 2 (since both 4//2 = 2 and 5//2 = 2)
        child1 = Person(first_name="Child1", surname="Smith", sex=Sex.MALE)
        child2 = Person(first_name="Child2", surname="Smith", sex=Sex.FEMALE)

        family.add_child(child1)
        family.add_child(child2)

        # Both children should have Sosa 2
        assert child1.has_sosa(Sosa(2))
        assert child2.has_sosa(Sosa(2))

    def test_sosa_propagation_implexes(self):
        """Test Sosa propagation with implexes."""
        # Create person who appears as both Sosa 6 and Sosa 7 (cousins marriage)
        person = Person(first_name="Implex", surname="Person", sex=Sex.MALE)
        person.add_sosa(Sosa(6))
        person.add_sosa(Sosa(7))

        # Create family where this person is both father and mother
        # (unusual but possible in genealogy)
        family = Family()
        family.add_father(person)
        # In reality, we'd have different persons, but this tests
        # the algorithm

        child = Person(first_name="Child", surname="Person", sex=Sex.FEMALE)
        family.add_child(child)

        # Child should inherit Sosa numbers from both parent roles
        # Sosa 6 -> child Sosa 3, Sosa 7 -> child Sosa 3 (same result)
        assert child.has_sosa(Sosa(3))

    def test_complex_family_tree_sosa_propagation(self):
        """Test Sosa propagation in a complex family tree."""
        # Create a 3-generation family tree

        # Generation 1 (root)
        root = Person(first_name="Root", surname="Person", sex=Sex.MALE)
        root.add_sosa(Sosa(1))

        # Generation 2 (parents)
        father = Person(first_name="Father", surname="Person", sex=Sex.MALE)
        mother = Person(first_name="Mother", surname="Person", sex=Sex.FEMALE)

        family_gen2 = Family()
        family_gen2.add_child(root)
        family_gen2.add_father(father)
        family_gen2.add_mother(mother)

        # Check generation 2 Sosa
        assert father.has_sosa(Sosa(2))
        assert mother.has_sosa(Sosa(3))

        # Generation 3 (grandparents)
        # Paternal grandparents
        pat_grandfather = Person(first_name="Pat", surname="Grandfather", sex=Sex.MALE)
        pat_grandmother = Person(
            first_name="Pat", surname="Grandmother", sex=Sex.FEMALE
        )

        family_pat = Family()
        family_pat.add_child(father)
        family_pat.add_father(pat_grandfather)
        family_pat.add_mother(pat_grandmother)

        # Maternal grandparents
        mat_grandfather = Person(first_name="Mat", surname="Grandfather", sex=Sex.MALE)
        mat_grandmother = Person(
            first_name="Mat", surname="Grandmother", sex=Sex.FEMALE
        )

        family_mat = Family()
        family_mat.add_child(mother)
        family_mat.add_father(mat_grandfather)
        family_mat.add_mother(mat_grandmother)

        # Check generation 3 Sosa
        assert pat_grandfather.has_sosa(Sosa(4))
        assert pat_grandmother.has_sosa(Sosa(5))
        assert mat_grandfather.has_sosa(Sosa(6))
        assert mat_grandmother.has_sosa(Sosa(7))

    def test_sosa_consistency_with_existing_tests(self):
        """Test that Sosa inheritance doesn't break existing functionality."""
        # This test ensures our Sosa changes don't break bidirectional relationships
        family = Family()
        father = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        mother = Person(first_name="Jane", surname="Doe", sex=Sex.FEMALE)
        child = Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE)

        # Set up family relationships first
        family.add_father(father)
        family.add_mother(mother)
        family.add_child(child)

        # Add Sosa to child and propagate
        child.add_sosa_and_propagate(Sosa(1))

        # Check bidirectional relationships still work
        assert child in family.children
        assert family in child.families_as_child
        assert family in father.families_as_parent
        assert family in mother.families_as_parent

        # Check Sosa propagation also worked
        assert father.has_sosa(Sosa(2))
        assert mother.has_sosa(Sosa(3))

        # Check person can still find spouses and children
        father_spouses = father.get_spouses()
        assert mother in father_spouses

        father_children = father.get_children()
        assert child in father_children

    def test_sosa_propagation_edge_cases(self):
        """Test edge cases in Sosa propagation."""
        # Test with Sosa 0 (should be ignored)
        person = Person(first_name="Test", surname="Person", sex=Sex.MALE)
        person.add_sosa(Sosa(0))

        father_sosa_list, mother_sosa_list = person.calculate_parent_sosa_numbers()
        assert len(father_sosa_list) == 0
        assert len(mother_sosa_list) == 0

        # Test propagation with no Sosa numbers
        family = Family()
        father = Person(first_name="Father", surname="Test", sex=Sex.MALE)
        child = Person(first_name="Child", surname="Test", sex=Sex.FEMALE)

        family.add_father(father)
        family.add_child(child)

        # Should not crash, no propagation should occur
        assert len(father.get_all_sosa_numbers()) == 0
        assert len(child.get_all_sosa_numbers()) == 0

    def test_manual_sosa_propagation_methods(self):
        """Test manual Sosa propagation methods."""
        # Create family structure
        family = Family()
        father = Person(first_name="Father", surname="Test", sex=Sex.MALE)
        mother = Person(first_name="Mother", surname="Test", sex=Sex.FEMALE)
        child = Person(first_name="Child", surname="Test", sex=Sex.FEMALE)

        # Set up family without Sosa
        family.add_father(father)
        family.add_mother(mother)
        family.add_child(child)

        # Manually set child Sosa and propagate
        child.add_sosa(Sosa(1))
        child.propagate_sosa_to_parents()

        # Check propagation
        assert father.has_sosa(Sosa(2))
        assert mother.has_sosa(Sosa(3))

        # Test reverse propagation
        # Add grandparents
        grandfather = Person(first_name="Grandfather", surname="Test", sex=Sex.MALE)
        grandmother = Person(first_name="Grandmother", surname="Test", sex=Sex.FEMALE)
        grandfather.add_sosa(Sosa(4))
        grandmother.add_sosa(Sosa(5))

        # Propagate down
        grandfather.propagate_sosa_to_children()
        grandmother.propagate_sosa_to_children()

        # This won't work automatically because we need to create the family first
        # But we can test the calculation methods
        child_sosa_list = grandfather.calculate_child_sosa_numbers()
        assert Sosa(2) in child_sosa_list
