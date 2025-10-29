import os
import pickle
import shutil
from typing import Any

# Flag pour activer la sauvegarde mémoire
save_mem = False
verbose = False


def trace(s: str):
    if verbose:
        print(f"*** {s}")


def safe_rename(src: str, dst: str):
    try:
        if os.path.exists(dst):
            os.remove(dst)
        os.rename(src, dst)
    except Exception:
        shutil.copyfile(src, dst)
        os.remove(src)


def output_particles_file(particles, fname):
    with open(fname, "w", encoding="utf-8") as f:
        for s in particles:
            f.write(s.replace(" ", "_") + "\n")


def output_notes(base, dst):
    content = getattr(base.data.bnotes, "nread", lambda *_: "")("", "RnAll")
    with open(dst, "w", encoding="utf-8") as f:
        f.write(content)


def output_notes_d(base, dst_dir):
    efiles = getattr(base.data.bnotes, "efiles", lambda: [])()
    for f in efiles:
        dst = os.path.join(dst_dir, f + ".txt")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        content = getattr(base.data.bnotes, "nread", lambda *_: "")(f, "RnAll")
        with open(dst, "w", encoding="utf-8") as oc:
            oc.write(content)


# Fonction principale de sauvegarde de la base sur disque
def output(base: Any) -> None:
    """
    Sauvegarde la base GeneWeb sur le disque dans les fichiers binaires et index.
    - base : objet contenant les données et les accès
    """
    bdir = base.data.bdir
    if not os.path.exists(bdir):
        os.makedirs(bdir)
    tmp_particles = os.path.join(bdir, "1particles.txt")
    tmp_base = os.path.join(bdir, "1base.bin")
    tmp_base_acc = os.path.join(bdir, "1base.acc.bin")
    tmp_names_inx = os.path.join(bdir, "1names.inx.bin")
    tmp_names_acc = os.path.join(bdir, "1names.acc.bin")
    tmp_strings_inx = os.path.join(bdir, "1strings.inx.bin")
    tmp_notes = os.path.join(bdir, "1notes.txt")
    tmp_notes_d = os.path.join(bdir, "1notes_d")
    # Sauvegarde des tableaux principaux
    with open(tmp_base, "wb") as f:
        pickle.dump(base.data.persons, f, protocol=4)
        pickle.dump(base.data.families, f, protocol=4)
        pickle.dump(base.data.strings, f, protocol=4)
    with open(tmp_base_acc, "wb") as f:
        pickle.dump(base.data.persons.len, f, protocol=4)
        pickle.dump(base.data.families.len, f, protocol=4)
        pickle.dump(base.data.strings.len, f, protocol=4)
    with open(tmp_names_inx, "wb") as f:
        pickle.dump({}, f, protocol=4)
    with open(tmp_names_acc, "wb") as f:
        pickle.dump({}, f, protocol=4)
    with open(tmp_strings_inx, "wb") as f:
        pickle.dump({}, f, protocol=4)
    output_notes(base, tmp_notes)
    output_notes_d(base, tmp_notes_d)
    output_particles_file(getattr(base.data, "particles_txt", []), tmp_particles)
    # Renommage sécurisé des fichiers temporaires
    safe_rename(tmp_base, os.path.join(bdir, "base.bin"))
    safe_rename(tmp_base_acc, os.path.join(bdir, "base.acc.bin"))
    safe_rename(tmp_names_inx, os.path.join(bdir, "names.inx.bin"))
    safe_rename(tmp_names_acc, os.path.join(bdir, "names.acc.bin"))
    safe_rename(tmp_strings_inx, os.path.join(bdir, "strings.inx.bin"))
    safe_rename(tmp_particles, os.path.join(bdir, "particles.txt"))
    if os.path.exists(tmp_notes):
        safe_rename(tmp_notes, os.path.join(bdir, "notes.txt"))
    if os.path.exists(tmp_notes_d):
        notes_d = os.path.join(bdir, "notes_d")
        if os.path.exists(notes_d):
            shutil.rmtree(notes_d)
        safe_rename(tmp_notes_d, notes_d)
    # Nettoyage des fichiers obsolètes
    for fname in [
        "patches",
        "patches~",
        "synchro_patches",
        "notes_link",
        "restrict",
        "tstab_visitor",
        "nb_persons",
        "tstab",
    ]:
        fpath = os.path.join(bdir, fname)
        if os.path.exists(fpath):
            if os.path.isdir(fpath):
                shutil.rmtree(fpath)
            else:
                os.remove(fpath)
