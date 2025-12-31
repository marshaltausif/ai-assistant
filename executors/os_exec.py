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
    "command prompt": "cmd",
    "notepad": "notepad",
    "calculator": "calc",
    "paint": "mspaint",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt"
}

def open_app(app_name: str) -> bool:
    """Open an application on Windows"""
    app = app_name.lower().strip()
    
    # 1️⃣ Alias resolution
    command = APP_ALIASES.get(app, app)
    
    if not sys.platform.startswith("win"):
        print("⚠️ This resolver is Windows-only")
        return False

    try:
        print(f"🔄 Attempting to open: {app_name}")
        
        # 2️⃣ If command exists in PATH
        if shutil.which(command):
            print(f"✅ Found in PATH: {command}")
            subprocess.Popen(command, shell=True)
            return True
        
        # 3️⃣ Try Windows 'start' command
        print(f"🔄 Trying Windows 'start' command...")
        try:
            subprocess.Popen(f'start "" "{command}"', shell=True)
            print(f"✅ Opened via 'start' command")
            return True
        except Exception as e:
            print(f"⚠️ 'start' failed: {e}")
        
        # 4️⃣ Try PowerShell Start-Process
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
        
        # 5️⃣ Try common Windows applications
        windows_apps = {
            "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "notepad": "notepad.exe",
            "calc": "calc.exe",
            "mspaint": "mspaint.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe"
        }
        
        if app in windows_apps:
            try:
                subprocess.Popen(windows_apps[app], shell=True)
                print(f"✅ Opened via direct path")
                return True
            except Exception as e:
                print(f"⚠️ Direct path failed: {e}")
        
        print(f"❌ Could not find or open application: {app_name}")
        return False
        
    except Exception as e:
        print(f"❌ Error opening app: {e}")
        return False