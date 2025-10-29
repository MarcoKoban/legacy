from typing import Callable, Generic, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class AVLNode(Generic[K, V]):
    def __init__(
        self,
        key: K,
        value: V,
        left: Optional["AVLNode[K, V]"] = None,
        right: Optional["AVLNode[K, V]"] = None,
    ):
        self.key = key
        self.value = value
        self.left = left
        self.right = right
        self.height = 1


class AVLMap(Generic[K, V]):
    def __init__(self, compare: Callable[[K, K], int]):
        self.root: Optional[AVLNode[K, V]] = None
        self.compare = compare

    def height(self, node: Optional[AVLNode[K, V]]) -> int:
        return node.height if node else 0

    def update_height(self, node: AVLNode[K, V]):
        node.height = max(self.height(node.left), self.height(node.right)) + 1

    def rotate_left(self, node: AVLNode[K, V]) -> AVLNode[K, V]:
        r = node.right
        node.right = r.left
        r.left = node
        self.update_height(node)
        self.update_height(r)
        return r

    def rotate_right(self, node: AVLNode[K, V]) -> AVLNode[K, V]:
        left_child = node.left
        node.left = left_child.right
        left_child.right = node
        self.update_height(node)
        self.update_height(left_child)
        return left_child

    def balance(self, node: AVLNode[K, V]) -> AVLNode[K, V]:
        self.update_height(node)
        if self.height(node.left) > self.height(node.right) + 1:
            if self.height(node.left.left) < self.height(node.left.right):
                node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        if self.height(node.right) > self.height(node.left) + 1:
            if self.height(node.right.right) < self.height(node.right.left):
                node.right = self.rotate_right(node.right)
            return self.rotate_left(node)
        return node

    def add(self, key: K, value: V):
        def _add(node: Optional[AVLNode[K, V]], key: K, value: V) -> AVLNode[K, V]:
            if not node:
                return AVLNode(key, value)
            cmp = self.compare(key, node.key)
            if cmp == 0:
                node.value = value
            elif cmp < 0:
                node.left = _add(node.left, key, value)
                node = self.balance(node)
            else:
                node.right = _add(node.right, key, value)
                node = self.balance(node)
            return node

        self.root = _add(self.root, key, value)

    def find(self, key: K) -> V:
        node = self.root
        while node:
            cmp = self.compare(key, node.key)
            if cmp == 0:
                return node.value
            elif cmp < 0:
                node = node.left
            else:
                node = node.right
        raise KeyError(key)

    def mem(self, key: K) -> bool:
        node = self.root
        while node:
            cmp = self.compare(key, node.key)
            if cmp == 0:
                return True
            elif cmp < 0:
                node = node.left
            else:
                node = node.right
        return False

    def key_after(self, f_compare: Callable[[K], int]) -> K:
        def _key_after(node: Optional[AVLNode[K, V]]) -> Optional[K]:
            if not node:
                return None
            c = f_compare(node.key)
            if c < 0:
                left = _key_after(node.left)
                return left if left is not None else node.key
            elif c > 0:
                return _key_after(node.right)
            else:
                return node.key

        result = _key_after(self.root)
        if result is None:
            raise KeyError("No key found")
        return result

    def next(self, key: K) -> K:
        node = self.root
        succ = None
        while node:
            cmp = self.compare(key, node.key)
            if cmp < 0:
                succ = node.key
                node = node.left
            else:
                node = node.right
        if succ is None:
            raise KeyError("No next key found")
        return succ


# Exemple d'utilisation :
# avl = AVLMap(compare=lambda x, y: (x > y) - (x < y))
# avl.add('a', 1)
# avl.add('b', 2)
# print(avl.find('a'))
# print(avl.mem('b'))
# print(avl.next('a'))
