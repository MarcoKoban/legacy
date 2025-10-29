import os

from geneweb.db.outbase import output


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


def test_output_integration(tmp_path):
    base = DummyBase(tmp_path)
    output(base)
    bdir = base.data.bdir
    # Vérifie que les fichiers principaux existent
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
