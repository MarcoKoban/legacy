import io
import pickle

from geneweb.db.iovalue import (
    input,
    output,
    output_array_access,
    sizeof_long,
)


def test_input_output():
    value = {"a": 1, "b": [2, 3]}
    f = io.BytesIO()
    output(f, value)
    f.seek(0)
    loaded = input(f)
    assert loaded == value


def test_output_array_access():
    arr = [10, 20, 30]

    def getf(i):
        return arr[i]

    f = io.BytesIO()
    pos = 0
    end_pos = output_array_access(f, getf, len(arr), pos)
    # On vérifie que les positions et les valeurs sont bien écrites
    f.seek(0)
    # Pour chaque élément, on lit la position (4 octets) puis la valeur picklée
    for i in range(len(arr)):
        pos_bytes = f.read(sizeof_long)
        pos_val = int.from_bytes(pos_bytes, "little")
        assert pos_val == pos + sum(
            len(pickle.dumps(arr[j], protocol=4)) for j in range(i)
        )
        value = pickle.load(f)
        assert value == arr[i]
    assert end_pos == pos + sum(len(pickle.dumps(x, protocol=4)) for x in arr)
