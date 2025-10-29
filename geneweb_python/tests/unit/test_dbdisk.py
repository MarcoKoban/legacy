from geneweb.db.dbdisk import (
    BaseData,
    BaseFunc,
    BaseVersion,
    DskBase,
    RecordAccess,
    StringPersonIndex,
    VisibleRecordAccess,
)


def test_record_access():
    loaded = []

    def load_array():
        loaded.append("loaded")

    def get(i):
        return i * 2

    def get_nopending(i):
        return i * 3

    def output_array(arr):
        loaded.append(arr)

    def clear_array():
        loaded.append("cleared")

    ra = RecordAccess(load_array, get, get_nopending, 5, output_array, clear_array)
    ra.load_array()
    assert loaded == ["loaded"]
    assert ra.get(2) == 4
    assert ra.get_nopending(2) == 6
    ra.output_array("arr")
    assert loaded[-1] == "arr"
    ra.clear_array()
    assert loaded[-1] == "cleared"
    assert ra.len == 5


def test_string_person_index():
    def find(i):
        return [i, i + 1]

    def cursor(s):
        return len(s)

    def next_(i):
        return i + 1

    spi = StringPersonIndex(find, cursor, next_)
    assert spi.find(3) == [3, 4]
    assert spi.cursor("abc") == 3
    assert spi.next(5) == 6


def test_visible_record_access():
    called = {}

    def v_write():
        called["write"] = True

    def v_get(fn, i):
        return fn(i)

    vra = VisibleRecordAccess(v_write, v_get)
    vra.v_write()
    assert called["write"] is True
    assert vra.v_get(lambda x: x > 2, 3)
    assert not vra.v_get(lambda x: x > 2, 1)


def test_base_data_and_func():
    ra = RecordAccess(
        lambda: None, lambda i: i, lambda i: i, 1, lambda arr: None, lambda: None
    )
    vra = VisibleRecordAccess(lambda: None, lambda fn, i: True)
    spi = StringPersonIndex(lambda i: [i], lambda s: 0, lambda i: i)
    bd = BaseData(
        persons=ra,
        ascends=ra,
        unions=ra,
        visible=vra,
        families=ra,
        couples=ra,
        descends=ra,
        strings=ra,
        particles_txt=["p"],
        particles=None,
        bnotes=None,
        bdir="dir",
        perm="RDONLY",
    )
    assert bd.persons.len == 1
    assert bd.bdir == "dir"
    bf = BaseFunc(
        person_of_key=lambda a, b, c: 42,
        persons_of_name=lambda s: [1, 2],
        strings_of_sname=lambda s: [3],
        strings_of_fname=lambda s: [4],
        persons_of_surname=spi,
        persons_of_first_name=spi,
        patch_person=lambda i, x: None,
        patch_ascend=lambda i, x: None,
        patch_union=lambda i, x: None,
        patch_family=lambda i, x: None,
        patch_couple=lambda i, x: None,
        patch_descend=lambda i, x: None,
        patch_name=lambda s, i: None,
        insert_string=lambda s: 99,
        commit_patches=lambda: None,
        commit_notes=lambda s1, s2: None,
        commit_wiznotes=lambda s1, s2: None,
        nb_of_real_persons=lambda: 7,
        iper_exists=lambda i: i == 1,
        ifam_exists=lambda i: i == 2,
    )
    assert bf.person_of_key("a", "b", 1) == 42
    assert bf.persons_of_name("x") == [1, 2]
    assert bf.strings_of_sname("y") == [3]
    assert bf.strings_of_fname("z") == [4]
    assert bf.insert_string("foo") == 99
    assert bf.nb_of_real_persons() == 7
    assert bf.iper_exists(1)
    assert not bf.iper_exists(0)
    assert bf.ifam_exists(2)
    assert not bf.ifam_exists(0)


def test_dsk_base():
    ra = RecordAccess(
        lambda: None, lambda i: i, lambda i: i, 1, lambda arr: None, lambda: None
    )
    vra = VisibleRecordAccess(lambda: None, lambda fn, i: True)
    spi = StringPersonIndex(lambda i: [i], lambda s: 0, lambda i: i)
    bd = BaseData(
        persons=ra,
        ascends=ra,
        unions=ra,
        visible=vra,
        families=ra,
        couples=ra,
        descends=ra,
        strings=ra,
        particles_txt=["p"],
        particles=None,
        bnotes=None,
        bdir="dir",
        perm="RDONLY",
    )
    bf = BaseFunc(
        person_of_key=lambda a, b, c: 42,
        persons_of_name=lambda s: [1, 2],
        strings_of_sname=lambda s: [3],
        strings_of_fname=lambda s: [4],
        persons_of_surname=spi,
        persons_of_first_name=spi,
        patch_person=lambda i, x: None,
        patch_ascend=lambda i, x: None,
        patch_union=lambda i, x: None,
        patch_family=lambda i, x: None,
        patch_couple=lambda i, x: None,
        patch_descend=lambda i, x: None,
        patch_name=lambda s, i: None,
        insert_string=lambda s: 99,
        commit_patches=lambda: None,
        commit_notes=lambda s1, s2: None,
        commit_wiznotes=lambda s1, s2: None,
        nb_of_real_persons=lambda: 7,
        iper_exists=lambda i: i == 1,
        ifam_exists=lambda i: i == 2,
    )
    db = DskBase(bd, bf, BaseVersion.GnWb0024)
    assert db.data.bdir == "dir"
    assert db.func.nb_of_real_persons() == 7
    assert db.version == BaseVersion.GnWb0024
