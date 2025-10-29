import os

from geneweb.db import outbase
from geneweb.db.outbase import (
    output_notes,
    output_notes_d,
    output_particles_file,
    safe_rename,
)


def test_safe_rename(tmp_path):
    src = os.path.join(tmp_path, "src.txt")
    dst = os.path.join(tmp_path, "dst.txt")
    with open(src, "w") as f:
        f.write("hello")
    safe_rename(src, dst)
    assert os.path.exists(dst)
    with open(dst) as f:
        assert f.read() == "hello"


def test_output_particles_file(tmp_path):
    fname = os.path.join(tmp_path, "particles.txt")
    particles = ["Jean Pierre", "O Neil"]
    output_particles_file(particles, fname)
    with open(fname) as f:
        lines = f.read().splitlines()
    assert lines == ["Jean_Pierre", "O_Neil"]


def test_output_notes(tmp_path):
    class DummyBnotes:
        def nread(self, a, b):
            return "note content"

    class DummyBase:
        data = type("Data", (), {})()
        data.bnotes = DummyBnotes()

    fname = os.path.join(tmp_path, "notes.txt")
    output_notes(DummyBase(), fname)
    with open(fname) as f:
        assert f.read() == "note content"


def test_output_notes_d(tmp_path):
    class DummyBnotes:
        def efiles(self):
            return ["page1", "page2"]

        def nread(self, a, b):
            return f"content_{a}"

    class DummyBase:
        data = type("Data", (), {})()
        data.bnotes = DummyBnotes()

    dst_dir = os.path.join(tmp_path, "notes_d")
    output_notes_d(DummyBase(), dst_dir)
    for page in ["page1", "page2"]:
        fname = os.path.join(dst_dir, page + ".txt")
        assert os.path.exists(fname)
        with open(fname) as f:
            assert f.read() == f"content_{page}"


# Test de la fonction trace avec verbose True
def test_trace_verbose(capsys):
    outbase.verbose = True
    outbase.trace("test message")
    outbase.verbose = False
    captured = capsys.readouterr()
    assert "*** test message" in captured.out


# Test de la fonction trace avec verbose False
def test_trace_not_verbose(capsys):
    outbase.verbose = False
    outbase.trace("should not print")
    captured = capsys.readouterr()
    assert captured.out == ""


# Test safe_rename quand dst existe
def test_safe_rename_removes_existing(tmp_path):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("src")
    dst.write_text("dst")
    outbase.safe_rename(str(src), str(dst))
    assert dst.read_text() == "src"
    assert not src.exists()


# Test safe_rename fallback sur exception
def test_safe_rename_fallback(monkeypatch, tmp_path):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("src")

    def fail_rename(s, d):
        raise OSError()

    monkeypatch.setattr(os, "rename", fail_rename)
    outbase.safe_rename(str(src), str(dst))
    assert dst.read_text() == "src"
    assert not src.exists()


# Test output avec nettoyage de fichiers obsolètes et création de tous les fichiers
class DummyArray:
    def __init__(self, items):
        self.items = items
        self.len = len(items)

    def __iter__(self):
        return iter(self.items)


class DummyBnotes:
    def nread(self, a, b):
        if a == "page1":
            return "content_page1"
        return "note content"

    def efiles(self):
        return ["page1"]


class DummyData:
    def __init__(self, tmpdir):
        self.persons = DummyArray(["p1", "p2"])
        self.families = DummyArray(["f1"])
        self.strings = DummyArray(["s1"])
        self.bnotes = DummyBnotes()
        self.particles_txt = ["Jean Pierre"]
        self.bdir = os.path.join(tmpdir, "db")


class DummyBase:
    def __init__(self, tmpdir):
        self.data = DummyData(tmpdir)


def test_output_creates_files_and_cleans(tmp_path):
    base = DummyBase(tmp_path)
    bdir = base.data.bdir
    os.makedirs(bdir, exist_ok=True)
    # Crée des fichiers/dirs obsolètes
    for fname in [
        "patches",
        "patches~",
        "synchro_patches",
        "notes_link",
        "restrict",
        "tstab_visitor",
        "nb_persons",
        "tstab",
    ]:
        fpath = os.path.join(bdir, fname)
        if "patches" in fname:
            os.makedirs(fpath, exist_ok=True)
        else:
            with open(fpath, "w") as f:
                f.write("old")
    outbase.output(base)
    # Tous les fichiers/dirs obsolètes doivent être supprimés
    for fname in [
        "patches",
        "patches~",
        "synchro_patches",
        "notes_link",
        "restrict",
        "tstab_visitor",
        "nb_persons",
        "tstab",
    ]:
        assert not os.path.exists(os.path.join(bdir, fname))
    # Vérifie la création des fichiers principaux
    for fname in [
        "base.bin",
        "base.acc.bin",
        "names.inx.bin",
        "names.acc.bin",
        "strings.inx.bin",
        "particles.txt",
        "notes.txt",
    ]:
        assert os.path.exists(os.path.join(bdir, fname))
    # Vérifie le contenu des particles
    with open(os.path.join(bdir, "particles.txt")) as f:
        assert f.read().strip() == "Jean_Pierre"
    # Vérifie le contenu des notes
    with open(os.path.join(bdir, "notes.txt")) as f:
        assert f.read() == "note content"
    # Vérifie le contenu des notes_d
    notes_d_file = os.path.join(bdir, "notes_d", "page1.txt")
    assert os.path.exists(notes_d_file)
    with open(notes_d_file) as f:
        assert f.read() == "content_page1"


# Test output_notes_d remplace notes_d existant


def test_output_notes_d_existing_notes_d_full(tmp_path):
    base = DummyBase(tmp_path)
    bdir = base.data.bdir
    notes_d = os.path.join(bdir, "notes_d")
    os.makedirs(notes_d, exist_ok=True)
    with open(os.path.join(notes_d, "old.txt"), "w") as f:
        f.write("old")
    outbase.output(base)
    # L'ancien notes_d doit être remplacé
    assert os.path.exists(os.path.join(bdir, "notes_d", "page1.txt"))
    assert not os.path.exists(os.path.join(bdir, "notes_d", "old.txt"))
