import pytest

from geneweb.db.avl import AVLMap


def cmp_int(x, y):
    return (x > y) - (x < y)


def test_add_and_find():
    avl = AVLMap(compare=cmp_int)
    avl.add(10, "a")
    avl.add(5, "b")
    avl.add(15, "c")
    assert avl.find(10) == "a"
    assert avl.find(5) == "b"
    assert avl.find(15) == "c"


def test_update_value():
    avl = AVLMap(compare=cmp_int)
    avl.add(1, "x")
    avl.add(1, "y")
    assert avl.find(1) == "y"


def test_mem():
    avl = AVLMap(compare=cmp_int)
    avl.add(2, "foo")
    assert avl.mem(2)
    assert not avl.mem(3)


def test_find_key_error():
    avl = AVLMap(compare=cmp_int)
    avl.add(1, "a")
    with pytest.raises(KeyError):
        avl.find(99)


def test_key_after():
    avl = AVLMap(compare=cmp_int)
    for k in [10, 20, 30]:
        avl.add(k, str(k))
    # Cherche la clé juste supérieure à 15
    key = avl.key_after(lambda x: cmp_int(15, x))
    assert key == 20
    # Cherche la clé égale à 20
    key = avl.key_after(lambda x: cmp_int(20, x))
    assert key == 20
    # Cherche la clé la plus petite
    key = avl.key_after(lambda x: cmp_int(5, x))
    assert key == 10
    # Erreur si aucune clé
    empty_avl = AVLMap(compare=cmp_int)
    with pytest.raises(KeyError):
        empty_avl.key_after(lambda x: cmp_int(1, x))


def test_next():
    avl = AVLMap(compare=cmp_int)
    for k in [10, 20, 30]:
        avl.add(k, str(k))
    assert avl.next(10) == 20
    assert avl.next(20) == 30
    with pytest.raises(KeyError):
        avl.next(30)


def test_empty_avlmap_find_mem():
    avl = AVLMap(compare=cmp_int)
    assert not avl.mem(1)
    with pytest.raises(KeyError):
        avl.find(1)


# Test de la rotation gauche/droite et balance
# On force la structure pour tester les méthodes internes


def test_rotate_left_and_right_and_balance():
    avl = AVLMap(compare=cmp_int)
    # Ajoute dans l'ordre pour forcer un déséquilibre
    avl.add(3, "a")
    avl.add(2, "b")
    avl.add(1, "c")
    # Après rotations, l'arbre doit être équilibré
    assert avl.root.height == 2
    # Ajoute dans l'autre sens pour forcer rotation gauche
    avl2 = AVLMap(compare=cmp_int)
    avl2.add(1, "x")
    avl2.add(2, "y")
    avl2.add(3, "z")
    assert avl2.root.height == 2


# Test next sur clé absente


def test_next_keyerror():
    avl = AVLMap(compare=cmp_int)
    avl.add(1, "a")
    with pytest.raises(KeyError):
        avl.next(99)


# Test key_after sur arbre vide


def test_key_after_empty():
    avl = AVLMap(compare=cmp_int)
    with pytest.raises(KeyError):
        avl.key_after(lambda x: cmp_int(1, x))


# Test add avec différents types de clés


def test_add_various_types():
    avl = AVLMap(compare=lambda x, y: (str(x) > str(y)) - (str(x) < str(y)))
    avl.add("a", 1)
    avl.add("b", 2)
    avl.add("c", 3)
    assert avl.find("b") == 2
    assert avl.mem("c")
