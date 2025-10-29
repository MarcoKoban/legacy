from typing import Any, Callable, List, Optional


# Types de base (à adapter selon la définition Python de gen_person, gen_family, etc.)
class DskPerson:
    pass  # Remplacer par la vraie structure


class DskAscend:
    pass


class DskUnion:
    pass


class DskFamily:
    pass


class DskCouple:
    pass


class DskDescend:
    pass


class DskTitle:
    pass


class RecordAccess:
    def __init__(
        self,
        load_array: Callable[[], None],
        get: Callable[[int], Any],
        get_nopending: Callable[[int], Any],
        len_: int,
        output_array: Callable[[Any], None],
        clear_array: Callable[[], None],
    ):
        self.load_array = load_array
        self.get = get
        self.get_nopending = get_nopending
        self.len = len_
        self.output_array = output_array
        self.clear_array = clear_array


class StringPersonIndex:
    def __init__(
        self,
        find: Callable[[int], List[int]],
        cursor: Callable[[str], int],
        next_: Callable[[int], int],
    ):
        self.find = find
        self.cursor = cursor
        self.next = next_


class VisibleRecordAccess:
    def __init__(
        self,
        v_write: Callable[[], None],
        v_get: Callable[[Callable[[Any], bool], int], bool],
    ):
        self.v_write = v_write
        self.v_get = v_get


class Perm:
    RDONLY = "RDONLY"
    RDRW = "RDRW"


class BaseData:
    def __init__(
        self,
        persons: RecordAccess,
        ascends: RecordAccess,
        unions: RecordAccess,
        visible: VisibleRecordAccess,
        families: RecordAccess,
        couples: RecordAccess,
        descends: RecordAccess,
        strings: RecordAccess,
        particles_txt: List[str],
        particles: Any,
        bnotes: Any,
        bdir: str,
        perm: str,
    ):
        self.persons = persons
        self.ascends = ascends
        self.unions = unions
        self.visible = visible
        self.families = families
        self.couples = couples
        self.descends = descends
        self.strings = strings
        self.particles_txt = particles_txt
        self.particles = particles
        self.bnotes = bnotes
        self.bdir = bdir
        self.perm = perm


class BaseFunc:
    def __init__(
        self,
        person_of_key: Callable[[str, str, int], Optional[int]],
        persons_of_name: Callable[[str], List[int]],
        strings_of_sname: Callable[[str], List[int]],
        strings_of_fname: Callable[[str], List[int]],
        persons_of_surname: StringPersonIndex,
        persons_of_first_name: StringPersonIndex,
        patch_person: Callable[[int, Any], None],
        patch_ascend: Callable[[int, Any], None],
        patch_union: Callable[[int, Any], None],
        patch_family: Callable[[int, Any], None],
        patch_couple: Callable[[int, Any], None],
        patch_descend: Callable[[int, Any], None],
        patch_name: Callable[[str, int], None],
        insert_string: Callable[[str], int],
        commit_patches: Callable[[], None],
        commit_notes: Callable[[str, str], None],
        commit_wiznotes: Callable[[str, str], None],
        nb_of_real_persons: Callable[[], int],
        iper_exists: Callable[[int], bool],
        ifam_exists: Callable[[int], bool],
    ):
        self.person_of_key = person_of_key
        self.persons_of_name = persons_of_name
        self.strings_of_sname = strings_of_sname
        self.strings_of_fname = strings_of_fname
        self.persons_of_surname = persons_of_surname
        self.persons_of_first_name = persons_of_first_name
        self.patch_person = patch_person
        self.patch_ascend = patch_ascend
        self.patch_union = patch_union
        self.patch_family = patch_family
        self.patch_couple = patch_couple
        self.patch_descend = patch_descend
        self.patch_name = patch_name
        self.insert_string = insert_string
        self.commit_patches = commit_patches
        self.commit_notes = commit_notes
        self.commit_wiznotes = commit_wiznotes
        self.nb_of_real_persons = nb_of_real_persons
        self.iper_exists = iper_exists
        self.ifam_exists = ifam_exists


class BaseVersion:
    GnWb0020 = "GnWb0020"
    GnWb0021 = "GnWb0021"
    GnWb0022 = "GnWb0022"
    GnWb0023 = "GnWb0023"
    GnWb0024 = "GnWb0024"


class DskBase:
    def __init__(self, data: BaseData, func: BaseFunc, version: str):
        self.data = data
        self.func = func
        self.version = version
