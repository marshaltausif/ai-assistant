import pyperclip
import subprocess
import platform
from typing import Optional

class ClipboardExecutor:
    def __init__(self):
        self.system = platform.system()
        self.history = []
    
    def copy(self, text: str) -> bool:
        """Copy text to clipboard"""
        try:
            pyperclip.copy(str(text))
            self.history.append(text)
            if len(self.history) > 10:
                self.history.pop(0)
            return True
        except Exception as e:
            print(f"❌ Copy failed: {e}")
            return False
    
    def paste(self) -> Optional[str]:
        """Get text from clipboard"""
        try:
            text = pyperclip.paste()
            return text if text else None
        except Exception as e:
            print(f"❌ Paste failed: {e}")
            return None
    
    def clear(self) -> bool:
        """Clear clipboard"""
        try:
            if self.system == "Windows":
                subprocess.run(['clip'], shell=True, input='', text=True)
            elif self.system == "Darwin":  # macOS
                subprocess.run(['pbcopy'], input='', text=True)
            else:  # Linux
                subprocess.run(['xclip', '-selection', 'c'], input='', text=True)
            return True
        except Exception as e:
            print(f"❌ Clear clipboard failed: {e}")
            return False
    
    def get_history(self) -> list:
        """Get clipboard history"""
        return self.history.copy()