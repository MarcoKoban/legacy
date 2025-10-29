"""
Tests for bidirectional relationships between Person and Family.
"""

from geneweb.core.family import Family
from geneweb.core.person import Person, Sex


class TestBidirectionalRelationships:
    """Test bidirectional relationships between Person and Family."""

    def test_add_child_maintains_bidirectional_relationship(self):
        """Test that adding a child to family updates both sides."""
        # Create family and child
        family = Family()
        child = Person(first_name="John", surname="Doe", sex=Sex.MALE)

        # Add child to family
        family.add_child(child)

        # Check both sides of the relationship
        assert child in family.children
        assert family in child.families_as_child
        assert len(child.families_as_child) == 1

    def test_remove_child_maintains_bidirectional_relationship(self):
        """Test that removing a child from family updates both sides."""
        # Create family and child
        family = Family()
        child = Person(first_name="John", surname="Doe", sex=Sex.MALE)

        # Add then remove child
        family.add_child(child)
        family.remove_child(child)

        # Check both sides of the relationship are cleaned
        assert child not in family.children
        assert family not in child.families_as_child
        assert len(child.families_as_child) == 0

    def test_add_parents_maintains_bidirectional_relationship(self):
        """Test that adding parents to family updates both sides."""
        # Create family and parents
        family = Family()
        father = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        mother = Person(first_name="Jane", surname="Doe", sex=Sex.FEMALE)

        # Add parents to family
        family.add_father(father)
        family.add_mother(mother)

        # Check both sides of the relationship
        assert father in family.father
        assert mother in family.mother
        assert family in father.families_as_parent
        assert family in mother.families_as_parent

    def test_remove_parents_maintains_bidirectional_relationship(self):
        """Test that removing parents from family updates both sides."""
        # Create family and parents
        family = Family()
        father = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        mother = Person(first_name="Jane", surname="Doe", sex=Sex.FEMALE)

        # Add then remove parents
        family.add_father(father)
        family.add_mother(mother)
        family.remove_father(father)
        family.remove_mother(mother)

        # Check both sides of the relationship are cleaned
        assert family.father is None
        assert family.mother is None
        assert family not in father.families_as_parent
        assert family not in mother.families_as_parent

    def test_person_get_spouses_method(self):
        """Test that person can find their spouses through families."""
        # Create family with parents
        family = Family()
        father = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        mother = Person(first_name="Jane", surname="Smith", sex=Sex.FEMALE)

        # Add parents to family
        family.add_father(father)
        family.add_mother(mother)

        # Test spouse finding
        father_spouses = father.get_spouses()
        mother_spouses = mother.get_spouses()

        assert mother in father_spouses
        assert father in mother_spouses
        assert len(father_spouses) == 1
        assert len(mother_spouses) == 1

    def test_person_get_children_method(self):
        """Test that person can find their children through families."""
        # Create family with parents and children
        family = Family()
        father = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        mother = Person(first_name="Jane", surname="Doe", sex=Sex.FEMALE)
        child1 = Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE)
        child2 = Person(first_name="Bob", surname="Doe", sex=Sex.MALE)

        # Set up family relationships
        family.add_father(father)
        family.add_mother(mother)
        family.add_child(child1)
        family.add_child(child2)

        # Test children finding
        father_children = father.get_children()
        mother_children = mother.get_children()

        assert child1 in father_children
        assert child2 in father_children
        assert child1 in mother_children
        assert child2 in mother_children
        assert len(father_children) == 2
        assert len(mother_children) == 2

    def test_person_get_parents_method(self):
        """Test that person can find their parents through families."""
        # Create family with parents and child
        family = Family()
        father = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        mother = Person(first_name="Jane", surname="Doe", sex=Sex.FEMALE)
        child = Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE)

        # Set up family relationships
        family.add_father(father)
        family.add_mother(mother)
        family.add_child(child)

        # Test parent finding
        child_parents = child.get_parents()

        assert father in child_parents
        assert mother in child_parents
        assert len(child_parents) == 2

    def test_multiple_marriages_support(self):
        """Test support for multiple marriages per person."""
        # Create person with two marriages
        person = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        spouse1 = Person(first_name="Jane", surname="Smith", sex=Sex.FEMALE)
        spouse2 = Person(first_name="Mary", surname="Johnson", sex=Sex.FEMALE)

        # Create two families
        family1 = Family()
        family2 = Family()

        # Set up first marriage
        family1.add_father(person)
        family1.add_mother(spouse1)

        # Set up second marriage
        family2.add_father(person)
        family2.add_mother(spouse2)

        # Test multiple marriages
        assert person.has_multiple_marriages()
        assert len(person.families_as_parent) == 2

        spouses = person.get_spouses()
        assert spouse1 in spouses
        assert spouse2 in spouses
        assert len(spouses) == 2

    def test_family_query_methods(self):
        """Test family query methods for checking membership."""
        # Create family with members
        family = Family()
        father = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        mother = Person(first_name="Jane", surname="Doe", sex=Sex.FEMALE)
        child = Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE)
        outsider = Person(first_name="Bob", surname="Smith", sex=Sex.MALE)

        # Set up family
        family.add_father(father)
        family.add_mother(mother)
        family.add_child(child)

        # Test membership queries
        assert family.is_member(father)
        assert family.is_member(mother)
        assert family.is_member(child)
        assert not family.is_member(outsider)

        assert family.is_parent(father)
        assert family.is_parent(mother)
        assert not family.is_parent(child)

        assert family.is_child(child)
        assert not family.is_child(father)
        assert not family.is_child(mother)

        # Test get methods
        all_parents = family.get_all_parents()
        assert father in all_parents
        assert mother in all_parents
        assert len(all_parents) == 2

        all_members = family.get_all_members()
        assert len(all_members) == 3
        assert father in all_members
        assert mother in all_members
        assert child in all_members

    def test_consistency_across_operations(self):
        """Test that relationships remain consistent
        across multiple operations."""
        # Create family and persons
        family = Family()
        father = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        mother = Person(first_name="Jane", surname="Doe", sex=Sex.FEMALE)
        child1 = Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE)
        child2 = Person(first_name="Bob", surname="Doe", sex=Sex.MALE)

        # Build family step by step
        family.add_father(father)
        assert len(father.families_as_parent) == 1

        family.add_mother(mother)
        assert len(mother.families_as_parent) == 1
        assert len(father.get_spouses()) == 1
        assert mother in father.get_spouses()

        family.add_child(child1)
        assert len(child1.families_as_child) == 1
        assert len(father.get_children()) == 1
        assert len(mother.get_children()) == 1

        family.add_child(child2)
        assert len(child2.families_as_child) == 1
        assert len(father.get_children()) == 2
        assert len(mother.get_children()) == 2

        # Remove child1
        family.remove_child(child1)
        assert len(child1.families_as_child) == 0
        assert len(father.get_children()) == 1
        assert len(mother.get_children()) == 1
        assert child2 in father.get_children()

        # Verify consistency
        for parent in [father, mother]:
            assert family in parent.families_as_parent
            assert len(parent.get_children()) == 1
            assert child2 in parent.get_children()

        assert family in child2.families_as_child
        assert len(child2.get_parents()) == 2
