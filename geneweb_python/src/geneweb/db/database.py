# database.py
"""
GeneWeb database management (Python version)
Inspired by OCaml database.ml
"""
import glob
import os
import pickle
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class VisibleState:
    NONE = 0
    TRUE = 1
    FALSE = 2


class SynchroPatch:
    def __init__(self):
        self.synch_list: List[tuple[str, List[int], List[int]]] = []


@dataclass
class Person:
    id: int
    first_name: str
    surname: str
    occ: int = 0
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    birth_place: Optional[str] = None
    death_place: Optional[str] = None
    gender: Optional[str] = None
    parents: List[int] = field(default_factory=list)
    unions: List[int] = field(default_factory=list)
    notes: Optional[str] = None
    restrict: Optional[int] = None
    aliases: List[str] = field(default_factory=list)
    titles: List[str] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    profession: Optional[str] = None
    images: List[str] = field(default_factory=list)
    # Ajoute d'autres champs selon besoin


@dataclass
class Family:
    id: int
    members: List[int] = field(default_factory=list)
    parents: List[int] = field(default_factory=list)
    children: List[int] = field(default_factory=list)
    notes: Optional[str] = None
    events: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    type: Optional[str] = None
    # Ajoute d'autres champs selon besoin


@dataclass
class Union:
    id: int
    partners: List[int] = field(default_factory=list)
    marriage_date: Optional[str] = None
    marriage_place: Optional[str] = None
    divorce_date: Optional[str] = None
    divorce_place: Optional[str] = None
    children: List[int] = field(default_factory=list)
    notes: Optional[str] = None
    witnesses: List[str] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    type: Optional[str] = None
    # Ajoute d'autres champs selon besoin


@dataclass
class Couple:
    id: int
    spouse1: int
    spouse2: int
    marriage_date: Optional[str] = None
    marriage_place: Optional[str] = None
    divorce_date: Optional[str] = None
    divorce_place: Optional[str] = None
    children: List[int] = field(default_factory=list)
    notes: Optional[str] = None
    witnesses: List[str] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    # Ajoute d'autres champs selon besoin


@dataclass
class Descend:
    id: int
    children: List[int] = field(default_factory=list)
    parent: Optional[int] = None
    notes: Optional[str] = None
    events: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    type: Optional[str] = None
    # Ajoute d'autres champs selon besoin


class NameIndex:
    """Index pour la recherche rapide par nom/prénom."""

    def __init__(self):
        self.name_to_persons: Dict[str, List[int]] = {}
        self.surname_to_persons: Dict[str, List[int]] = {}
        self.firstname_to_persons: Dict[str, List[int]] = {}

    def add_person(self, person: Person):
        key = f"{person.first_name} {person.surname}"
        self.name_to_persons.setdefault(key.lower(), []).append(person.id)
        self.surname_to_persons.setdefault(person.surname.lower(), []).append(person.id)
        self.firstname_to_persons.setdefault(person.first_name.lower(), []).append(
            person.id
        )

    def find_by_name(self, name: str) -> List[int]:
        return self.name_to_persons.get(name.lower(), [])

    def find_by_surname(self, surname: str) -> List[int]:
        return self.surname_to_persons.get(surname.lower(), [])

    def find_by_firstname(self, firstname: str) -> List[int]:
        return self.firstname_to_persons.get(firstname.lower(), [])


class PatchManager:
    """Gestion des patchs pour les modifications non validées."""

    def __init__(self):
        self.person_patches: Dict[int, Person] = {}
        self.family_patches: Dict[int, Family] = {}
        self.union_patches: Dict[int, Union] = {}
        self.couple_patches: Dict[int, Couple] = {}
        self.descend_patches: Dict[int, Descend] = {}
        self.string_patches: Dict[int, str] = {}
        self.name_patches: Dict[int, List[int]] = {}

    def add_person_patch(self, person: Person):
        self.person_patches[person.id] = person

    def apply_patches(self, persons: List[Person]) -> List[Person]:
        # Remplace ou ajoute les personnes patchées
        patched = {p.id: p for p in persons}
        patched.update(self.person_patches)
        return list(patched.values())


class VisibilityManager:
    """Gestion de la visibilité des personnes dans la base."""

    def __init__(self, persons_len: int):
        self.visible: List[int] = [VisibleState.NONE] * persons_len

    def set_visible(self, idx: int, state: int):
        if 0 <= idx < len(self.visible):
            self.visible[idx] = state

    def get_visible(self, idx: int) -> int:
        if 0 <= idx < len(self.visible):
            return self.visible[idx]
        return VisibleState.NONE

    def save(self, dbdir: str):
        restrict_path = os.path.join(dbdir, "restrict")
        with open(restrict_path, "wb") as f:
            pickle.dump(self.visible, f)

    def load(self, dbdir: str):
        restrict_path = os.path.join(dbdir, "restrict")
        if os.path.exists(restrict_path):
            with open(restrict_path, "rb") as f:
                self.visible = pickle.load(f)


