import pytest

from geneweb.core.family import Family
from geneweb.core.person import Person, Sex
from geneweb.core.sosa import Sosa


class DummyParent(Person):
    def get_all_sosa_numbers(self):
        # Return a parent Sosa < 2 and one >= 2 to test both branches
        return [Sosa(1), Sosa(2)]


class DummyChild(Person):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sosa_added = []

    def add_sosa(self, sosa):
        self.sosa_added.append(sosa)


@pytest.mark.parametrize("parent_sosa_value,should_raise", [(1, True), (2, False)])
def test_propagate_sosa_to_child_valueerror(
    monkeypatch, parent_sosa_value, should_raise
):
    # Setup family with dummy parents
    child = DummyChild(first_name="Test", surname="Child", sex=Sex.MALE, occ=0)
    family = Family()
    parent = DummyParent(first_name="Parent", surname="Test", sex=Sex.MALE, occ=0)
    # Patch get_all_sosa_numbers to return the desired value
    parent.get_all_sosa_numbers = lambda: [Sosa(parent_sosa_value)]
    family.father = [parent]
    family.mother = None

    # Patch child.add_sosa to raise ValueError for Sosa < 2
    def add_sosa(sosa):
        if sosa.value < 1:
            raise ValueError("Invalid Sosa")
        child.sosa_added.append(sosa)

    child.add_sosa = add_sosa
    # Patch Sosa.child_sosa to raise ValueError for Sosa < 2
    orig_child_sosa = Sosa.child_sosa

    def child_sosa(self):
        if self.value < 2:
            raise ValueError("Sosa < 2 cannot have child")
        return Sosa(self.value // 2)

    Sosa.child_sosa = child_sosa
    # Should not raise for Sosa >= 2, should raise and continue for Sosa < 2
    family._propagate_sosa_to_child(child)
    Sosa.child_sosa = orig_child_sosa
    # For Sosa=2, child should have Sosa(1) added
    if not should_raise:
        assert child.sosa_added and child.sosa_added[0] == Sosa(1)
    else:
        assert not child.sosa_added
