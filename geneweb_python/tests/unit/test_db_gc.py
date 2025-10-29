from geneweb.db.db_gc import (
    EMPTY_STRING,
    QUEST_STRING,
    empty_person,
    gc,
)


class DummyPerson:
    def __init__(self, first_name, surname, image=EMPTY_STRING):
        self.first_name = first_name
        self.surname = surname
        self.image = image
        self.first_names_aliases = []
        self.surnames_aliases = []
        self.public_name = EMPTY_STRING
        self.qualifiers = []
        self.titles = []
        self.rparents = []
        self.related = []
        self.aliases = []
        self.occupation = EMPTY_STRING
        self.sex = "Neuter"
        self.birth = "Date_None"
        self.birth_place = EMPTY_STRING
        self.birth_note = EMPTY_STRING
        self.birth_src = EMPTY_STRING
        self.baptism = "Date_None"
        self.baptism_place = EMPTY_STRING
        self.baptism_note = EMPTY_STRING
        self.baptism_src = EMPTY_STRING
        self.death = "DontKnowIfDead"
        self.death_place = EMPTY_STRING
        self.death_note = EMPTY_STRING
        self.death_src = EMPTY_STRING
        self.burial = "UnknownBurial"
        self.burial_place = EMPTY_STRING
        self.burial_note = EMPTY_STRING
        self.burial_src = EMPTY_STRING
        self.pevents = []
        self.notes = EMPTY_STRING
        self.psources = EMPTY_STRING


class DummyArray:
    def __init__(self, items):
        self.items = items
        self.len = len(items)

    def load_array(self):
        pass

    def get(self, i):
        return self.items[i]


class DummyBase:
    def __init__(self, persons, families, strings):
        self.data = type("Data", (), {})()
        self.data.persons = DummyArray(persons)
        self.data.ascends = DummyArray([])
        self.data.unions = DummyArray([])
        self.data.families = DummyArray(families)
        self.data.couples = DummyArray([])
        self.data.descends = DummyArray([])
        self.data.strings = DummyArray(strings)


def test_empty_person_true():
    p = DummyPerson(EMPTY_STRING, EMPTY_STRING)
    assert empty_person(p)
    p2 = DummyPerson(QUEST_STRING, QUEST_STRING)
    assert empty_person(p2)


def test_empty_person_false():
    p = DummyPerson("John", "Doe")
    assert not empty_person(p)


def test_gc_dry_run_marks_non_empty():
    # 2 personnes vides, 1 non vide
    persons = [
        DummyPerson(EMPTY_STRING, EMPTY_STRING),
        DummyPerson(QUEST_STRING, QUEST_STRING),
        DummyPerson("John", "Doe"),
    ]
    families = []
    strings = ["a", "b", "c"]
    base = DummyBase(persons, families, strings)
    deletedp, deletedf, deleteds = gc(base, dry_run=True)
    # Seule personne non vide marquée, donc les deux premières supprimées
    assert set(deletedp) == {1, 0}
    assert deletedf == []
    assert set(deleteds) == {2}


def test_gc_dry_run_all_empty():
    persons = [DummyPerson(EMPTY_STRING, EMPTY_STRING) for _ in range(3)]
    families = []
    strings = []
    base = DummyBase(persons, families, strings)
    deletedp, deletedf, deleteds = gc(base, dry_run=True)
    assert set(deletedp) == {2, 1, 0}
    assert deletedf == []
    assert deleteds == []
