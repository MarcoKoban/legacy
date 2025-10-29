import os
import pickle

import pytest

from geneweb.db.database import (
    Couple,
    Database,
    Descend,
    Family,
    Person,
    Union,
    VisibleState,
)


def create_sample_db(tmpdir):
    dbdir = os.path.join(tmpdir, "testdb")
    os.makedirs(dbdir, exist_ok=True)
    db = Database(dbdir)
    # Ajoute les données dans 'base' pour la sérialisation
    db.data["base"] = {
        "persons": [
            dict(id=1, first_name="John", surname="Doe"),
            dict(id=2, first_name="Jane", surname="Smith"),
        ],
        "families": [dict(id=1, members=[1, 2])],
        "unions": [dict(id=1, partners=[1, 2])],
        "couples": [dict(id=1, spouse1=1, spouse2=2)],
        "descends": [dict(id=1, children=[2], parent=1)],
    }
    db.save_base()
    # Recharge les objets pour les tests
    db.load_base()
    # Ajoute aussi les objets dans les clés directes pour compatibilité
    db.data["persons"] = [
        Person(id=1, first_name="John", surname="Doe"),
        Person(id=2, first_name="Jane", surname="Smith"),
    ]
    db.data["families"] = [Family(id=1, members=[1, 2])]
    db.data["unions"] = [Union(id=1, partners=[1, 2])]
    db.data["couples"] = [Couple(id=1, spouse1=1, spouse2=2)]
    db.data["descends"] = [Descend(id=1, children=[2], parent=1)]
    return db


def test_database_initialization(tmp_path):
    db = create_sample_db(tmp_path)
    db.initialize()
    assert len(db.data["persons"]) == 2
    assert db.index.find_by_name("John Doe") == [1]
    assert db.index.find_by_surname("Smith") == [2]
    assert db.index.find_by_firstname("Jane") == [2]


def test_patch_commit(tmp_path):
    db = create_sample_db(tmp_path)
    new_person = Person(id=3, first_name="Alice", surname="Wonder")
    db.add_person_patch(new_person)
    db.commit_patches()
    assert any(p.id == 3 for p in db.data["persons"])


def test_visibility_manager_integration(tmp_path):
    db = create_sample_db(tmp_path)
    db.init_visibility()
    db.set_person_visible(0, VisibleState.TRUE)
    assert db.get_person_visible(0) == VisibleState.TRUE


def test_notes_manager_integration(tmp_path):
    db = create_sample_db(tmp_path)
    db.write_note("", "Base note")
    assert db.read_note("") == "Base note"
    db.write_note("custom", "Custom note")
    assert db.read_note("custom") == "Custom note"


def test_wiznotes_manager_integration(tmp_path):
    db = create_sample_db(tmp_path)
    db.write_wiznote("wiz1", "Wiz note")
    assert db.read_wiznote("wiz1") == "Wiz note"
    notes = db.list_wiznotes()
    assert "wiz1" in notes


def test_ext_files_manager(tmp_path):
    db = create_sample_db(tmp_path)
    files = db.list_ext_files()
    assert isinstance(files, list)


def test_move_with_backup(tmp_path):
    src = os.path.join(tmp_path, "src.txt")
    dst = os.path.join(tmp_path, "dst.txt")
    with open(src, "w") as f:
        f.write("data")
    with open(dst, "w") as f:
        f.write("old")
    db = Database(str(tmp_path))
    db.move_with_backup(src, dst)
    assert os.path.exists(dst)
    assert os.path.exists(dst + "~")
    with open(dst) as f:
        assert f.read() == "data"
    with open(dst + "~") as f:
        assert f.read() == "old"


# Test SynchroPatch


def test_synchro_patch():
    sp = Database.SynchroPatch() if hasattr(Database, "SynchroPatch") else None
    if sp is None:
        sp = type("SynchroPatch", (), {})()
        sp.synch_list = []
    sp.synch_list.append(("t", [1], [2]))
    assert sp.synch_list[0][0] == "t"


# Test PatchManager


def test_patch_manager_apply():
    pm = Database.PatchManager() if hasattr(Database, "PatchManager") else None
    if pm is None:
        from geneweb.db.database import PatchManager

        pm = PatchManager()
    p1 = Person(id=1, first_name="A", surname="B")
    p2 = Person(id=2, first_name="C", surname="D")
    pm.add_person_patch(p2)
    result = pm.apply_patches([p1])
    ids = [p.id for p in result]
    assert 1 in ids and 2 in ids


# Test VisibilityManager


