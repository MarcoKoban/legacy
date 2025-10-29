from geneweb.db.driver import (
    Indexed,
    Istr,
    get_aliases,
    get_baptism,
    get_baptism_note,
    get_baptism_place,
    get_baptism_src,
    get_birth,
    get_birth_note,
    get_birth_place,
    get_birth_src,
    get_burial,
    get_burial_note,
    get_burial_place,
    get_burial_src,
    get_children,
    get_comment,
    get_death,
    get_death_note,
    get_death_place,
    get_death_src,
    get_divorce,
    get_family,
    get_family_of_gen_family,
    get_father,
    get_fevents,
    get_first_name,
    get_first_names_aliases,
    get_fsources,
    get_ifam,
    get_image,
    get_iper,
    get_marriage,
    get_marriage_note,
    get_marriage_place,
    get_marriage_src,
    get_mother,
    get_notes,
    get_occ,
    get_occupation,
    get_origin_file,
    get_parent_array,
    get_parents,
    get_person_of_gen_person,
    get_pevents,
    get_psources,
    get_public_name,
    get_qualifiers,
    get_related,
    get_relation,
    get_rparents,
    get_separation,
    get_sex,
    get_surname,
    get_surnames_aliases,
    get_titles,
    get_witnesses,
)


class DummyPerson:
    def __init__(self):
        self.first_name = 42
        self.surname = 43
        self.occ = 1
        self.key_index = 99
        self.family = [7, 8]
        self.titles = ["title"]
        self.aliases = [44]
        self.first_names_aliases = [45]
        self.surnames_aliases = [46]
        self.public_name = 47
        self.qualifiers = [48]
        self.related = [100]
        self.rparents = [101]
        self.notes = 49
        self.occupation = 50
        self.image = 51
        self.sex = "M"
        self.birth = "birth"
        self.birth_place = 52
        self.birth_note = 53
        self.birth_src = 54
        self.baptism = "baptism"
        self.baptism_place = 55
        self.baptism_note = 56
        self.baptism_src = 57
        self.death = "death"
        self.death_place = 58
        self.death_note = 59
        self.death_src = 60
        self.burial = "burial"
        self.burial_place = 61
        self.burial_note = 62
        self.burial_src = 63
        self.pevents = ["event"]
        self.psources = 64
        self.parents = 65


class DummyFamily:
    def __init__(self):
        self.father = 1
        self.mother = 2
        self.children = [3, 4]
        self.comment = 5
        self.fsources = 6
        self.marriage = "marriage"
        self.marriage_note = 7
        self.marriage_place = 8
        self.marriage_src = 9
        self.origin_file = 10
        self.parent_array = [11, 12]
        self.relation = "relation"
        self.witnesses = [13, 14]
        self.fevents = ["fevent"]
        self.fam_index = 15
        self.divorce = "divorce"
        self.separation = "separation"


def test_indexed_methods():
    assert Indexed.is_dummy(-1)
    assert not Indexed.is_dummy(0)
    assert Indexed.hash(5) == 5
    assert Indexed.equal(2, 2)
    assert not Indexed.equal(2, 3)
    assert Indexed.compare(2, 3) == -1
    assert Indexed.compare(3, 2) == 1
    assert Indexed.compare(2, 2) == 0
    assert Indexed.to_string(7) == "7"
    assert Indexed.of_string("8") == 8


def test_istr_methods():
    assert Istr.is_empty(0)
    assert not Istr.is_empty(2)
    assert Istr.is_quest(1)
    assert not Istr.is_quest(0)


def test_getters_person():
    p = DummyPerson()
    assert get_first_name(p) == 42
    assert get_surname(p) == 43
    assert get_occ(p) == 1
    assert get_iper(p) == 99
    assert get_family(p) == [7, 8]
    assert get_titles(p) == ["title"]
    assert get_aliases(p) == [44]
    assert get_first_names_aliases(p) == [45]
    assert get_surnames_aliases(p) == [46]
    assert get_public_name(p) == 47
    assert get_qualifiers(p) == [48]
    assert get_related(p) == [100]
    assert get_rparents(p) == [101]
    assert get_notes(p) == 49
    assert get_occupation(p) == 50
    assert get_image(p) == 51
    assert get_sex(p) == "M"
    assert get_birth(p) == "birth"
    assert get_birth_place(p) == 52
    assert get_birth_note(p) == 53
    assert get_birth_src(p) == 54
    assert get_baptism(p) == "baptism"
    assert get_baptism_place(p) == 55
    assert get_baptism_note(p) == 56
    assert get_baptism_src(p) == 57
    assert get_death(p) == "death"
    assert get_death_place(p) == 58
    assert get_death_note(p) == 59
    assert get_death_src(p) == 60
    assert get_burial(p) == "burial"
    assert get_burial_place(p) == 61
    assert get_burial_note(p) == 62
    assert get_burial_src(p) == 63
    assert get_pevents(p) == ["event"]
    assert get_psources(p) == 64
    assert get_parents(p) == 65


def test_getters_family():
    f = DummyFamily()
    assert get_father(f) == 1
    assert get_mother(f) == 2
    assert get_children(f) == [3, 4]
    assert get_comment(f) == 5
    assert get_fsources(f) == 6
    assert get_marriage(f) == "marriage"
    assert get_marriage_note(f) == 7
    assert get_marriage_place(f) == 8
    assert get_marriage_src(f) == 9
    assert get_origin_file(f) == 10
    assert get_parent_array(f) == [11, 12]
    assert get_relation(f) == "relation"
    assert get_witnesses(f) == [13, 14]
    assert get_fevents(f) == ["fevent"]
    assert get_ifam(f) == 15
    assert get_divorce(f) == "divorce"
    assert get_separation(f) == "separation"
    assert get_family_of_gen_family(f) == f


def test_get_person_of_gen_person():
    p = DummyPerson()
    assert get_person_of_gen_person(p) == p
