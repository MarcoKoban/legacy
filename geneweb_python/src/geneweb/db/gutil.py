import re
from typing import Any, List, Optional


# Désignation unique d'une personne
def designation(base, p):
    first_name = base.p_first_name(p)
    nom = base.p_surname(p)
    return f"{first_name}.{base.get_occ(p)} {nom}"


# Fonctions de couple/famille
def father(cpl):
    return cpl.father


def mother(cpl):
    return cpl.mother


def couple(multi: bool, fath, moth):
    if not multi:
        return (fath, moth)  # À adapter selon le modèle gen_couple
    else:
        return (fath, moth, "multi")


def parent_array(cpl):
    return [cpl.father, cpl.mother]


def spouse(ip, cpl):
    return cpl.mother if ip == cpl.father else cpl.father


# Recherche par clé


def person_is_key(base, p, k):
    k_norm = k.lower().strip()
    key_str = f"{base.p_first_name(p)} {base.p_surname(p)}".lower().strip()
    if k_norm == key_str:
        return True
    misc_names = base.person_misc_names(p, base.get_titles)
    return any(k_norm == name.lower().strip() for name in misc_names)


def find_num(s: str, i: int) -> Optional[tuple]:
    match = re.search(r"[.](\d+)", s[i:])
    if match:
        occ = int(match.group(1))
        j = i + match.start(1)
        return occ, j
    return None


def split_key(s: str, i: int) -> Optional[tuple]:
    match = re.search(r"(.*?)\.(\d+)\s+(.*)", s[i:])
    if match:
        first_name = match.group(1)
        occ = int(match.group(2))
        surname = match.group(3)
        return i, first_name, occ, surname
    return None


def person_of_string_key(base, s: str) -> Optional[int]:
    res = split_key(s, 0)
    if res:
        _, first_name, occ, surname = res
        return base.person_of_key(first_name, surname, occ)
    return None


def rsplit_key(s: str) -> Optional[tuple]:
    match = re.match(r"(.+?)\.(\d+)\s+(.+)", s)
    if match:
        first_name = match.group(1)
        occ = int(match.group(2))
        surname = match.group(3)
        return first_name, occ, surname
    return None


def person_of_string_dot_key(base, s: str) -> Optional[int]:
    res = rsplit_key(s)
    if res:
        first_name, occ, surname = res
        return base.person_of_key(first_name, surname, occ)
    return None


def person_not_a_key_find_all(base, s: str) -> List[int]:
    ipl = base.persons_of_name(s)
    return [ip for ip in ipl if person_is_key(base, base.poi(ip), s)]


def person_ht_find_all(base, s: str) -> List[int]:
    ip = person_of_string_key(base, s)
    if ip is not None:
        return [ip]
    return person_not_a_key_find_all(base, s)


def find_same_name(base, p) -> List[Any]:
    f = base.p_first_name(p)
    s = base.p_surname(p)
    ipl = person_ht_find_all(base, f + " " + s)
    f_norm = f.lower().strip()
    s_norm = s.lower().strip()
    pl = [
        base.poi(ip)
        for ip in ipl
        if base.p_first_name(base.poi(ip)).lower().strip() == f_norm
        and base.p_surname(base.poi(ip)).lower().strip() == s_norm
    ]
    return sorted(pl, key=lambda p: base.get_occ(p))


def trim_trailing_spaces(s: str) -> str:
    return s.rstrip(" \r\n\t")


# Comparaison alphabétique


def alphabetic_utf_8(n1: str, n2: str) -> int:
    return (n1 > n2) - (n1 < n2)


def alphabetic(n1: str, n2: str) -> int:
    return (n1 > n2) - (n1 < n2)


def alphabetic_order(n1: str, n2: str) -> int:
    return alphabetic_utf_8(n1, n2)


def arg_list_of_string(line: str) -> List[str]:
    return re.findall(r'"([^"]*)"|\'([^\']*)\'|([^\s]+)', line)


# Tri des listes de personnes


def sort_person_list(base, persons: List[Any]) -> List[Any]:
    def person_sort_key(p):
        return (
            getattr(p, "birth", None),
            getattr(p, "death", None),
            base.p_surname(p),
            base.p_first_name(p),
            base.get_occ(p),
            base.get_iper(p),
        )

    return sorted(persons, key=person_sort_key)


def sort_uniq_person_list(base, persons: List[Any]) -> List[Any]:
    seen = set()
    result = []
    for p in sort_person_list(base, persons):
        k = base.get_iper(p)
        if k not in seen:
            seen.add(k)
            result.append(p)
    return result


def find_free_occ(base, f: str, s: str) -> int:
    ipl = base.persons_of_name(f + " " + s)
    first_name = f.lower().strip()
    surname = s.lower().strip()
    occs = set()
    for ip in ipl:
        p = base.poi(ip)
        if (
            p
            and base.p_first_name(p).lower().strip() == first_name
            and base.p_surname(p).lower().strip() == surname
        ):
            occs.add(base.get_occ(p))
    occs = sorted(occs)
    cnt = 0
    for o in occs:
        if cnt == o:
            cnt += 1
        else:
            break
    return cnt


def get_birth_death_date(p) -> tuple:
    birth_date = getattr(p, "birth", None)
    approx = False
    if birth_date is None:
        birth_date = getattr(p, "baptism", None)
        approx = True
    death_date = getattr(p, "death", None)
    if death_date is None:
        burial = getattr(p, "burial", None)
        death_date = getattr(burial, "date", None) if burial else None
        approx = True
    return birth_date, death_date, approx
