import os
import shutil

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUTOBOX_DIR = os.path.join(os.path.dirname(BASE_DIR), "AutoBox")

FOLDER_ALIASES = {
    "ab1": "AB1",
    "a1": "AB1",
    "av1": "AB1",

    "ab2": "AB2",
    "a2": "AB2",
    "av2": "AB2",

    "ab3": "AB3",
    "a3": "AB3",
    "av3": "AB3",
}


def normalize_folder(name):
    if not name:
        return None
    return FOLDER_ALIASES.get(name.lower().replace(" ", ""), name.upper())


def create_file(path):
    if "/" in path:
        full_path = os.path.join(AUTOBOX_DIR, path)
    else:
        full_path = os.path.join(BASE_DIR, path)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    open(full_path, "a", encoding="utf-8").close()


def write_file(path, content):
    if "/" in path:
        full_path = os.path.join(AUTOBOX_DIR, path)
    else:
        full_path = os.path.join(BASE_DIR, path)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content or "")


def read_file(path):
    if "/" in path:
        full_path = os.path.join(AUTOBOX_DIR, path)
    else:
        full_path = os.path.join(BASE_DIR, path)

    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def move_file(source, destination):
    destination = normalize_folder(destination)

    # CASE 1: source already includes folder (e.g., AB2/House.py)
    if "/" in source:
        src_path = os.path.join(AUTOBOX_DIR, source)
    else:
        # CASE 2: search AutoBox for the file
        src_path = None
        for folder in ["AB1", "AB2", "AB3"]:
            candidate = os.path.join(AUTOBOX_DIR, folder, source)
            if os.path.exists(candidate):
                src_path = candidate
                break

        # fallback to BASE_DIR
        if not src_path:
            candidate = os.path.join(BASE_DIR, source)
            if os.path.exists(candidate):
                src_path = candidate

    if not src_path or not os.path.exists(src_path):
        raise FileNotFoundError(f"File not found: {source}")

    dst_dir = os.path.join(AUTOBOX_DIR, destination)
    os.makedirs(dst_dir, exist_ok=True)

    shutil.move(src_path, os.path.join(dst_dir, os.path.basename(src_path)))
