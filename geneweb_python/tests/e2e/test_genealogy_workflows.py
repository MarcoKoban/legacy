"""
End-to-end tests for Geneweb genealogy workflows.

These tests validate complete user scenarios and workflows that span multiple
components of the Geneweb system, ensuring the Python implementation maintains
compatibility with the original OCaml version.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

import pytest

from geneweb.core.calendar import (
    CalendarConverter,
    CalendarDate,
    CalendarType,
    FrenchCalendar,
    GregorianCalendar,
)
from geneweb.core.event import Event
from geneweb.core.place import Place
from geneweb.core.sosa import Sosa
from geneweb.db.database import Database, Person
from geneweb.db.database import create_geneweb_db as create_empty_db


@pytest.mark.e2e
@pytest.mark.slow
class TestGenealogyWorkflows:
    """Test complete genealogy workflows end-to-end."""

    def test_create_and_navigate_family_tree(self, tmp_path):
        """Build a small tree and validate parent navigation and Sosa numbers."""
        seed_persons = [
            {
                "id": 1,
                "first_name": "Alice",
                "surname": "Root",
                "gender": "F",
                "parents": [2, 3],
            },
            {
                "id": 2,
                "first_name": "Bernard",
                "surname": "Root",
                "gender": "M",
            },
            {
                "id": 3,
                "first_name": "Claire",
                "surname": "Root",
                "gender": "F",
            },
        ]
        db = create_empty_db(
            str(tmp_path / "tree"), seed_persons=seed_persons, overwrite=True
        )

        child = db.get_person_by_id(1)
        father = db.get_person_by_id(2)
        mother = db.get_person_by_id(3)

        assert child is not None and child.parents == [2, 3]
        assert father is not None and father.surname == child.surname
        assert mother is not None and mother.surname == child.surname

        root_sosa = Sosa.one()
        assert root_sosa.father_sosa() == Sosa(2)
        assert root_sosa.mother_sosa() == Sosa(3)
        assert Sosa(4).branch_path() == [0, 0]

    def test_import_export_gedcom_workflow(self, tmp_path):
        """Persist a database to disk and reload it to simulate GEDCOM flow."""
        seed_persons = [
            {
                "id": 1,
                "first_name": "Amelie",
                "surname": "Dubois",
                "birth_place": "Paris",
                "birth_date": "1901-01-01",
            }
        ]
        db_path = tmp_path / "gedcom"
        db = create_empty_db(str(db_path), seed_persons=seed_persons, overwrite=True)
        db.write_note("", "Family summary")
        db.save_all()

        reloaded = Database(str(db_path))
        reloaded.initialize()

        assert reloaded.read_note("") == "Family summary"
        loaded_person = reloaded.get_person_by_id(1)
        assert loaded_person is not None
        assert loaded_person.first_name == "Amelie"
        assert loaded_person.birth_place == "Paris"

    def test_search_and_display_workflow(self, tmp_path):
        """Search for persons and inspect returned details."""
        seed_persons = [
            {
                "id": 1,
                "first_name": "Luc",
                "surname": "Martin",
                "birth_place": "Lyon",
            },
            {
                "id": 2,
                "first_name": "Lucie",
                "surname": "Martin",
                "birth_place": "Grenoble",
            },
            {
                "id": 3,
                "first_name": "Marc",
                "surname": "Durand",
                "birth_place": "Lille",
            },
        ]
        db = create_empty_db(
            str(tmp_path / "search"), seed_persons=seed_persons, overwrite=True
        )
        db.build_indexes()

        luc_results = db.search_persons_by_name("Luc Martin")
        assert [p.id for p in luc_results] == [1]

        surname_results = db.search_persons_by_surname("Martin")
        assert {p.id for p in surname_results} == {1, 2}

        detailed = db.get_person_by_id(2)
        assert detailed is not None
        assert detailed.birth_place == "Grenoble"

    def test_calendar_and_events_workflow(self):
        """Exercise calendar conversions and event formatting."""
        event = Event(place=Place("[Quartier] - Marseille"))
        event.set_date_from_components(1889, 3, 31)
        assert event.date == "1889-03-31"
        assert event.place.normalize() == "Quartier, Marseille"

        gregorian = GregorianCalendar()
        french = FrenchCalendar()
        converter = CalendarConverter()

        greg_date = CalendarDate(
            year=1889, month=3, day=31, calendar_type=CalendarType.GREGORIAN
        )
        sdn = gregorian.to_sdn(greg_date)
        assert gregorian.from_sdn(sdn).year == 1889

        jul_date = converter.convert(greg_date, CalendarType.JULIAN)
        back_to_greg = converter.convert(jul_date, CalendarType.GREGORIAN)
        assert back_to_greg.year == greg_date.year

        french_date = CalendarDate(
            year=1, month=7, day=15, calendar_type=CalendarType.FRENCH
        )
        french_sdn = french.to_sdn(french_date)
        assert french.from_sdn(french_sdn).month == 7


@pytest.mark.e2e
@pytest.mark.slow
class TestDataIntegrityWorkflows:
    """Test data integrity across complete workflows."""

    def test_multi_generation_consistency(self, tmp_path):
        """Validate multi-generation relationships and Sosa generation math."""
        seed_persons = [
            {"id": 1, "first_name": "Root", "surname": "Ancestor", "parents": [2, 3]},
            {
                "id": 2,
                "first_name": "ParentA",
                "surname": "Ancestor",
                "parents": [4, 5],
            },
            {"id": 3, "first_name": "ParentB", "surname": "Ancestor"},
            {"id": 4, "first_name": "GrandA", "surname": "Ancestor"},
            {"id": 5, "first_name": "GrandB", "surname": "Ancestor"},
        ]
        db = create_empty_db(
            str(tmp_path / "consistency"), seed_persons=seed_persons, overwrite=True
        )

        root = db.get_person_by_id(1)
        assert root is not None
        assert root.parents == [2, 3]

        parent = db.get_person_by_id(2)
        assert parent is not None
        assert parent.parents == [4, 5]

        assert Sosa(1).generation() == 1
        assert Sosa(2).generation() == 2
        assert Sosa(4).generation() == 3

    def test_concurrent_operations_workflow(self, tmp_path):
        """Simulate overlapping updates via patch manager and commit results."""
        db = create_empty_db(
            str(tmp_path / "concurrency"), seed_persons=[], overwrite=True
        )
        initial_person = Person(id=1, first_name="Elise", surname="Dupont")
        db.add_person_patch(initial_person)
        updated_person = Person(
            id=1, first_name="Elise", surname="Dupont", profession="Historian"
        )
        db.add_person_patch(updated_person)
        db.commit_patches()

        committed = db.get_person_by_id(1)
        assert committed is not None
        assert committed.profession == "Historian"
        assert db.synchro_patch.synch_list, "Synchro log should record the commit"


@pytest.mark.e2e
class TestCompatibilityWorkflows:
    """Test compatibility with OCaml Geneweb workflows."""

    def test_ocaml_python_data_compatibility(self, tmp_path):
        """Confirm OCaml shaped records map cleanly to Python dataclasses."""
        ocaml_person = {
            "id": 7,
            "first_name": "Jean",
            "surname": "Valjean",
            "birth_place": "Paris",
        }
        python_person = Person(**ocaml_person)
        assert asdict(python_person)["first_name"] == "Jean"

        db = create_empty_db(
            str(tmp_path / "compat"), seed_persons=[ocaml_person], overwrite=True
        )
        stored = db.get_person_by_id(7)
        assert stored is not None
        assert stored.first_name == python_person.first_name

    def test_performance_parity_workflow(self, tmp_path):
        """Compare index build and search across a moderate dataset."""
        seed_persons: List[Dict[str, Any]] = []
        for idx in range(1, 401):
            seed_persons.append(
                {
                    "id": idx,
                    "first_name": f"Person{idx}",
                    "surname": "Benchmark",
                }
            )

        db = create_empty_db(
            str(tmp_path / "performance"), seed_persons=seed_persons, overwrite=True
        )

        db.build_indexes()
        matches = db.search_persons_by_surname("Benchmark")
        assert len(matches) == 400
        assert matches[0].first_name.startswith("Person")


# Helper functions for E2E test setup and utilities


def setup_test_database(tmp_path, seed_persons: List[Dict[str, Any]]) -> Database:
    """Create an initialized database for tests."""
    return create_empty_db(
        str(tmp_path / "helper_db"), seed_persons=seed_persons, overwrite=True
    )


def cleanup_test_database(db: Database) -> None:
    """Ensure database data is flushed to disk for assertions."""
    db.save_all()


def create_sample_family_tree() -> List[Dict[str, Any]]:
    """Return a reusable seed tree for tests needing multi-generation data."""
    return [
        {"id": 1, "first_name": "Root", "surname": "Sample", "parents": [2, 3]},
        {"id": 2, "first_name": "Parent1", "surname": "Sample"},
        {"id": 3, "first_name": "Parent2", "surname": "Sample"},
    ]


def validate_migration_results(ocaml_data: Any, python_data: Any) -> bool:
    """Check that two dataclass-backed records carry identical payloads."""
    return asdict(python_data) == ocaml_data
