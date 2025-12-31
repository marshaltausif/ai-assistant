import json
import os
import difflib

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "state.json")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUTOBOX_DIR = os.path.join(os.path.dirname(BASE_DIR), "AutoBox")


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def update_memory(**kwargs):
    state = load_memory()
    state.update({k: v for k, v in kwargs.items() if v is not None})
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def find_closest_file(name):
    if not name:
        return None

    candidates = []

    # Search base directory
    for root, _, files in os.walk(BASE_DIR):
        for f in files:
            candidates.append(f)

    # Search AutoBox folders
    if os.path.exists(AUTOBOX_DIR):
        for root, _, files in os.walk(AUTOBOX_DIR):
            for f in files:
                candidates.append(f)

    matches = difflib.get_close_matches(name, candidates, n=1, cutoff=0.6)
    return matches[0] if matches else None


def resolve_reference(name):
    state = load_memory()

    if not name:
        return None

    n = name.lower()

    # Memory references
    if n in ["that", "that file", "last", "last file"]:
        return state.get("last_created_file") or state.get("last_touched_file")

    # Folder normalization (voice tolerant)
    if n in ["ab1", "ab2", "ab3", "av1", "av2", "av3"]:
        return n.replace("v", "b")

    # Fuzzy filename resolution
    closest = find_closest_file(name)
    if closest:
        return closest

    return name
