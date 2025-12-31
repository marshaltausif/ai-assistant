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
    """Convert folder aliases to standard names"""
    if not name:
        return None
    return FOLDER_ALIASES.get(name.lower().replace(" ", ""), name.upper())

def get_full_path(path: str) -> str:
    """Convert relative path to absolute path within AutoBox"""
    if not path:
        return None
    
    # Normalize path separators
    path = path.replace('\\', '/')
    
    # Check if path already includes AutoBox folder
    if path.startswith(('AB1/', 'AB2/', 'AB3/')):
        return os.path.join(AUTOBOX_DIR, path)
    
    # Check if path starts with folder alias
    parts = path.split('/')
    if len(parts) > 0 and parts[0].lower() in FOLDER_ALIASES:
        folder = normalize_folder(parts[0])
        filename = '/'.join(parts[1:]) if len(parts) > 1 else ""
        return os.path.join(AUTOBOX_DIR, folder, filename)
    
    # Default to AB1
    return os.path.join(AUTOBOX_DIR, "AB1", path)

def create_file(path: str, content: str = None) -> bool:
    """Create a file with optional content - FIXED to accept 2 arguments"""
    try:
        full_path = get_full_path(path)
        if not full_path:
            print(f"❌ Could not resolve path: {path}")
            return False
        
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write content if provided, otherwise create empty file
        if content:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Created file with content: {full_path}")
        else:
            # Create empty file
            with open(full_path, 'w', encoding='utf-8'):
                pass
            print(f"✅ Created empty file: {full_path}")
        
        return True
    except Exception as e:
        print(f"❌ Create file error: {e}")
        return False

def delete_file(path: str) -> bool:
    """Delete a file"""
    try:
        full_path = get_full_path(path)
        if full_path and os.path.exists(full_path):
            os.remove(full_path)
            print(f"✅ Deleted: {full_path}")
            return True
        print(f"❌ File not found: {path}")
        return False
    except Exception as e:
        print(f"❌ Delete file error: {e}")
        return False

def write_file(path: str, content: str) -> bool:
    """Write content to a file"""
    try:
        full_path = get_full_path(path)
        if not full_path:
            print(f"❌ Could not resolve path: {path}")
            return False
        
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content or "")
        
        print(f"✅ Wrote to file: {full_path}")
        return True
    except Exception as e:
        print(f"❌ Write file error: {e}")
        return False

def read_file(path: str) -> str:
    """Read content from a file"""
    try:
        full_path = get_full_path(path)
        if not full_path or not os.path.exists(full_path):
            print(f"❌ File not found: {path}")
            return None
        
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        print(f"✅ Read file: {full_path} ({len(content)} chars)")
        return content
    except Exception as e:
        print(f"❌ Read file error: {e}")
        return None

def move_file(source: str, destination: str) -> bool:
    """Move a file between AutoBox folders"""
    try:
        destination = normalize_folder(destination)

        # CASE 1: source already includes folder (e.g., AB2/House.py)
        if "/" in source:
            src_path = get_full_path(source)
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

        dst_path = os.path.join(dst_dir, os.path.basename(src_path))
        shutil.move(src_path, dst_path)
        
        print(f"✅ Moved: {src_path} -> {dst_path}")
        return True
        
    except Exception as e:
        print(f"❌ Move file error: {e}")
        return False