import pickle
from typing import Any, Callable, List

# --- Constantes pour les versions de fichiers GeneWeb ---
magic_GnWb0020 = "GnWb0020"
magic_GnWb0021 = "GnWb0021"
magic_GnWb0022 = "GnWb0022"
magic_GnWb0023 = "GnWb0023"
magic_GnWb0024 = "GnWb0024"

# --- Taille maximale de la table de hachage pour l'indexation des noms ---
table_size = 0x3FFF
int_size = 4  # Taille d'un entier dans les fichiers binaires GeneWeb

# --- Types équivalents ---
NameIndexData = List[List[int]]  # Index pour les mélanges de noms
StringsOfFsname = List[List[int]]  # Index pour les sous-chaînes de noms


# --- Table de hachage pour les clés entières ---
class IntHT(dict):
    def __setitem__(self, key: int, value: Any):
        super().__setitem__(key, value)

    def __getitem__(self, key: int) -> Any:
        return super().__getitem__(key)

    def __contains__(self, key: int) -> bool:
        return super().__contains__(key)

    def get(self, key: int, default=None) -> Any:
        return super().get(key, default)


# --- Fonctions utilitaires pour l'indexation des noms ---
def crush_lower(s: str) -> str:
    """Normalise chaîne pour indexation (comme Name.crush_lower OCaml)."""
    return s.lower().replace("'", "").replace("-", " ").strip()


def name_index(s: str) -> int:
    """Calcule index version normalisée dans tableau table_size."""
    return hash(crush_lower(s)) % table_size


# --- Fonctions de comparaison ---
def compare_fnames(s1: str, s2: str) -> int:
    """Compare deux prénoms lexicographiquement."""
    return (s1 > s2) - (s1 < s2)


def compare_fnames_i(base_data: Any, i1: int, i2: int) -> int:
    """Compare deux prénoms par index dans base_data.strings."""
    if i1 == i2:
        return 0
    return compare_fnames(base_data.data.strings[i1], base_data.data.strings[i2])


def compare_snames(base_data: Any, s1: str, s2: str) -> int:
    """Compare deux noms de famille (remplacer par une logique avancée si besoin)."""
    # Ici, on utilise la comparaison lexicographique, à adapter si besoin
    return (s1 > s2) - (s1 < s2)


def compare_snames_i(base_data: Any, i1: int, i2: int) -> int:
    """Compare deux noms de famille par index dans base_data.strings."""
    if i1 == i2:
        return 0
    return compare_snames(
        base_data, base_data.data.strings[i1], base_data.data.strings[i2]
    )


# --- Accesseurs pour les données de base ---
def poi(base: Any, i: int) -> Any:
    """Retourne la personne d'index i dans base."""
    return base.data.persons[i]


def sou(base: Any, i: int) -> str:
    """Retourne la chaîne d'index i dans base."""
    return base.data.strings[i]


def p_first_name(base: Any, p: Any) -> str:
    """Retourne le prénom de la personne p."""
    return nominative(sou(base, p.first_name))


def p_surname(base: Any, p: Any) -> str:
    """Retourne le nom de famille de la personne p."""
    return nominative(sou(base, p.surname))


def nominative(s: str) -> str:
    """Retourne la forme nominative d'un nom (stub, à adapter si besoin)."""
    return s


# --- Sérialisation sans partage (équivalent Marshal.to_channel No_sharing) ---
def output_value_no_sharing(file_path: str, value: Any):
    """Sérialise value dans un fichier sans partage (pickle, protocole 4)."""
    with open(file_path, "wb") as f:
        pickle.dump(value, f, protocol=4)


# --- Mélange de noms pour une personne (stub, à enrichir selon le modèle) ---
def dsk_person_misc_names(
    base: Any, p: Any, nobtit: Callable[[Any], List[Any]]
) -> List[str]:
    """Calcule les mélanges de noms pour une personne (stub, à enrichir)."""
    # À adapter selon la structure réelle des données
    return [p_first_name(base, p), p_surname(base, p)]


# --- Exemples d'utilisation ---
# int_ht = IntHT()
# int_ht[42] = "exemple"
# print(int_ht[42])

# Ajoutez ici d'autres fonctions utilitaires selon les besoins GeneWeb
