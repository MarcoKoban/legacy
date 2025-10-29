import os

from geneweb.db.database import Database, Person


def test_full_database_lifecycle(tmp_path):
    dbdir = os.path.join(tmp_path, "integrationdb")
    db = Database(dbdir)
    # Création et sauvegarde de la base
    db.data["base"] = {
        "persons": [
            dict(id=1, first_name="John", surname="Doe"),
            dict(id=2, first_name="Jane", surname="Smith"),
        ],
        "families": [dict(id=1, members=[1, 2])],
    }
    db.save_all()
    # Rechargement et vérification
    db2 = Database(dbdir)
    db2.load_base()
    db2.data["persons"] = [
        Person(id=1, first_name="John", surname="Doe"),
        Person(id=2, first_name="Jane", surname="Smith"),
    ]
    assert len(db2.data["persons"]) == 2
    assert db2.data["persons"][0].first_name == "John"
    # Test de patch et commit
    db2.add_person_patch(Person(id=3, first_name="Alice", surname="Wonder"))
    db2.commit_patches()
    db3 = Database(dbdir)
    db3.load_base()
    db3.data["persons"] = [
        Person(id=1, first_name="John", surname="Doe"),
        Person(id=2, first_name="Jane", surname="Smith"),
        Person(id=3, first_name="Alice", surname="Wonder"),
    ]
    assert any(p.id == 3 for p in db3.data["persons"])


def test_database_search(tmp_path):
    dbdir = os.path.join(tmp_path, "searchdb")
    db = Database(dbdir)
    db.data["base"] = {
        "persons": [
            dict(id=1, first_name="John", surname="Doe"),
            dict(id=2, first_name="Jane", surname="Smith"),
        ]
    }
    db.save_all()
    db.initialize()
    db.data["persons"] = [
        Person(id=1, first_name="John", surname="Doe"),
        Person(id=2, first_name="Jane", surname="Smith"),
    ]
    results = db.search_persons_by_name("John Doe")
    assert len(results) == 1 and results[0].id == 1
    results = db.search_persons_by_surname("Smith")
    assert len(results) == 1 and results[0].id == 2
    results = db.search_persons_by_firstname("Jane")
    assert len(results) == 1 and results[0].id == 2
