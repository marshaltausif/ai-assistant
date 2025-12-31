#!/usr/bin/env python3
"""
Advanced AI Assistant Controller - COMPLETE VERSION (FIXED)
Supports: Files, Web, Clipboard, Apps, System operations
"""

import json
import sys
import traceback
from datetime import datetime
from typing import Dict, Any
import os

# Add project root to path
sys.path.append('.')

# Import your existing modules
from controller.llm import ask_llm  # Your working LLM
from executors.file_exec import create_file, write_file, read_file, move_file
from voice.stt import listen_and_transcribe
from voice.tts import speak
from memory.memory import load_memory, update_memory, resolve_reference

# Helper function for safe file creation
def safe_create_file(path: str, content: str = None) -> bool:
    """Handle create_file with optional content"""
    try:
        # Try with 2 arguments
        success = create_file(path, content)
        return success
    except TypeError as e:
        # If that fails, create empty then write
        print(f"⚠️ create_file() TypeError: {e}, using fallback")
        try:
            # Try with just path
            success = create_file(path)
            if success and content:
                # Write content separately
                return write_file(path, content)
            return success
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")
            return False
    except Exception as e:
        print(f"❌ Create file error: {e}")
        return False

# Add delete_file function 
def delete_file(path: str) -> bool:
    """Delete a file"""
    try:
        from executors.file_exec import get_full_path
        full_path = get_full_path(path)
        if full_path and os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
    except Exception as e:
        print(f"❌ Delete file error: {e}")
        return False

# Try to import optional modules
try:
    from executors.os_exec import open_app
    APP_ENABLED = True
except ImportError:
    APP_ENABLED = False
    print("⚠️ App executor not available")

try:
    from executors.web_exec import WebExecutor
    WEB_ENABLED = True
except ImportError:
    WEB_ENABLED = False
    print("⚠️ Web executor not available")

try:
    from executors.clipboard_exec import ClipboardExecutor
    CLIPBOARD_ENABLED = True
except ImportError:
    CLIPBOARD_ENABLED = False
    print("⚠️ Clipboard not available")

# Configuration - UPDATED MODEL NAME
CONFIG = {
    "VOICE_ENABLED": True,
    "VOICE_OUTPUT": True,
    "AUTOBOX_PATH": "AutoBox",
    "LLM_MODEL": "gemma3:1b",  # ⚠️ CHANGED FROM gemma:4b to gemma3:1b
    "ENABLE_WEB": WEB_ENABLED,
    "ENABLE_CLIPBOARD": CLIPBOARD_ENABLED,
    "ENABLE_APPS": APP_ENABLED,
}

