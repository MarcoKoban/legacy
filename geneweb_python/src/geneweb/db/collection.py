from typing import Callable, Generic, List, Optional, TypeVar

T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")
V = TypeVar("V")


class Collection(Generic[T]):
    def __init__(self, length: int, get: Callable[[int], Optional[T]]):
        self.length = length
        self.get = get

    @staticmethod
    def make(length: int, get: Callable[[int], Optional[T]]) -> "Collection[T]":
        return Collection(length, get)

    @staticmethod
    def empty() -> "Collection[T]":
        return Collection(-1, lambda _: None)

    def map(self, fn: Callable[[T], U]) -> "Collection[U]":
        def get_mapped(i: int) -> Optional[U]:
            x = self.get(i)
            return fn(x) if x is not None else None

        return Collection(self.length, get_mapped)

    def length_(self) -> int:
        return self.length

    def iter(self, fn: Callable[[T], None]) -> None:
        for i in range(self.length):
            x = self.get(i)
            if x is not None:
                fn(x)

    def iteri(self, fn: Callable[[int, T], None]) -> None:
        for i in range(self.length):
            x = self.get(i)
            if x is not None:
                fn(i, x)

    def fold(
        self,
        fn: Callable[[U, T], U],
        acc: U,
        from_: Optional[int] = None,
        until: Optional[int] = None,
    ) -> U:
        start = from_ if from_ is not None else 0
        end = until + 1 if until is not None else self.length
        for i in range(start, end):
            x = self.get(i)
            if x is not None:
                acc = fn(acc, x)
        return acc

    def fold_until(
        self, continue_fn: Callable[[U], bool], fn: Callable[[U, T], U], acc: U
    ) -> U:
        i = 0
        while continue_fn(acc) and i < self.length:
            x = self.get(i)
            if x is not None:
                acc = fn(acc, x)
            i += 1
        return acc

    def iterator(self) -> Callable[[], Optional[T]]:
        cursor = [0]

        def next_():
            while cursor[0] < self.length:
                x = self.get(cursor[0])
                cursor[0] += 1
                if x is not None:
                    return x
            return None

        return next_


# Alias
collection = Collection


class Marker(Generic[K, V]):
    def __init__(self, get: Callable[[K], V], set: Callable[[K, V], None]):
        self.get = get
        self.set = set

    @staticmethod
    def make(k: Callable[[K], int], c: Collection[K], i: V) -> "Marker[K, V]":
        a: List[V] = [i for _ in range(c.length)]

        def get_marker(x: K) -> V:
            return a[k(x)]

        def set_marker(x: K, v: V) -> None:
            a[k(x)] = v

        return Marker(get_marker, set_marker)

    @staticmethod
    def dummy(_k: K, v: V) -> "Marker[K, V]":
        return Marker(lambda _x: v, lambda _x, _v: None)

    @staticmethod
    def get(marker: "Marker[K, V]", k: K) -> V:
        return marker.get(k)

    @staticmethod
    def set(marker: "Marker[K, V]", k: K, v: V) -> None:
        marker.set(k, v)
