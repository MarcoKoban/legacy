import os
import pickle

from geneweb.db.dutil import (
    IntHT,
    compare_fnames,
    compare_fnames_i,
    compare_snames,
    compare_snames_i,
    crush_lower,
    dsk_person_misc_names,
    name_index,
    nominative,
    output_value_no_sharing,
    p_first_name,
    p_surname,
    poi,
    sou,
)


class DummyBase:
    def __init__(self):
        self.data = type("Data", (), {})()
        self.data.persons = ["p0", "p1", "p2"]
        self.data.strings = ["John", "Doe", "Smith"]


class DummyPerson:
    def __init__(self, first_name, surname):
        self.first_name = first_name
        self.surname = surname


def test_intht():
    ht = IntHT()
    ht[1] = "a"
    assert ht[1] == "a"
    assert 1 in ht
    assert ht.get(2) is None


def test_crush_lower():
    assert crush_lower("Jean-Pierre") == "jean pierre"
    assert crush_lower("O'Neil") == "oneil"
    assert crush_lower("  Test  ") == "test"


def test_name_index():
    idx1 = name_index("Jean-Pierre")
    idx2 = name_index("Jean-Pierre")
    idx3 = name_index("Pierre")
    assert idx1 == idx2
    assert isinstance(idx1, int)
    assert idx1 != idx3


def test_compare_fnames():
    assert compare_fnames("Alice", "Bob") == -1
    assert compare_fnames("Bob", "Alice") == 1
    assert compare_fnames("Bob", "Bob") == 0


def test_compare_fnames_i():
    base = DummyBase()
    assert compare_fnames_i(base, 0, 1) == 1
    assert compare_fnames_i(base, 1, 0) == -1
    assert compare_fnames_i(base, 0, 0) == 0


def test_compare_snames():
    base = DummyBase()
    assert compare_snames(base, "Alice", "Bob") == -1
    assert compare_snames(base, "Bob", "Alice") == 1
    assert compare_snames(base, "Bob", "Bob") == 0


def test_compare_snames_i():
    base = DummyBase()
    assert compare_snames_i(base, 0, 1) == 1
    assert compare_snames_i(base, 1, 0) == -1
    assert compare_snames_i(base, 0, 0) == 0


def test_poi_sou():
    base = DummyBase()
    assert poi(base, 1) == "p1"
    assert sou(base, 2) == "Smith"


def test_p_first_name_p_surname_nominative():
    base = DummyBase()
    p = DummyPerson(0, 1)
    assert p_first_name(base, p) == "John"
    assert p_surname(base, p) == "Doe"
    assert nominative("Test") == "Test"


def test_output_value_no_sharing(tmp_path):
    file_path = os.path.join(tmp_path, "test.pkl")
    value = {"a": 1, "b": 2}
    output_value_no_sharing(file_path, value)
    with open(file_path, "rb") as f:
        loaded = pickle.load(f)
    assert loaded == value


def test_dsk_person_misc_names():
    base = DummyBase()
    p = DummyPerson(0, 1)
    result = dsk_person_misc_names(base, p, lambda x: ["nob"])
    assert result == ["John", "Doe"]
