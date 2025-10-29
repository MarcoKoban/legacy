from geneweb.db.collection import Collection, Marker


def test_make_and_get():
    c = Collection.make(3, lambda i: i if i < 3 else None)
    assert c.length_() == 3
    assert c.get(0) == 0
    assert c.get(2) == 2
    assert c.get(3) is None


def test_empty():
    c = Collection.empty()
    assert c.length_() == -1
    assert c.get(0) is None


def test_map():
    c = Collection.make(3, lambda i: i)
    c2 = c.map(lambda x: x * 2)
    assert c2.get(0) == 0
    assert c2.get(1) == 2
    assert c2.get(2) == 4


def test_iter():
    c = Collection.make(3, lambda i: i)
    result = []
    c.iter(lambda x: result.append(x))
    assert result == [0, 1, 2]


def test_iteri():
    c = Collection.make(3, lambda i: i)
    result = []
    c.iteri(lambda i, x: result.append((i, x)))
    assert result == [(0, 0), (1, 1), (2, 2)]


def test_fold():
    c = Collection.make(4, lambda i: i)
    total = c.fold(lambda acc, x: acc + x, 0)
    assert total == 6
    # Test from/until
    total2 = c.fold(lambda acc, x: acc + x, 0, from_=1, until=2)
    assert total2 == 3


def test_fold_until():
    c = Collection.make(5, lambda i: i)

    def continue_fn(acc):
        return acc < 6

    total = c.fold_until(continue_fn, lambda acc, x: acc + x, 0)
    # Should stop when acc >= 6
    assert total >= 6


def test_iterator():
    c = Collection.make(3, lambda i: i)
    it = c.iterator()
    values = [it(), it(), it(), it()]
    assert values == [0, 1, 2, None]


def test_marker_make_and_get_set():
    c = Collection.make(3, lambda i: i)
    marker = Marker.make(lambda x: x, c, 0)
    assert marker.get(1) == 0
    marker.set(1, 42)
    assert marker.get(1) == 42


def test_marker_dummy():
    marker = Marker.dummy(0, 99)
    assert marker.get(123) == 99
    marker.set(123, 88)  # Should do nothing
    assert marker.get(123) == 99