class NotesManager:
    """Gestion des notes de la base et des pages étendues."""

    def __init__(self, dbdir: str):
        self.dbdir = dbdir
        self.notes: Dict[str, str] = {}
        self.notes_dir = os.path.join(dbdir, "notes_d")
        os.makedirs(self.notes_dir, exist_ok=True)

    def read_note(self, key: str) -> str:
        if key == "":
            path = os.path.join(self.dbdir, "notes")
        else:
            path = os.path.join(self.notes_dir, f"{key}.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def write_note(self, key: str, content: str):
        if key == "":
            path = os.path.join(self.dbdir, "notes")
        else:
            path = os.path.join(self.notes_dir, f"{key}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


class WizNotesManager:
    """Gestion des notes 'wiznotes' (pages étendues)."""

    def __init__(self, dbdir: str):
        self.wiznotes_dir = os.path.join(dbdir, "wiznotes")
        os.makedirs(self.wiznotes_dir, exist_ok=True)

    def read_wiznote(self, key: str) -> str:
        path = os.path.join(self.wiznotes_dir, f"{key}.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def write_wiznote(self, key: str, content: str):
        path = os.path.join(self.wiznotes_dir, f"{key}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def list_wiznotes(self) -> List[str]:
        return [
            os.path.splitext(os.path.basename(f))[0]
            for f in glob.glob(os.path.join(self.wiznotes_dir, "*.txt"))
        ]


class ExtFilesManager:
    """Gestion des fichiers étendus (ex: notes_d, nodes_d, etc.)."""

    def __init__(self, dbdir: str, subdir: str):
        self.dir = os.path.join(dbdir, subdir)
        os.makedirs(self.dir, exist_ok=True)

    def list_txt_files(self) -> List[str]:
        return [
            os.path.splitext(os.path.basename(f))[0]
            for f in glob.glob(os.path.join(self.dir, "*.txt"))
        ]


class Database:
    def __init__(self, dbdir: str, read_only: bool = False):
        self.dbdir = dbdir if dbdir.endswith(".gwb") else dbdir + ".gwb"
        self.read_only = read_only
        self.data: Dict[str, Any] = {}
        self.patches: Dict[str, Any] = {}
        self.synchro_patch = SynchroPatch()
        self.visible: Optional[List[int]] = None
        self.patch_manager = PatchManager()
        self.visibility_manager = None
        self.notes_manager = NotesManager(self.dbdir)
        self.wiznotes_manager = WizNotesManager(self.dbdir)
        self.ext_files_manager = ExtFilesManager(self.dbdir, "notes_d")
        # Initialize families storage
        if "families" not in self.data:
            self.data["families"] = {}

    def load(self):
        """Load database files (simplified, extend as needed)"""
        base_path = os.path.join(self.dbdir, "base")
        if os.path.exists(base_path):
            with open(base_path, "rb") as f:
                self.data["base"] = pickle.load(f)
        # Load other files as needed
        synchro_path = os.path.join(self.dbdir, "synchro_patches")
        if os.path.exists(synchro_path):
            with open(synchro_path, "rb") as f:
                self.synchro_patch.synch_list = pickle.load(f)

    def save(self):
        """Save database files (simplified, extend as needed)"""
        if self.read_only:
            raise PermissionError("Database is read-only")
        base_path = os.path.join(self.dbdir, "base")
        with open(base_path, "wb") as f:
            pickle.dump(self.data.get("base", {}), f)
        # Save other files as needed
        synchro_path = os.path.join(self.dbdir, "synchro_patches")
        with open(synchro_path, "wb") as f:
            pickle.dump(self.synchro_patch.synch_list, f)

    def move_with_backup(self, src: str, dst: str):
        """Move file with backup (like OCaml move_with_backup)"""
        if os.path.exists(dst + "~"):
            os.remove(dst + "~")
        if os.path.exists(dst):
            os.rename(dst, dst + "~")
        if os.path.exists(src):
            os.rename(src, dst)

    def add_person_patch(self, person: Person):
        self.patch_manager.add_person_patch(person)

    def commit_patches(self):
        """Valide les patchs et les applique à la base."""
        if self.read_only:
            raise PermissionError("Database is read-only")
        # Applique les patchs sur toutes les entités
        self.data["persons"] = self.patch_manager.apply_patches(
            self.data.get("persons", [])
        )
        self.data["families"] = self.patch_manager.apply_patches(
            self.data.get("families", [])
        )
        self.data["unions"] = self.patch_manager.apply_patches(
            self.data.get("unions", [])
        )
        self.data["couples"] = self.patch_manager.apply_patches(
            self.data.get("couples", [])
        )
        self.data["descends"] = self.patch_manager.apply_patches(
            self.data.get("descends", [])
        )
        self.patch_manager = PatchManager()
        self.save_base()
        # Ajoute une entrée de synchro
        import time

        timestamp = str(int(time.time()))
        self.synchro_patch.synch_list.append(
            (timestamp, [p.id for p in self.data["persons"]], [])
        )
        self.save()

    def input_synchro(self):
        """Load synchro_patches file"""
        synchro_path = os.path.join(self.dbdir, "synchro_patches")
        if os.path.exists(synchro_path):
            with open(synchro_path, "rb") as f:
                self.synchro_patch.synch_list = pickle.load(f)
        else:
            self.synchro_patch = SynchroPatch()

    def init_visibility(self):
        persons_len = len(self.data.get("persons", []))
        self.visibility_manager = VisibilityManager(persons_len)
        try:
            self.visibility_manager.load(self.dbdir)
        except Exception as e:
            print(f"Erreur lors du chargement de la visibilité: {e}")

    def set_person_visible(self, idx: int, state: int):
        if self.visibility_manager:
            self.visibility_manager.set_visible(idx, state)
            self.visibility_manager.save(self.dbdir)

    def get_person_visible(self, idx: int) -> int:
        if self.visibility_manager:
            return self.visibility_manager.get_visible(idx)
        return VisibleState.NONE

    def read_note(self, key: str) -> str:
        return self.notes_manager.read_note(key)

    def write_note(self, key: str, content: str):
        self.notes_manager.write_note(key, content)

    def read_wiznote(self, key: str) -> str:
        return self.wiznotes_manager.read_wiznote(key)

    def write_wiznote(self, key: str, content: str):
        self.wiznotes_manager.write_wiznote(key, content)

    def list_wiznotes(self) -> List[str]:
        return self.wiznotes_manager.list_wiznotes()

    def list_ext_files(self) -> List[str]:
        return self.ext_files_manager.list_txt_files()

    def load_base(self):
        """Load the main base file and parse persons/families/etc."""
        base_path = os.path.join(self.dbdir, "base")
        if os.path.exists(base_path):
            try:
                with open(base_path, "rb") as f:
                    base_data = pickle.load(f)
                    self.data["base"] = base_data
                    self.data["persons"] = [
                        Person(**p) for p in base_data.get("persons", [])
                    ]
                    self.data["families"] = [
                        Family(**f) for f in base_data.get("families", [])
                    ]
                    self.data["unions"] = [
                        Union(**u) for u in base_data.get("unions", [])
                    ]
                    self.data["couples"] = [
                        Couple(**c) for c in base_data.get("couples", [])
                    ]
                    self.data["descends"] = [
                        Descend(**d) for d in base_data.get("descends", [])
                    ]
            except Exception as e:
                print(f"Erreur lors du chargement de la base: {e}")
                self.data["persons"] = []
                self.data["families"] = []
                self.data["unions"] = []
                self.data["couples"] = []
                self.data["descends"] = []
        else:
            self.data["persons"] = []
            self.data["families"] = []
            self.data["unions"] = []
            self.data["couples"] = []
            self.data["descends"] = []

    def save_base(self):
        """Save the main base file."""
        base_path = os.path.join(self.dbdir, "base")
        with open(base_path, "wb") as f:
            pickle.dump(self.data.get("base", {}), f)

    def build_indexes(self):
        """Construit les index à partir des personnes chargées."""
        self.index = NameIndex()
        for person in self.data.get("persons", []):
            self.index.add_person(person)

    def search_persons_by_name(self, name: str) -> List[Person]:
        ids = self.index.find_by_name(name)
        return [p for p in self.data.get("persons", []) if p.id in ids]

    def search_persons_by_surname(self, surname: str) -> List[Person]:
        ids = self.index.find_by_surname(surname)
        return [p for p in self.data.get("persons", []) if p.id in ids]

    def search_persons_by_firstname(self, firstname: str) -> List[Person]:
        ids = self.index.find_by_firstname(firstname)
        return [p for p in self.data.get("persons", []) if p.id in ids]

    def initialize(self):
        """
        Initialise la base :
        - Charge les fichiers principaux
        - Construit les index
        - Initialise la visibilité
        - Prépare les gestionnaires de notes et fichiers annexes
        """
        self.load_base()
        self.build_indexes()
        self.init_visibility()
        # Les notes et wiznotes sont déjà initialisées dans __init__

    def save_all(self):
        """Sauvegarde tous les fichiers importants de la base."""
        self.save_base()
        if self.visibility_manager:
            self.visibility_manager.save(self.dbdir)
        self.save()
        # Les notes et wiznotes sont sauvegardées à chaque modification

    def get_person_by_id(self, person_id: int) -> Optional[Person]:
        """Get a person by their ID."""
        # Si on a un index de personnes, chercher dedans
        persons = self.data.get("persons", [])
        for person in persons:
            if hasattr(person, "id") and person.id == person_id:
                return person
            elif isinstance(person, dict) and person.get("id") == person_id:
                # Convert dict to Person if needed
                return Person(**person)
        return None

    def add_person(self, person: Person) -> int:
        """Add a person to the database and return their ID."""
        if "persons" not in self.data:
            self.data["persons"] = []

        # Générer un nouvel ID si la personne n'en a pas
        if not hasattr(person, "id") or person.id is None:
            # Trouver le plus grand ID existant
            max_id = 0
            for p in self.data["persons"]:
                pid = p.id if hasattr(p, "id") else p.get("id", 0)
                if pid > max_id:
                    max_id = pid
            person.id = max_id + 1

        self.data["persons"].append(person)
        return person.id

    # ===== Family Management Methods =====

    def add_family(self, family) -> str:
        """
        Add a family to the database.

        Args:
            family: Family object from geneweb.core.family

        Returns:
            str: Generated family ID
        """
        from uuid import uuid4

        # Initialize families dict if not exists
        if "families" not in self.data:
            self.data["families"] = {}

        # Generate unique ID
        family_id = str(uuid4())

        # Store family
        self.data["families"][family_id] = family

        return family_id

    def get_family(self, family_id: str):
        """
        Get a family by ID.

        Args:
            family_id: Family ID

        Returns:
            Family object or None if not found
        """
        if "families" not in self.data:
            self.data["families"] = {}

        return self.data["families"].get(family_id)

    def get_all_families(self) -> Dict[str, Any]:
        """
        Get all families.

        Returns:
            Dict mapping family IDs to Family objects
        """
        if "families" not in self.data:
            self.data["families"] = {}

        return self.data["families"]

    def delete_family(self, family_id: str) -> bool:
        """
        Delete a family from the database.

        Args:
            family_id: Family ID to delete

        Returns:
            bool: True if deleted, False if not found
        """
        if "families" not in self.data:
            self.data["families"] = {}

        if family_id in self.data["families"]:
            del self.data["families"][family_id]
            return True
        return False

    def get_person(self, person_id: int):
        """
        Get a person by ID (alias for get_person_by_id).

        Args:
            person_id: Person ID

        Returns:
            Person object or None if not found
        """
        return self.get_person_by_id(person_id)


def create_geneweb_db(
    path: str,
    seed_persons: Optional[List[Dict[str, Any]]] = None,
    overwrite: bool = False,
) -> Database:
    """Helper: create a .gwb db directory at `path`,
    write a minimal base and return an initialized Database.

    - path: path to the db ('.gwb' will be appended if absent)
    - seed_persons: list of dicts matching Person fields to prefill the base
    - overwrite: if True and directory exists, existing files will be overwritten
    """
    db = Database(path)
    # ensure directory exists
    os.makedirs(db.dbdir, exist_ok=True)

    base = {
        "persons": seed_persons or [],
        "families": [],
        "unions": [],
        "couples": [],
        "descends": [],
    }

    base_path = os.path.join(db.dbdir, "base")
    if os.path.exists(base_path) and not overwrite:
        # if base exists and we don't want to overwrite, just load existing DB
        db.load_base()
        db.build_indexes()
        db.init_visibility()
        return db

    # write base and initialize
    db.data["base"] = base
    db.save_base()
    db.load_base()
    db.build_indexes()
    db.init_visibility()
    return db


"""
Documentation rapide :
- Database regroupe toutes les opérations sur la base GeneWeb (lecture, écriture,
    recherche, patchs, visibilité, notes, etc.)
- Les gestionnaires spécialisés (VisibilityManager, NotesManager,
    WizNotesManager, PatchManager, etc.)
    facilitent la modularité et la maintenance.
- Le code est adapté pour Python, avec robustesse et extensibilité.
"""
