import subprocess
import sys
import shutil

# Known friendly aliases (optional, grows over time)
APP_ALIASES = {
    "browser": "chrome",
    "google chrome": "chrome",
    "visual studio code": "code",
    "vscode": "code",
    "terminal": "cmd",
    "command prompt": "cmd"
}

def open_app(app_name: str):
    app = app_name.lower().strip()

    # 1️⃣ Alias resolution
    command = APP_ALIASES.get(app, app)

    if not sys.platform.startswith("win"):
        raise RuntimeError("This resolver is Windows-only for now")

    # 2️⃣ If command exists in PATH
    if shutil.which(command):
        subprocess.Popen(command, shell=True)
        return

    # 3️⃣ Try Windows 'start' (Start Menu / App Registry)
    try:
        subprocess.Popen(f'start "" "{command}"', shell=True)
        return
    except Exception:
        pass

    # 4️⃣ Try PowerShell Start-Process (more powerful)
    try:
        subprocess.Popen(
            ["powershell", "-Command", f"Start-Process '{command}'"],
            shell=True
        )
        return
    except Exception:
        pass

    print(f"❌ Could not find or open application: {app_name}")
