import subprocess
import sys
import shutil

# Known friendly aliases
APP_ALIASES = {
    "browser": "chrome",
    "google chrome": "chrome",
    "visual studio code": "code",
    "vscode": "code",
    "terminal": "cmd",
    "command prompt": "cmd",
    "notepad": "notepad",
    "calculator": "calc",
    "paint": "mspaint",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "edge": "msedge",
    "firefox": "firefox",
    "opera": "opera",
    "brave": "brave",
    "spotify": "spotify",
    "vlc": "vlc",
    "photoshop": "photoshop"
}

def open_app(app_name: str) -> bool:
    """Open an application on Windows"""
    app = app_name.lower().strip()
    
    # Alias resolution
    command = APP_ALIASES.get(app, app)
    
    if not sys.platform.startswith("win"):
        print("⚠️ This resolver is Windows-only")
        return False

    print(f"🔄 Attempting to open: {app_name} (command: {command})")
    
    try:
        # 1. Try direct execution
        if shutil.which(command):
            print(f"✅ Found in PATH: {command}")
            subprocess.Popen(command, shell=True)
            return True
        
        # 2. Try Windows 'start' command
        print(f"🔄 Trying Windows 'start' command...")
        try:
            subprocess.Popen(f'start "" "{command}"', shell=True)
            print(f"✅ Opened via 'start' command")
            return True
        except Exception as e:
            print(f"⚠️ 'start' failed: {e}")
        
        # 3. Try PowerShell
        print(f"🔄 Trying PowerShell...")
        try:
            subprocess.Popen(
                ["powershell", "-Command", f"Start-Process '{command}'"],
                shell=True
            )
            print(f"✅ Opened via PowerShell")
            return True
        except Exception as e:
            print(f"⚠️ PowerShell failed: {e}")
        
        # 4. Try common Windows applications with paths
        windows_apps = {
            "chrome": [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            ],
            "notepad": ["notepad.exe"],
            "calc": ["calc.exe"],
            "mspaint": ["mspaint.exe"],
            "cmd": ["cmd.exe"],
            "powershell": ["powershell.exe"],
            "explorer": ["explorer.exe"],
            "edge": ["C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"]
        }
        
        if app in windows_apps:
            for path in windows_apps[app]:
                try:
                    if os.path.exists(path):
                        subprocess.Popen(path, shell=True)
                        print(f"✅ Opened via direct path: {path}")
                        return True
                except Exception as e:
                    print(f"⚠️ Path {path} failed: {e}")
        
        # 5. Last resort: try just the name
        print(f"🔄 Trying raw command...")
        try:
            subprocess.Popen(command, shell=True)
            print(f"✅ Opened via raw command")
            return True
        except Exception as e:
            print(f"❌ All methods failed: {e}")
        
        print(f"❌ Could not open application: {app_name}")
        return False
        
    except Exception as e:
        print(f"❌ Error opening app: {e}")
        return False

def close_app(app_name: str) -> bool:
    """Close an application (simplified)"""
    try:
        if sys.platform.startswith("win"):
            subprocess.run(["taskkill", "/f", "/im", f"{app_name}.exe"], 
                          capture_output=True, shell=True)
            print(f"✅ Attempted to close: {app_name}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error closing app: {e}")
        return False