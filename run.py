#!/usr/bin/env python3
"""
Advanced AI Assistant Controller - COMPLETE 600+ LINE VERSION (FULLY FIXED)
Supports: Files, Web, Clipboard, Apps, System operations - ALL ISSUES RESOLVED
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

# ================== CRITICAL FIXES ==================
# Helper function for safe file creation with list handling
def safe_create_file(path: str, content: any = None) -> bool:
    """Handle create_file with optional content - FIXED for lists"""
    try:
        # Convert content to string if it's a list
        if isinstance(content, list):
            content = ", ".join(str(item) for item in content)
        elif isinstance(content, dict):
            content = json.dumps(content, indent=2)
        elif content is not None:
            content = str(content)
        
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

# Helper to normalize any content to string
def normalize_content(content: any) -> str:
    """Convert any content type to string - CRITICAL FIX for lists"""
    if content is None:
        return None
    if isinstance(content, list):
        return ", ".join(str(item) for item in content)
    if isinstance(content, dict):
        return json.dumps(content, indent=2)
    return str(content)

# Add delete_file function to file_exec.py if missing
def delete_file(path: str) -> bool:
    """Delete a file"""
    try:
        from executors.file_exec import get_full_path
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

# ================== OPTIONAL IMPORTS ==================
# Try to import optional modules
try:
    from executors.os_exec import open_app, close_app
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

# ================== CONFIGURATION ==================
# Configuration - UPDATED WITH VISIBLE BROWSER
CONFIG = {
    "VOICE_ENABLED": True,
    "VOICE_OUTPUT": True,
    "AUTOBOX_PATH": "AutoBox",
    "LLM_MODEL": "gemma3:1b",  # ⚠️ CORRECTED MODEL NAME
    "ENABLE_WEB": WEB_ENABLED,
    "ENABLE_CLIPBOARD": CLIPBOARD_ENABLED,
    "ENABLE_APPS": APP_ENABLED,
    "BROWSER_VISIBLE": True,  # ⚠️ NEW: Make browser visible
}

# ================== MAIN ASSISTANT CLASS ==================
class AdvancedAssistant:
    def __init__(self):
        self.config = CONFIG
        print("🤖 Advanced AI Assistant Initializing...")
        print("=" * 70)
        
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
            print("✅ AutoBox created successfully")
        else:
            print("✅ AutoBox: Ready")
        
        # Initialize optional components
        if self.config["ENABLE_WEB"]:
            # ⚠️ FIXED: Use VISIBLE browser (not headless)
            headless_mode = not self.config["BROWSER_VISIBLE"]
            self.web = WebExecutor(headless=headless_mode)
            if headless_mode:
                print("✅ Web: Ready (headless mode)")
            else:
                print("✅ Web: Ready (VISIBLE browser mode)")
        else:
            self.web = None
        
        if self.config["ENABLE_CLIPBOARD"]:
            self.clipboard = ClipboardExecutor()
            print("✅ Clipboard: Ready")
        else:
            self.clipboard = None
        
        if self.config["ENABLE_APPS"]:
            print("✅ Apps: Ready")
        
        print("✅ Voice: Ready (TTS & STT)")
        print(f"✅ LLM: Ready (using {self.config['LLM_MODEL']})")
        print("=" * 70)
    
    def say(self, text: str):
        """Output with voice and text"""
        if not text:
            return
        
        print(f"\n🤖 {text}")
        
        if self.config["VOICE_OUTPUT"]:
            speak(text)
    
    def get_user_input(self) -> str:
        """Get input from text or voice"""
        print("\n" + "=" * 70)
        print("💬 HOW CAN I HELP YOU?")
        print("   Type command, 'v' for voice, 'multi' for multi-line, 'exit' to quit")
        print("   'help' for commands, 'status' for system info")
        print("-" * 50)
        
        mode = input(">> ").strip()
        
        if mode.lower() == 'exit':
            return 'exit'
        
        if mode.lower() == 'v':
            self.say("Listening... Speak now")
            user_input = listen_and_transcribe()
            self.say(f"You said: {user_input}")
            return user_input
        
        if mode.lower() == 'multi':
            print("\n📝 Enter multi-line command (type 'END' on a new line to finish):")
            lines = []
            while True:
                line = input("... ")
                if line.upper() == 'END':
                    break
                lines.append(line)
            return '\n'.join(lines)
        
        if mode.lower() == 'help':
            self.show_help()
            return ""
        
        if mode.lower() == 'status':
            self.show_status()
            return ""
        
        if mode.lower() == 'clear':
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            return ""
        
        return mode
    
    def execute_intent(self, intent: Dict[str, Any], original_input: str = "") -> bool:
        """Execute validated intent with ALL FIXES"""
        steps = intent.get("steps", [])
        
        if not steps:
            # Check if it's a greeting/chat command
            if self.is_chat_command(original_input):
                return self.handle_chat_command(original_input)
            self.say("No executable actions found in your request.")
            return False
        
        all_success = True
        
        for i, step in enumerate(steps):
            self.say(f"🚀 Executing step {i+1}/{len(steps)}...")
            
            action = step.get("action", "").lower()
            target = step.get("target", "")
            content = step.get("content", "")
            
            # ⚠️ CRITICAL FIX: Normalize content before processing
            content = normalize_content(content)
            
            # Map actions to handlers
            success = False
            
            # FILE OPERATIONS (WITH LIST HANDLING FIX)
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
            
            # WEB OPERATIONS (WITH VISIBLE BROWSER FIX)
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
            elif action == "close_app":
                success = self.handle_close_app(target)
            
            # SYSTEM OPERATIONS
            elif action in ["system_info", "info"]:
                success = self.handle_system_info()
            
            # CHAT/NO ACTION
            elif action in ["none", "chat", "respond"]:
                success = self.handle_chat_command(original_input or target or content or "Hello")
            
            # UNKNOWN ACTION
            else:
                self.say(f"⚠️ Unknown action: '{action}'")
                success = False
            
            if not success:
                all_success = False
                self.say(f"❌ Step {i+1} failed")
            else:
                self.say(f"✅ Step {i+1} completed")
        
        return all_success
    
    # ================== FILE HANDLERS (FIXED) ==================
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
                self.say(f"📄 Created file: {target}")
                if content:
                    self.say(f"   Content: {content[:50]}{'...' if len(content) > 50 else ''}")
            else:
                self.say(f"❌ Failed to create: {target}")
            
            return success
        except Exception as e:
            self.say(f"❌ Failed to create file: {str(e)}")
            return False
    
    def handle_write_file(self, target: str, content: str) -> bool:
        try:
            target = resolve_reference(target) or target
            
            # ⚠️ FIXED: Content already normalized
            success = write_file(target, content)
            
            if success:
                update_memory(last_written_file=target)
                self.say(f"✏️  Wrote to: {target}")
                self.say(f"   Content: {content[:50]}{'...' if len(content) > 50 else ''}")
            else:
                self.say(f"❌ Failed to write: {target}")
            
            return success
        except Exception as e:
            self.say(f"❌ Failed to write file: {str(e)}")
            return False
    
    def handle_read_file(self, target: str) -> bool:
        try:
            target = resolve_reference(target) or target
            content = read_file(target)
            
            if content is None:
                self.say(f"❌ File not found: {target}")
                return False
            
            self.say(f"📖 Contents of {target}:")
            print("\n" + "="*60)
            print(content)
            print("="*60 + "\n")
            
            update_memory(last_read_file=target)
            
            # Ask if user wants to copy to clipboard
            if self.clipboard and len(content) < 1000:
                copy = input("📋 Copy to clipboard? (y/n): ").lower()
                if copy == 'y':
                    self.clipboard.copy(content)
                    self.say("✅ Copied to clipboard")
            
            return True
        except Exception as e:
            self.say(f"❌ Failed to read file: {str(e)}")
            return False
    
    def handle_move_file(self, source: str, destination: str) -> bool:
        try:
            source = resolve_reference(source) or source
            move_file(source, destination)
            update_memory(last_moved_file=source, last_folder=destination)
            self.say(f"🚚 Moved {source} to {destination}")
            return True
        except Exception as e:
            self.say(f"❌ Failed to move file: {str(e)}")
            return False
    
    def handle_delete_file(self, target: str) -> bool:
        try:
            target = resolve_reference(target) or target
            success = delete_file(target)
            
            if success:
                self.say(f"🗑️  Deleted: {target}")
            else:
                self.say(f"❌ File not found: {target}")
            
            return success
        except Exception as e:
            self.say(f"❌ Failed to delete file: {str(e)}")
            return False
    
    # ================== WEB HANDLERS (VISIBLE BROWSER) ==================
    def handle_open_url(self, url: str) -> bool:
        if not self.web:
            self.say("❌ Web features are disabled")
            return False
        
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            success = self.web.open_url(url)
            if success:
                self.say(f"🌐 Opened: {url}")
                update_memory(last_url=url)
            else:
                self.say(f"❌ Failed to open: {url}")
            
            return success
        except Exception as e:
            self.say(f"❌ Failed to open URL: {str(e)}")
            return False
    
    def handle_search_web(self, query: str) -> bool:
        if not self.web:
            self.say("❌ Web features are disabled")
            return False
        
        try:
            # Simple search - just open Google
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            success = self.web.open_url(search_url)
            
            if success:
                self.say(f"🔍 Searching for: {query}")
                update_memory(last_search=query)
                
                # Ask if user wants to save search
                save = input("💾 Save search results? (y/n): ").lower()
                if save == 'y':
                    import time
                    from executors.file_exec import write_file
                    filename = f"AB1/search_{query[:20]}_{int(time.time())}.txt"
                    content = f"Search query: {query}\nURL: {search_url}\nTimestamp: {datetime.now()}"
                    write_file(filename, content)
                    self.say(f"✅ Saved search to {filename}")
            
            return success
        except Exception as e:
            self.say(f"❌ Search failed: {str(e)}")
            return False
    
    def handle_extract_web(self, url: str) -> bool:
        if not self.web:
            self.say("❌ Web features are disabled")
            return False
        
        try:
            content = self.web.get_page_content(url)
            if content:
                self.say(f"📄 Extracted content from {url}:")
                print("\n" + "-"*60)
                print(content[:500] + "..." if len(content) > 500 else content)
                print("-"*60 + "\n")
                
                # Auto-save to AutoBox
                import hashlib
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                filename = f"AB1/web_{url_hash}.txt"
                from executors.file_exec import write_file
                write_file(filename, content)
                self.say(f"💾 Auto-saved to {filename}")
                
                # Copy to clipboard
                if self.clipboard and len(content) < 1000:
                    self.clipboard.copy(content[:500])
                    self.say("📋 First 500 chars copied to clipboard")
                
                return True
            else:
                self.say(f"❌ Could not extract content from {url}")
                return False
        except Exception as e:
            self.say(f"❌ Extraction failed: {str(e)}")
            return False
    
    # ================== CLIPBOARD HANDLERS ==================
    def handle_copy_clipboard(self, text: str) -> bool:
        if not self.clipboard:
            self.say("❌ Clipboard features are disabled")
            return False
        
        try:
            success = self.clipboard.copy(text)
            if success:
                self.say("📋 Copied to clipboard")
                self.say(f"   Text: {text[:50]}{'...' if len(text) > 50 else ''}")
            return success
        except Exception as e:
            self.say(f"❌ Copy failed: {str(e)}")
            return False
    
    def handle_paste_clipboard(self) -> bool:
        if not self.clipboard:
            self.say("❌ Clipboard features are disabled")
            return False
        
        try:
            text = self.clipboard.paste()
            if text:
                self.say("📋 Clipboard contents:")
                print("\n" + "="*60)
                print(text[:500] + "..." if len(text) > 500 else text)
                print("="*60 + "\n")
                
                # Ask if user wants to save
                save = input("💾 Save clipboard to file? (y/n): ").lower()
                if save == 'y':
                    import time
                    from executors.file_exec import write_file
                    filename = f"AB1/clipboard_{int(time.time())}.txt"
                    write_file(filename, text)
                    self.say(f"✅ Saved to {filename}")
                
                return True
            else:
                self.say("📋 Clipboard is empty")
                return False
        except Exception as e:
            self.say(f"❌ Paste failed: {str(e)}")
            return False
    
    # ================== APP HANDLERS ==================
    def handle_open_app(self, app_name: str) -> bool:
        if not APP_ENABLED:
            self.say("❌ App features are disabled")
            return False
        
        try:
            success = open_app(app_name)
            if success:
                self.say(f"🚀 Opening {app_name}")
                update_memory(last_app=app_name)
            else:
                self.say(f"❌ Could not open {app_name}")
            return success
        except Exception as e:
            self.say(f"❌ Failed to open app: {str(e)}")
            return False
    
    def handle_close_app(self, app_name: str) -> bool:
        if not APP_ENABLED:
            self.say("❌ App features are disabled")
            return False
        
        try:
            success = close_app(app_name)
            if success:
                self.say(f"⏹️  Closing {app_name}")
            return success
        except Exception as e:
            self.say(f"❌ Failed to close app: {str(e)}")
            return False
    
    # ================== SYSTEM HANDLER ==================
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
                "Disk": f"{psutil.disk_usage('/').percent}% used",
                "Uptime": f"{psutil.boot_time()} seconds"
            }
            
            self.say("🖥️ System Information:")
            print("\n" + "-"*40)
            for key, value in info.items():
                print(f"  {key:15}: {value}")
            print("-"*40 + "\n")
            
            # Save to file
            from executors.file_exec import write_file
            content = "\n".join([f"{k}: {v}" for k, v in info.items()])
            write_file("AB1/system_info.txt", content)
            self.say("💾 System info saved to AB1/system_info.txt")
            
            return True
        except ImportError:
            self.say("⚠️ Install psutil for system info: pip install psutil")
            return False
        except Exception as e:
            self.say(f"❌ System info failed: {str(e)}")
            return False
    
    # ================== CHAT HANDLER ==================
    def is_chat_command(self, text: str) -> bool:
        """Check if input is conversational"""
        if not text:
            return False
        
        text = text.lower().strip()
        chat_words = ["hello", "hi", "hey", "how are you", "what's up", 
                     "good morning", "good evening", "good afternoon",
                     "thank you", "thanks", "please", "sorry", "bye", "goodbye",
                     "what can you do", "who are you", "your name"]
        
        question_words = ["what", "how", "why", "when", "where", "who", "can you", "could you"]
        
        # Check for greetings
        if any(word in text for word in chat_words):
            return True
        
        # Check for questions
        if "?" in text:
            return True
        
        # Check for question starters
        words = text.split()
        if words and words[0] in question_words:
            return True
        
        return False
    
    def handle_chat_command(self, user_input: str) -> bool:
        """Handle conversational inputs - FIXED to not create files"""
        text = user_input.lower().strip()
        
        # Greetings
        if any(word in text for word in ["hello", "hi", "hey"]):
            responses = [
                "Hello! I'm your AI assistant. How can I help you today?",
                "Hi there! Ready to execute some commands!",
                "Hey! What would you like me to do?",
            ]
            import random
            response = random.choice(responses)
            self.say(response)
            return True
        
        # How are you
        if "how are you" in text:
            self.say("I'm functioning optimally! Ready to help you with tasks.")
            return True
        
        # Thanks
        if any(word in text for word in ["thank", "thanks"]):
            self.say("You're welcome! Happy to help.")
            return True
        
        # Goodbye
        if any(word in text for word in ["bye", "goodbye"]):
            self.say("Goodbye! Have a great day.")
            return True
        
        # What can you do
        if "what can you do" in text or "your name" in text or "who are you" in text:
            self.say("I'm a local AI assistant. I can create files, open apps, browse web, manage clipboard, and execute system commands.")
            return True
        
        # Time
        if "time" in text:
            current_time = datetime.now().strftime("%I:%M %p")
            self.say(f"The current time is {current_time}")
            return True
        
        # Questions
        if "?" in text or any(word in text for word in ["what", "how", "why", "when", "where"]):
            self.say("I'm focused on executing commands. Try: 'create file', 'open app', 'search web', or type 'help' for all commands.")
            return True
        
        # Default: friendly response
        self.say("I'm here to help! Type 'help' to see what I can do.")
        return True
    
    # ================== MAIN PROCESSING ==================
    def process_command(self, user_input: str):
        """Main processing pipeline"""
        if not user_input or user_input.strip() == "":
            return
        
        # Get intent from LLM
        self.say("🧠 Analyzing command...")
        json_response = ask_llm(user_input)
        
        # Parse JSON
        try:
            intent = json.loads(json_response)
        except json.JSONDecodeError:
            self.say("❌ I couldn't understand that command.")
            print(f"Raw LLM response: {json_response}")
            
            # Try chat mode as fallback
            if self.is_chat_command(user_input):
                self.handle_chat_command(user_input)
            return
        
        # Execute intent
        success = self.execute_intent(intent, user_input)
        
        if success:
            self.say("🎉 All tasks completed successfully!")
        else:
            self.say("⚠️ Some tasks had issues. Check above for errors.")
    
    def show_help(self):
        """Show available commands"""
        help_text = """
