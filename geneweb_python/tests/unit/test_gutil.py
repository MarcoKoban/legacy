import geneweb.db.gutil as gutil
from geneweb.db.gutil import (
    alphabetic,
    alphabetic_order,
    alphabetic_utf_8,
    arg_list_of_string,
    couple,
    designation,
    father,
    find_free_occ,
    find_num,
    get_birth_death_date,
    mother,
    parent_array,
    person_of_string_dot_key,
    person_of_string_key,
    rsplit_key,
    sort_person_list,
    sort_uniq_person_list,
    split_key,
    spouse,
    trim_trailing_spaces,
)


class DummyBase:
    def p_first_name(self, p):
        return p.first_name

    def p_surname(self, p):
        return p.surname

    def get_occ(self, p):
        return p.occ

    def get_iper(self, p):
        return p.key_index

    def person_of_key(self, f, s, occ):
        return 42

    def persons_of_name(self, s):
        return [1, 2]

    def poi(self, ip):
        return DummyPerson("John", "Doe", occ=ip)

    def person_misc_names(self, p, fn):
        return ["John Doe", "J. Doe"]

    def get_titles(self, p):
        return ["title"]


class DummyPerson:
    def __init__(self, first_name, surname, occ=0, key_index=0, birth=None, death=None):
        self.first_name = first_name
        self.surname = surname
        self.occ = occ
        self.key_index = key_index
        self.birth = birth
        self.death = death


class DummyCouple:
    def __init__(self, father, mother):
        self.father = father
        self.mother = mother


def test_designation():
    base = DummyBase()
    p = DummyPerson("John", "Doe", occ=2)
    assert designation(base, p) == "John.2 Doe"


def test_couple_family_utils():
    cpl = DummyCouple(1, 2)
    assert father(cpl) == 1
    assert mother(cpl) == 2
    assert couple(False, 1, 2) == (1, 2)
    assert couple(True, 1, 2) == (1, 2, "multi")
    assert parent_array(cpl) == [1, 2]
    assert spouse(1, cpl) == 2
    assert spouse(2, cpl) == 1


def test_find_num():
    assert find_num("John.3 Doe", 0) == (3, 5)
    assert find_num("John Doe", 0) is None


def test_split_key():
    assert split_key("John.3 Doe", 0) == (0, "John", 3, "Doe")
    assert split_key("John Doe", 0) is None


def test_rsplit_key():
    assert rsplit_key("John.3 Doe") == ("John", 3, "Doe")
    assert rsplit_key("John Doe") is None


def test_person_of_string_key_and_dot_key():
    base = DummyBase()
    assert person_of_string_key(base, "John.3 Doe") == 42
    assert person_of_string_dot_key(base, "John.3 Doe") == 42


def test_trim_trailing_spaces():
    assert trim_trailing_spaces("abc   ") == "abc"
    assert trim_trailing_spaces("abc\n\t") == "abc"


def test_alphabetic_comparisons():
    assert alphabetic_utf_8("abc", "abd") == -1
    assert alphabetic("abc", "abd") == -1
    assert alphabetic_order("abc", "abc") == 0


def test_arg_list_of_string():
    args = arg_list_of_string('foo "bar baz" qux')
    # args is a list of tuples, flatten
    flat = ["".join([a for a in t if a]) for t in args]
    assert flat == ["foo", "bar baz", "qux"]


def test_sort_person_list_and_uniq():
    base = DummyBase()
    p1 = DummyPerson("John", "Doe", occ=1, key_index=1, birth="1900", death="1950")
    p2 = DummyPerson("Jane", "Doe", occ=2, key_index=2, birth="1910", death="1960")
    p3 = DummyPerson("John", "Doe", occ=1, key_index=1, birth="1900", death="1950")
    persons = [p2, p1, p3]
    sorted_persons = sort_person_list(base, persons)
    assert sorted_persons[0].first_name == "John"
    uniq_persons = sort_uniq_person_list(base, persons)
    assert len(uniq_persons) == 2


def test_find_free_occ():
    base = DummyBase()
    assert find_free_occ(base, "John", "Doe") == 0


def test_get_birth_death_date():
    p = DummyPerson("John", "Doe", birth="1900", death="1950")
    birth, death, approx = get_birth_death_date(p)
    assert birth == "1900"
    assert death == "1950"
    assert approx is False


def test_person_is_key_true_false():
    class Base:
        def p_first_name(self, p):
            return "John"

        def p_surname(self, p):
            return "Doe"

        def person_misc_names(self, p, fn):
            return ["John Doe", "J. Doe"]

        def get_titles(self, p):
            return []

    class P:
        pass

    base = Base()
    p = P()
    assert gutil.person_is_key(base, p, "John Doe")
    assert gutil.person_is_key(base, p, "J. Doe")
    assert not gutil.person_is_key(base, p, "Jane Doe")


def test_person_not_a_key_find_all():
    base = type("Base", (), {})()
    base.persons_of_name = lambda s: [1, 2]
    base.poi = lambda ip: type("P", (), {"first_name": "John", "surname": "Doe"})()
    base.p_first_name = lambda p: p.first_name
    base.p_surname = lambda p: p.surname
    base.person_misc_names = lambda p, fn: ["John Doe"]
    base.get_titles = lambda p: []
    res = gutil.person_not_a_key_find_all(base, "John Doe")
    assert isinstance(res, list)


def test_person_ht_find_all():
    base = type("Base", (), {})()
    base.persons_of_name = lambda s: [1]
    base.poi = lambda ip: type("P", (), {"first_name": "John", "surname": "Doe"})()
    base.p_first_name = lambda p: p.first_name
    base.p_surname = lambda p: p.surname
    base.person_misc_names = lambda p, fn: ["John Doe"]
    base.get_titles = lambda p: []
    base.person_of_key = lambda f, s, occ: 1
    res = gutil.person_ht_find_all(base, "John.0 Doe")
    assert res == [1]


def test_find_same_name():
    base = type("Base", (), {})()
    base.p_first_name = lambda p: "John"
    base.p_surname = lambda p: "Doe"
    base.persons_of_name = lambda s: [1]
    base.poi = lambda ip: type(
        "P", (), {"occ": 0, "first_name": "John", "surname": "Doe"}
    )()
    base.get_occ = lambda p: p.occ
    p = type("P", (), {"occ": 0, "first_name": "John", "surname": "Doe"})()
    res = gutil.find_same_name(base, p)
    assert isinstance(res, list)


def test_trim_trailing_spaces_edge():
    assert trim_trailing_spaces("abc\r\n\t   ") == "abc"
    assert trim_trailing_spaces("abc") == "abc"


def test_alphabetic_utf_8_and_order():
    assert alphabetic_utf_8("é", "e") == 1
    assert alphabetic_order("a", "b") == -1