class AdvancedAssistant:
    def __init__(self):
        self.config = CONFIG
        print("🤖 Advanced AI Assistant Initializing...")
        
        # Check AutoBox
        autobox_path = self.config["AUTOBOX_PATH"]
        if autobox_path.startswith("~"):
            autobox_path = os.path.expanduser(autobox_path)
        
        if not os.path.exists(autobox_path):
            print(f"⚠️ AutoBox not found at: {autobox_path}")
            print("Creating AutoBox folders...")
            os.makedirs(autobox_path, exist_ok=True)
            for folder in ["AB1", "AB2", "AB3"]:
                os.makedirs(os.path.join(autobox_path, folder), exist_ok=True)
        
        print("✅ AutoBox: Ready")
        
        # Initialize optional components
        if self.config["ENABLE_WEB"]:
            self.web = WebExecutor(headless=True)  # Changed to headless for less memory
            print("✅ Web: Ready (headless mode)")
        else:
            self.web = None
        
        if self.config["ENABLE_CLIPBOARD"]:
            self.clipboard = ClipboardExecutor()
            print("✅ Clipboard: Ready")
        else:
            self.clipboard = None
        
        if self.config["ENABLE_APPS"]:
            print("✅ Apps: Ready")
        
        print("✅ Voice: Ready")
        print(f"✅ LLM: Ready (using {self.config['LLM_MODEL']})")
        print("=" * 60)
    
    def say(self, text: str):
        """Output with voice and text"""
        if not text:
            return
        
        print(f"\n🤖 {text}")
        
        if self.config["VOICE_OUTPUT"]:
            speak(text)
    
    def get_user_input(self) -> str:
        """Get input from text or voice"""
        print("\n" + "=" * 60)
        print("💬 How can I help?")
        print("   Type command, 'v' for voice, 'multi' for multi-line, 'exit' to quit")
        print("-" * 40)
        
        mode = input(">> ").strip()
        
        if mode.lower() == 'exit':
            return 'exit'
        
        if mode.lower() == 'v':
            self.say("Listening...")
            user_input = listen_and_transcribe()
            self.say(f"You said: {user_input}")
            return user_input
        
        if mode.lower() == 'multi':
            print("Enter multi-line command (empty line to finish):")
            lines = []
            while True:
                line = input("... ")
                if line == "":
                    break
                lines.append(line)
            return '\n'.join(lines)
        
        if mode.lower() == 'help':
            self.show_help()
            return ""
        
        if mode.lower() == 'status':
            self.show_status()
            return ""
        
        return mode
    
    def execute_intent(self, intent: Dict[str, Any]) -> bool:
        """Execute validated intent"""
        steps = intent.get("steps", [])
        
        if not steps:
            self.say("No executable actions found in your request.")
            return False
        
        all_success = True
        
        for i, step in enumerate(steps):
            self.say(f"Executing step {i+1}/{len(steps)}...")
            
            action = step.get("action", "").lower()
            target = step.get("target", "")
            content = step.get("content", "")
            
            # Map actions to handlers
            success = False
            
            # FILE OPERATIONS
            if action in ["create_file", "file_create"]:
                success = self.handle_create_file(target, content)
            elif action in ["write_file", "file_write"]:
                success = self.handle_write_file(target, content)
            elif action in ["read_file", "file_read"]:
                success = self.handle_read_file(target)
            elif action in ["move_file", "file_move"]:
                success = self.handle_move_file(target, content)
            elif action in ["delete_file", "file_delete"]:
                success = self.handle_delete_file(target)
            
            # WEB OPERATIONS
            elif action in ["open_url", "web_open"]:
                success = self.handle_open_url(target)
            elif action in ["search_web", "web_search", "search"]:
                success = self.handle_search_web(target)
            elif action in ["extract_web", "web_extract"]:
                success = self.handle_extract_web(target)
            
            # CLIPBOARD OPERATIONS
            elif action in ["copy_clipboard", "clip_copy", "copy"]:
                success = self.handle_copy_clipboard(target or content)
            elif action in ["paste_clipboard", "clip_paste", "paste"]:
                success = self.handle_paste_clipboard()
            
            # APP OPERATIONS
            elif action in ["open_app", "app_open"]:
                success = self.handle_open_app(target)
            
            # SYSTEM OPERATIONS
            elif action in ["system_info", "info"]:
                success = self.handle_system_info()
            
            # UNKNOWN ACTION
            else:
                self.say(f"Unknown action: {action}")
                success = False
            
            if not success:
                all_success = False
                self.say(f"Step {i+1} failed")
        
        return all_success
    
    # FILE HANDLERS - FIXED create_file issue
    def handle_create_file(self, target: str, content: str = None) -> bool:
        try:
            # Ensure path includes AutoBox folder
            if not any(folder in target.upper() for folder in ["AB1", "AB2", "AB3"]):
                # Use last folder or default
                memory = load_memory()
                last_folder = memory.get("last_folder", "AB1")
                target = f"{last_folder}/{target}"
            
            # ⚠️ FIXED: Use safe_create_file instead of create_file
            success = safe_create_file(target, content)
            
            if success:
                update_memory(last_created_file=target, last_folder=target.split("/")[0])
                self.say(f"Created file: {target}")
            else:
                self.say(f"Failed to create: {target}")
            
            return success
        except Exception as e:
            self.say(f"Failed to create file: {str(e)}")
            return False
    
    def handle_write_file(self, target: str, content: str) -> bool:
        try:
            target = resolve_reference(target) or target
            success = write_file(target, content)
            if success:
                update_memory(last_written_file=target)
                self.say(f"Wrote to: {target}")
            else:
                self.say(f"Failed to write: {target}")
            return success
        except Exception as e:
            self.say(f"Failed to write file: {str(e)}")
            return False
    
    def handle_read_file(self, target: str) -> bool:
        try:
            target = resolve_reference(target) or target
            content = read_file(target)
            if content is None:
                self.say(f"File not found: {target}")
                return False
            
            self.say(f"Contents of {target}:")
            print("\n" + "="*50)
            print(content)
            print("="*50 + "\n")
            
            update_memory(last_read_file=target)
            
            # Ask if user wants to copy to clipboard
            if self.clipboard and len(content) < 1000:
                copy = input("Copy to clipboard? (y/n): ").lower()
                if copy == 'y':
                    self.clipboard.copy(content)
                    self.say("Copied to clipboard")
            
            return True
        except Exception as e:
            self.say(f"Failed to read file: {str(e)}")
            return False
    
    def handle_move_file(self, source: str, destination: str) -> bool:
        try:
            source = resolve_reference(source) or source
            move_file(source, destination)
            update_memory(last_moved_file=source, last_folder=destination)
            self.say(f"Moved {source} to {destination}")
            return True
        except Exception as e:
            self.say(f"Failed to move file: {str(e)}")
            return False
    
    def handle_delete_file(self, target: str) -> bool:
        try:
            target = resolve_reference(target) or target
            success = delete_file(target)
            if success:
                self.say(f"Deleted: {target}")
            else:
                self.say(f"File not found: {target}")
            return success
        except Exception as e:
            self.say(f"Failed to delete file: {str(e)}")
            return False
    
    # WEB HANDLERS
    def handle_open_url(self, url: str) -> bool:
        if not self.web:
            self.say("Web features are disabled")
            return False
        
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            success = self.web.open_url(url)
            if success:
                self.say(f"Opened: {url}")
                update_memory(last_url=url)
            return success
        except Exception as e:
            self.say(f"Failed to open URL: {str(e)}")
            return False
    
    def handle_search_web(self, query: str) -> bool:
        if not self.web:
            self.say("Web features are disabled")
            return False
        
        try:
            # Simple search - just open Google
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            success = self.web.open_url(search_url)
            
            if success:
                self.say(f"Searching for: {query}")
                update_memory(last_search=query)
                
                # Ask if user wants to save search
                save = input("Save search results? (y/n): ").lower()
                if save == 'y':
                    import time
                    filename = f"AB1/search_{query[:20]}_{int(time.time())}.txt"
                    content = f"Search query: {query}\nURL: {search_url}\nTimestamp: {datetime.now()}"
                    write_file(filename, content)
                    self.say(f"Saved search to {filename}")
            
            return success
        except Exception as e:
            self.say(f"Search failed: {str(e)}")
            return False
    
    def handle_extract_web(self, url: str) -> bool:
        if not self.web:
            self.say("Web features are disabled")
            return False
        
        try:
            content = self.web.get_page_content(url)
            if content:
                self.say(f"Extracted content from {url}:")
                print("\n" + "-"*50)
                print(content[:500] + "..." if len(content) > 500 else content)
                print("-"*50 + "\n")
                
                # Auto-save to AutoBox
                import hashlib
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                filename = f"AB1/web_{url_hash}.txt"
                write_file(filename, content)
                self.say(f"Auto-saved to {filename}")
                
                # Copy to clipboard
                if self.clipboard and len(content) < 1000:
                    self.clipboard.copy(content[:500])
                    self.say("First 500 chars copied to clipboard")
                
                return True
            else:
                self.say(f"Could not extract content from {url}")
                return False
        except Exception as e:
            self.say(f"Extraction failed: {str(e)}")
            return False
    
    # CLIPBOARD HANDLERS
    def handle_copy_clipboard(self, text: str) -> bool:
        if not self.clipboard:
            self.say("Clipboard features are disabled")
            return False
        
        try:
            success = self.clipboard.copy(text)
            if success:
                self.say("Copied to clipboard")
            return success
        except Exception as e:
            self.say(f"Copy failed: {str(e)}")
            return False
    
    def handle_paste_clipboard(self) -> bool:
        if not self.clipboard:
            self.say("Clipboard features are disabled")
            return False
        
        try:
            text = self.clipboard.paste()
            if text:
                self.say("Clipboard contents:")
                print("\n" + "="*50)
                print(text[:500] + "..." if len(text) > 500 else text)
                print("="*50 + "\n")
                
                # Ask if user wants to save
                save = input("Save clipboard to file? (y/n): ").lower()
                if save == 'y':
                    import time
                    filename = f"AB1/clipboard_{int(time.time())}.txt"
                    write_file(filename, text)
                    self.say(f"Saved to {filename}")
                
                return True
            else:
                self.say("Clipboard is empty")
                return False
        except Exception as e:
            self.say(f"Paste failed: {str(e)}")
            return False
    
    # APP HANDLER
    def handle_open_app(self, app_name: str) -> bool:
        if not APP_ENABLED:
            self.say("App features are disabled")
            return False
        
        try:
            success = open_app(app_name)
            if success:
                self.say(f"Opening {app_name}")
                update_memory(last_app=app_name)
            return success
        except Exception as e:
            self.say(f"Failed to open app: {str(e)}")
            return False
    
    # SYSTEM HANDLER
    def handle_system_info(self) -> bool:
        try:
            import platform
            import psutil
            
            info = {
                "OS": platform.system(),
                "Version": platform.version(),
                "Processor": platform.processor(),
                "Python": platform.python_version(),
                "CPU Usage": f"{psutil.cpu_percent()}%",
                "Memory": f"{psutil.virtual_memory().percent}% used",
                "Disk": f"{psutil.disk_usage('/').percent}% used"
            }
            
            self.say("System Information:")
            for key, value in info.items():
                print(f"  {key}: {value}")
            
            # Save to file
            content = "\n".join([f"{k}: {v}" for k, v in info.items()])
            write_file("AB1/system_info.txt", content)
            
            return True
        except ImportError:
            self.say("Install psutil for system info: pip install psutil")
            return False
        except Exception as e:
            self.say(f"System info failed: {str(e)}")
            return False
    
    def process_command(self, user_input: str):
        """Main processing pipeline"""
        if not user_input or user_input.strip() == "":
            return
        
        # Get intent from LLM
        self.say("Analyzing command...")
        json_response = ask_llm(user_input)
        
        # Parse JSON
        try:
            intent = json.loads(json_response)
        except json.JSONDecodeError:
            self.say("I couldn't understand that command.")
            print(f"Raw LLM response: {json_response}")
            return
        
        # Execute intent
        success = self.execute_intent(intent)
        
        if success:
            self.say("✅ All tasks completed successfully!")
        else:
            self.say("⚠️ Some tasks had issues. Check above for errors.")
    
    def show_help(self):
        """Show available commands"""
        help_text = """
🎯 ADVANCED AI ASSISTANT - COMMAND REFERENCE

📁 FILE OPERATIONS:
  • create [file] in [ab1/ab2/ab3]    - Create file
  • write [text] to [file]            - Write content
  • read [file]                       - Read file content
  • move [file] to [folder]           - Move between AutoBox folders
  • delete [file]                     - Delete file

🌐 WEB OPERATIONS:
  • open [url]                        - Open website in browser
  • search [query]                    - Google search
  • extract from [url]                - Extract webpage content

📋 CLIPBOARD:
  • copy [text]                       - Copy to clipboard
  • paste                             - Show clipboard contents

💻 APPLICATIONS:
  • open [app]                        - Open application

🖥️ SYSTEM:
  • system info                       - Show system information

🗣️ VOICE CONTROL:
  • v                                 - Switch to voice input
  • multi                             - Multi-line text input

🔧 SPECIAL:
  • help                              - Show this help
  • status                            - Show system status
  • exit                              - Quit assistant

📚 EXAMPLES:
  • create notes.txt in ab2
  • write "Meeting notes" to AB2/notes.txt
  • read AB2/notes.txt
  • open google.com
  • search artificial intelligence news
  • copy this text to clipboard
  • open notepad
  • system info
"""
        print(help_text)
    
    def show_status(self):
        """Show system status"""
        memory = load_memory()
        print("\n📊 SYSTEM STATUS:")
        print(f"  AutoBox: {self.config['AUTOBOX_PATH']}")
        print(f"  Voice: {'Enabled' if self.config['VOICE_ENABLED'] else 'Disabled'}")
        print(f"  Web: {'Enabled' if self.config['ENABLE_WEB'] else 'Disabled'}")
        print(f"  Clipboard: {'Enabled' if self.config['ENABLE_CLIPBOARD'] else 'Disabled'}")
        print(f"  Apps: {'Enabled' if self.config['ENABLE_APPS'] else 'Disabled'}")
        print(f"  LLM Model: {self.config['LLM_MODEL']}")
        print("\n📝 RECENT ACTIONS:")
        for key, value in memory.items():
            if value:
                print(f"  {key}: {value}")
    
    def run(self):
        """Main loop"""
        self.say("🚀 ADVANCED AI ASSISTANT READY!")
        self.say(f"Using LLM model: {self.config['LLM_MODEL']}")
        self.say("Type 'help' to see all commands")
        
        while True:
            try:
                user_input = self.get_user_input()
                
                if user_input == 'exit':
                    self.say("Goodbye! 👋")
                    break
                
                if user_input == '':
                    continue
                
                # Process the command
                self.process_command(user_input)
                
            except KeyboardInterrupt:
                self.say("\nInterrupted. Type 'exit' to quit.")
                continue
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                traceback.print_exc()
                continue

def main():
    """Entry point"""
    try:
        assistant = AdvancedAssistant()
        assistant.run()
    except Exception as e:
        print(f"Fatal error during startup: {e}")
        traceback.print_exc()
        print("\nTry running the simple version: python simple_run.py")

if __name__ == "__main__":
    main()