🤖 ADVANCED AI ASSISTANT - COMMAND REFERENCE
══════════════════════════════════════════════════════════════

📁 FILE OPERATIONS:
  • create [file] in [ab1/ab2/ab3]    - Create file
  • write [text] to [file]            - Write content
  • read [file]                       - Read file content
  • move [file] to [folder]           - Move between AutoBox folders
  • delete [file]                     - Delete file

🌐 WEB OPERATIONS:
  • open [url]                        - Open website in VISIBLE browser
  • search [query]                    - Google search
  • extract from [url]                - Extract webpage content

📋 CLIPBOARD:
  • copy [text]                       - Copy to clipboard
  • paste                             - Show clipboard contents

💻 APPLICATIONS:
  • open [app]                        - Open application
  • close [app]                       - Close application

🖥️ SYSTEM:
  • system info                       - Show system information

💬 CHAT/QUESTIONS:
  • hello, hi, how are you            - Greet the assistant
  • what time is it                   - Get current time
  • what can you do                   - List capabilities
  • thanks, thank you                 - Say thanks
  • bye, goodbye                      - Say goodbye

🔧 SPECIAL COMMANDS:
  • v                                 - Switch to voice input
  • multi                             - Multi-line text input
  • help                              - Show this help
  • status                            - Show system status
  • clear                             - Clear screen
  • exit                              - Quit assistant

