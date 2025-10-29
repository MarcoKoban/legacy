from typing import Any, List, Optional

# Identifiants
istr = int
ifam = int
iper = int


class Indexed:
    dummy = -1

    @staticmethod
    def is_dummy(t: int) -> bool:
        return t == Indexed.dummy

    @staticmethod
    def hash(t: int) -> int:
        return t

    @staticmethod
    def equal(t1: int, t2: int) -> bool:
        return t1 == t2

    @staticmethod
    def compare(t1: int, t2: int) -> int:
        return (t1 > t2) - (t1 < t2)

    @staticmethod
    def to_string(t: int) -> str:
        return str(t)

    @staticmethod
    def of_string(s: str) -> int:
        return int(s)


class Istr(Indexed):
    empty = 0
    quest = 1

    @staticmethod
    def is_empty(i: int) -> bool:
        return i == Istr.empty

    @staticmethod
    def is_quest(i: int) -> bool:
        return i == Istr.quest


Ifam = Indexed
Iper = Indexed


# Structures de base
class Base:
    def __init__(self, data: Any, func: Any, version: str):
        self.data = data
        self.func = func
        self.version = version


# Getters (stubs, à adapter selon le modèle Python)
def get_first_name(person: Any) -> istr:
    return person.first_name


def get_surname(person: Any) -> istr:
    return person.surname


def get_occ(person: Any) -> int:
    return person.occ


def get_iper(person: Any) -> iper:
    return person.key_index


def get_father(family: Any) -> iper:
    return family.father


def get_mother(family: Any) -> iper:
    return family.mother


def get_family(person: Any) -> List[ifam]:
    return person.family


def get_children(family: Any) -> List[iper]:
    return family.children


def get_titles(person: Any) -> List[Any]:
    return person.titles


def get_aliases(person: Any) -> List[istr]:
    return person.aliases


def get_first_names_aliases(person: Any) -> List[istr]:
    return person.first_names_aliases


def get_surnames_aliases(person: Any) -> List[istr]:
    return person.surnames_aliases


def get_public_name(person: Any) -> istr:
    return person.public_name


def get_qualifiers(person: Any) -> List[istr]:
    return person.qualifiers


def get_related(person: Any) -> List[iper]:
    return person.related


def get_rparents(person: Any) -> List[Any]:
    return person.rparents


def get_notes(person: Any) -> istr:
    return person.notes


def get_occupation(person: Any) -> istr:
    return person.occupation


def get_image(person: Any) -> istr:
    return person.image


def get_sex(person: Any) -> str:
    return person.sex


def get_birth(person: Any) -> Any:
    return person.birth


def get_birth_place(person: Any) -> istr:
    return person.birth_place


def get_birth_note(person: Any) -> istr:
    return person.birth_note


def get_birth_src(person: Any) -> istr:
    return person.birth_src


def get_baptism(person: Any) -> Any:
    return person.baptism


def get_baptism_place(person: Any) -> istr:
    return person.baptism_place


def get_baptism_note(person: Any) -> istr:
    return person.baptism_note


def get_baptism_src(person: Any) -> istr:
    return person.baptism_src


def get_death(person: Any) -> Any:
    return person.death


def get_death_place(person: Any) -> istr:
    return person.death_place


def get_death_note(person: Any) -> istr:
    return person.death_note


def get_death_src(person: Any) -> istr:
    return person.death_src


def get_burial(person: Any) -> Any:
    return person.burial


def get_burial_place(person: Any) -> istr:
    return person.burial_place


def get_burial_note(person: Any) -> istr:
    return person.burial_note


def get_burial_src(person: Any) -> istr:
    return person.burial_src


def get_pevents(person: Any) -> List[Any]:
    return person.pevents


def get_psources(person: Any) -> istr:
    return person.psources


def get_parents(person: Any) -> Optional[ifam]:
    return person.parents


def get_comment(family: Any) -> istr:
    return family.comment


def get_fsources(family: Any) -> istr:
    return family.fsources


def get_marriage(family: Any) -> Any:
    return family.marriage


def get_marriage_note(family: Any) -> istr:
    return family.marriage_note


def get_marriage_place(family: Any) -> istr:
    return family.marriage_place


def get_marriage_src(family: Any) -> istr:
    return family.marriage_src


def get_origin_file(family: Any) -> istr:
    return family.origin_file


def get_parent_array(family: Any) -> List[iper]:
    return family.parent_array


def get_relation(family: Any) -> Any:
    return family.relation


def get_witnesses(family: Any) -> List[iper]:
    return family.witnesses


def get_fevents(family: Any) -> List[Any]:
    return family.fevents


def get_ifam(family: Any) -> ifam:
    return family.fam_index


def get_divorce(family: Any) -> Any:
    return family.divorce


def get_separation(family: Any) -> Any:
    return family.separation


def get_family_of_gen_family(family: Any) -> Any:
    return family


def get_person_of_gen_person(person: Any) -> Any:
    return person


# Utilitaires


def sou(base: Base, i: istr) -> str:
    return base.data.strings.get(i)


def bname(base: Base) -> str:
    import os

    return os.path.splitext(os.path.basename(base.data.bdir))[0]


def nb_of_persons(base: Base) -> int:
    return base.data.persons.len


def nb_of_real_persons(base: Base) -> int:
    return base.func.nb_of_real_persons()


def nb_of_families(base: Base) -> int:
    return base.data.families.len


def insert_string(base: Base, s: str) -> istr:
    return base.func.insert_string(s)


def commit_patches(base: Base) -> None:
    base.func.commit_patches()


def commit_notes(base: Base, s: str) -> None:
    base.func.commit_notes(s)


def commit_wiznotes(base: Base, s: str) -> None:
    base.func.commit_wiznotes(s)


def person_of_key(
    base: Base, first_name: str, surname: str, occ: int
) -> Optional[iper]:
    return base.func.person_of_key(first_name, surname, occ)


def persons_of_name(base: Base, name: str) -> List[iper]:
    return base.func.persons_of_name(name)


def persons_of_first_name(base: Base) -> Any:
    return base.func.persons_of_first_name


def persons_of_surname(base: Base) -> Any:
    return base.func.persons_of_surname


def base_particles(base: Base) -> Any:
    return base.data.particles


def base_strings_of_first_name(base: Base, s: str) -> List[istr]:
    return base.func.strings_of_fname(s)


def base_strings_of_surname(base: Base, s: str) -> List[istr]:
    return base.func.strings_of_sname(s)


def load_ascends_array(base: Base) -> None:
    base.data.ascends.load_array()


def load_unions_array(base: Base) -> None:
    base.data.unions.load_array()


def load_couples_array(base: Base) -> None:
    base.data.couples.load_array()


def load_descends_array(base: Base) -> None:
    base.data.descends.load_array()


def load_strings_array(base: Base) -> None:
    base.data.strings.load_array()


def load_persons_array(base: Base) -> None:
    base.data.persons.load_array()


def load_families_array(base: Base) -> None:
    base.data.families.load_array()


def clear_ascends_array(base: Base) -> None:
    base.data.ascends.clear_array()


def clear_unions_array(base: Base) -> None:
    base.data.unions.clear_array()


def clear_couples_array(base: Base) -> None:
    base.data.couples.clear_array()


def clear_descends_array(base: Base) -> None:
    base.data.descends.clear_array()


def clear_strings_array(base: Base) -> None:
    base.data.strings.clear_array()


def clear_persons_array(base: Base) -> None:
    base.data.persons.clear_array()


def clear_families_array(base: Base) -> None:
    base.data.families.clear_array()
