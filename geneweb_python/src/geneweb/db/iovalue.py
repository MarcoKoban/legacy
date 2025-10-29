import pickle
import struct
from typing import Any, BinaryIO, Callable

# Taille d'un long dans les fichiers binaires Geneweb
sizeof_long = 4


# Lecture d'une valeur depuis un canal binaire (équivalent Marshal.from_channel)
def input(f: BinaryIO) -> Any:
    return pickle.load(f)


# Écriture d'une valeur dans un canal binaire (équivalent Marshal.to_channel No_sharing)
def output(f: BinaryIO, value: Any) -> None:
    pickle.dump(value, f, protocol=4)


# Écriture d'un tableau en mode binaire, retourne la position après le tableau
def output_array_access(
    f: BinaryIO, getf: Callable[[int], Any], arr_len: int, pos: int
) -> int:
    # On écrit la position de chaque élément, puis les éléments eux-mêmes
    positions = []
    current_pos = pos
    for i in range(arr_len):
        positions.append(current_pos)
        value = getf(i)
        # On estime la taille de la valeur sérialisée
        data = pickle.dumps(value, protocol=4)
        f.write(struct.pack("I", current_pos))
        f.write(data)
        current_pos += len(data)
    return current_pos