📚 EXAMPLES:
  • create notes.txt in ab2
  • write "Meeting notes" to AB2/notes.txt
  • read AB2/notes.txt
  • open google.com                    (VISIBLE browser)
  • search artificial intelligence news
  • copy this text to clipboard
  • open notepad
  • system info
  • hello
  • what time is it

══════════════════════════════════════════════════════════════
"""
        print(help_text)
    
    def show_status(self):
        """Show system status"""
        memory = load_memory()
        print("\n📊 SYSTEM STATUS:")
        print("═" * 50)
        print(f"  AutoBox: {self.config['AUTOBOX_PATH']}")
        print(f"  Voice: {'✅ Enabled' if self.config['VOICE_ENABLED'] else '❌ Disabled'}")
        print(f"  Web: {'✅ Enabled (VISIBLE)' if self.config['ENABLE_WEB'] and self.config['BROWSER_VISIBLE'] else '✅ Enabled (Headless)' if self.config['ENABLE_WEB'] else '❌ Disabled'}")
        print(f"  Clipboard: {'✅ Enabled' if self.config['ENABLE_CLIPBOARD'] else '❌ Disabled'}")
        print(f"  Apps: {'✅ Enabled' if self.config['ENABLE_APPS'] else '❌ Disabled'}")
        print(f"  LLM Model: {self.config['LLM_MODEL']}")
        print("\n📝 RECENT ACTIONS:")
        for key, value in memory.items():
            if value:
                print(f"  {key:20}: {value}")
        print("═" * 50)
    
    def run(self):
        """Main loop"""
        self.say("🚀 ADVANCED AI ASSISTANT READY!")
        self.say(f"📡 Using LLM model: {self.config['LLM_MODEL']}")
        self.say("🔊 Voice: Enabled | 🌐 Browser: VISIBLE | 💾 AutoBox: Ready")
        self.say("Type 'help' to see all commands")
        print("\n" + "=" * 70)
        
        while True:
            try:
                user_input = self.get_user_input()
                
                if user_input == 'exit':
                    self.say("👋 Goodbye! Shutting down...")
                    # Clean up
                    if self.web:
                        self.web.close()
                    break
                
                if user_input == '':
                    continue
                
                # Process the command
                self.process_command(user_input)
                
            except KeyboardInterrupt:
                self.say("\n⚠️ Interrupted. Type 'exit' to quit.")
                continue
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                traceback.print_exc()
                continue

# ================== ENTRY POINT ==================
def main():
    """Entry point"""
    print("\n" + "=" * 70)
    print("🤖 ADVANCED AI ASSISTANT - STARTING...")
    print("=" * 70)
    
    try:
        assistant = AdvancedAssistant()
        assistant.run()
    except Exception as e:
        print(f"\n❌ FATAL ERROR DURING STARTUP: {e}")
        traceback.print_exc()
        print("\n⚠️ Try these fixes:")
        print("   1. Make sure Ollama is running: 'ollama serve'")
        print("   2. Check if model is downloaded: 'ollama pull gemma3:1b'")
        print("   3. Install missing packages: 'pip install -r requirements.txt'")
        print("   4. Check AutoBox folder exists at: ./AutoBox/")

if __name__ == "__main__":
    main()