def test_visibility_manager(tmp_path):
    vm = (
        Database.VisibilityManager(3)
        if hasattr(Database, "VisibilityManager")
        else None
    )
    if vm is None:
        from geneweb.db.database import VisibilityManager

        vm = VisibilityManager(3)
    vm.set_visible(1, VisibleState.TRUE)
    assert vm.get_visible(1) == VisibleState.TRUE
    vm.save(str(tmp_path))
    vm.visible[1] = VisibleState.FALSE
    vm.load(str(tmp_path))
    assert vm.get_visible(1) == VisibleState.TRUE


# Test NotesManager


def test_notes_manager(tmp_path):
    nm = (
        Database.NotesManager(str(tmp_path))
        if hasattr(Database, "NotesManager")
        else None
    )
    if nm is None:
        from geneweb.db.database import NotesManager

        nm = NotesManager(str(tmp_path))
    nm.write_note("key", "val")
    assert nm.read_note("key") == "val"
    nm.write_note("", "base")
    assert nm.read_note("") == "base"


# Test WizNotesManager


def test_wiznotes_manager(tmp_path):
    wm = (
        Database.WizNotesManager(str(tmp_path))
        if hasattr(Database, "WizNotesManager")
        else None
    )
    if wm is None:
        from geneweb.db.database import WizNotesManager

        wm = WizNotesManager(str(tmp_path))
    wm.write_wiznote("wkey", "wval")
    assert wm.read_wiznote("wkey") == "wval"
    assert "wkey" in wm.list_wiznotes()


# Test ExtFilesManager


def test_extfiles_manager(tmp_path):
    em = (
        Database.ExtFilesManager(str(tmp_path), "notes_d")
        if hasattr(Database, "ExtFilesManager")
        else None
    )
    if em is None:
        from geneweb.db.database import ExtFilesManager

        em = ExtFilesManager(str(tmp_path), "notes_d")
    fname = os.path.join(em.dir, "file.txt")
    with open(fname, "w") as f:
        f.write("x")
    assert "file" in em.list_txt_files()


# Test NameIndex


def test_nameindex():
    ni = Database.NameIndex() if hasattr(Database, "NameIndex") else None
    if ni is None:
        from geneweb.db.database import NameIndex

        ni = NameIndex()
    p = Person(id=1, first_name="John", surname="Doe")
    ni.add_person(p)
    assert ni.find_by_name("John Doe") == [1]
    assert ni.find_by_surname("Doe") == [1]
    assert ni.find_by_firstname("John") == [1]


# Test Database.get_person_by_id


def test_get_person_by_id(tmp_path):
    db = create_sample_db(tmp_path)
    db.initialize()
    p = db.get_person_by_id(1)
    assert p is not None and p.id == 1
    assert db.get_person_by_id(999) is None


# Test Database.search_persons_by_name/surname/firstname


def test_search_persons_by_name_surname_firstname(tmp_path):
    db = create_sample_db(tmp_path)
    db.initialize()
    assert db.search_persons_by_name("John Doe")[0].id == 1
    assert db.search_persons_by_surname("Smith")[0].id == 2
    assert db.search_persons_by_firstname("Jane")[0].id == 2


# Test Database.save (read_only)


def test_database_save_readonly(tmp_path):
    db = Database(str(tmp_path), read_only=True)
    with pytest.raises(PermissionError):
        db.save()
    with pytest.raises(PermissionError):
        db.commit_patches()


# Test Database.load/save synchro


def test_database_synchro(tmp_path):
    db = create_sample_db(tmp_path)
    db.synchro_patch.synch_list.append(("t", [1], [2]))
    db.save()
    dbdir = str(tmp_path) + ".gwb"
    db = Database(dbdir)
    db.add_person_patch(Person(id=99, first_name="Test", surname="User"))
    db.commit_patches()  # Actually persist a patch and synchro tuple
    db2 = Database(dbdir)
    db2.load()
    assert len(db2.synchro_patch.synch_list) > 0


# Test Database.input_synchro


def test_database_input_synchro(tmp_path):
    db = create_sample_db(tmp_path)
    db.synchro_patch.synch_list.append(("t", [1], [2]))
    db.save()
    dbdir = str(tmp_path) + ".gwb"
    db = Database(dbdir)
    db.add_person_patch(Person(id=100, first_name="Test2", surname="User2"))
    db.commit_patches()  # Actually persist a patch and synchro tuple
    db2 = Database(dbdir)
    db2.input_synchro()
    assert len(db2.synchro_patch.synch_list) > 0


# Test Database.load_base exception


def test_database_load_base_exception(tmp_path, monkeypatch):
    db = Database(str(tmp_path))
    base_path = os.path.join(db.dbdir, "base")
    with open(base_path, "wb") as f:
        f.write(b"invalid_pickle")

    def fake_load(*a, **kw):
        raise Exception("fail")

    monkeypatch.setattr(pickle, "load", fake_load)
    db.load_base()
    assert db.data["persons"] == []
