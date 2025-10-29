from typing import Any, List, Tuple

# Constantes équivalentes
DUMMY_IFAM = -1
EMPTY_STRING = 0
QUEST_STRING = 1


# Fonction pour détecter une personne vide (à adapter selon le modèle Python)
def empty_person(p: Any) -> bool:
    return (
        p.first_name in [EMPTY_STRING, QUEST_STRING]
        and p.surname in [EMPTY_STRING, QUEST_STRING]
        and p.image == EMPTY_STRING
        and p.first_names_aliases == []
        and p.surnames_aliases == []
        and p.public_name == EMPTY_STRING
        and p.qualifiers == []
        and p.titles == []
        and p.rparents == []
        and p.related == []
        and p.aliases == []
        and p.occupation == EMPTY_STRING
        and getattr(p, "sex", None) == "Neuter"
        and getattr(p, "birth", None) == "Date_None"
        and p.birth_place == EMPTY_STRING
        and p.birth_note == EMPTY_STRING
        and p.birth_src == EMPTY_STRING
        and getattr(p, "baptism", None) == "Date_None"
        and p.baptism_place == EMPTY_STRING
        and p.baptism_note == EMPTY_STRING
        and p.baptism_src == EMPTY_STRING
        and getattr(p, "death", None) == "DontKnowIfDead"
        and p.death_place == EMPTY_STRING
        and p.death_note == EMPTY_STRING
        and p.death_src == EMPTY_STRING
        and getattr(p, "burial", None) == "UnknownBurial"
        and p.burial_place == EMPTY_STRING
        and p.burial_note == EMPTY_STRING
        and p.burial_src == EMPTY_STRING
        and p.pevents == []
        and p.notes == EMPTY_STRING
        and p.psources == EMPTY_STRING
    )


def gc(base: Any, dry_run: bool = True) -> Tuple[List[int], List[int], List[int]]:
    """
    Garbage collector sur la base GeneWeb :
    - Marque les éléments référencés (personnes, familles, chaînes)
    - Si dry_run, retourne les indices des éléments non référencés
    - Sinon, compacte la base en supprimant les éléments non référencés
    """
    # Chargement des tableaux (à adapter selon l'API Python)
    base.data.persons.load_array()
    base.data.ascends.load_array()
    base.data.unions.load_array()
    base.data.families.load_array()
    base.data.couples.load_array()
    base.data.descends.load_array()
    base.data.strings.load_array()

    mp = [False] * base.data.persons.len
    mf = [False] * base.data.families.len
    ms = [False] * base.data.strings.len

    def markp(i):
        mp[i] = True

    def markf(i):
        mf[i] = True

    def marks(i):
        ms[i] = True

    if base.data.strings.len > 0:
        marks(0)
    if base.data.strings.len > 1:
        marks(1)

    # Marquage des personnes non vides
    for i in range(base.data.persons.len):
        p = base.data.persons.get(i)
        if not empty_person(p):
            markp(i)
            # map_person_ps, map_union_f, map_ascend_f à adapter selon le modèle Python
            # Futil.map_person_ps(markp, marks, p)
            # Futil.map_union_f(markf, base.data.unions.get(i))
            # Futil.map_ascend_f(markf, base.data.ascends.get(i))
            pass

    # Marquage des familles
    for i in range(base.data.families.len):
        if mf[i]:
            f = base.data.families.get(i)
            if getattr(f, "fam_index", None) != DUMMY_IFAM:
                # Futil.map_family_ps(markp, markf, marks, f)
                # Futil.map_couple_p(False, markp, base.data.couples.get(i))
                # Futil.map_descend_p(markp, base.data.descends.get(i))
                pass

    # Calcul des indices supprimés
    def aux(arr):
        sum_ = 0
        acc = []
        for i in reversed(range(len(arr))):
            if arr[i]:
                sum_ += 1
            else:
                acc.append(i)
        return sum_, acc

    lenp, deletedp = aux(mp)
    lenf, deletedf = aux(mf)
    lens, deleteds = aux(ms)

    if dry_run:
        return deletedp, deletedf, deleteds
    else:
        # Compactage mémoire : à adapter selon le modèle Python
        # Recréer les tableaux en ne gardant que les éléments marqués
        # Mettre à jour la base sur disque si besoin
        # ...
        return deletedp, deletedf, deleteds
