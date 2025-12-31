#!/usr/bin/env python3
"""
AI Assistant - WORKING VERSION
"""

import sys
import os
import json
sys.path.append('.')

print("🤖 Starting AI Assistant...")

# Import components
try:
    from controller.llm import ask_llm
    print("✅ LLM loaded")
except:
    print("⚠️ LLM import failed, using fallback")
    # Fallback function
    def ask_llm(user_input):
        user_input = user_input.lower()
        
        # Simple pattern matching
        if "create" in user_input and ".txt" in user_input:
            if "ab1" in user_input or "a1" in user_input:
                folder = "AB1"
            elif "ab2" in user_input or "a2" in user_input:
                folder = "AB2"
            elif "ab3" in user_input or "a3" in user_input:
                folder = "AB3"
            else:
                folder = "AB1"  # default
            
            # Extract filename
            import re
            match = re.search(r'(\w+\.\w+)', user_input)
            if match:
                filename = match.group(1)
                return json.dumps({
                    "steps": [{
                        "action": "create_file",
                        "target": f"{folder}/{filename}",
                        "content": None
                    }]
                })
        
        elif "write" in user_input and " to " in user_input:
            parts = user_input.split(" to ")
            if len(parts) == 2:
                content = parts[0].replace("write", "").strip().strip('"\'')
                target = parts[1].strip()
                return json.dumps({
                    "steps": [{
                        "action": "write_file",
                        "target": target,
                        "content": content
                    }]
                })
        
        elif "read" in user_input:
            target = user_input.replace("read", "").strip()
            return json.dumps({
                "steps": [{
                    "action": "read_file",
                    "target": target,
                    "content": None
                }]
            })
        
        elif "open" in user_input:
            if "http" in user_input or "www" in user_input or ".com" in user_input:
                import re
                url_match = re.search(r'(https?://\S+|www\.\S+)', user_input)
                if url_match:
                    url = url_match.group(1)
                    if not url.startswith("http"):
                        url = "https://" + url
                    return json.dumps({
                        "steps": [{
                            "action": "open_url",
                            "target": url,
                            "content": None
                        }]
                    })
            else:
                app = user_input.replace("open", "").strip()
                return json.dumps({
                    "steps": [{
                        "action": "open_app",
                        "target": app,
                        "content": None
                    }]
                })
        
        # Default
        return '{"steps": []}'

# Import other components
from executors.file_exec import create_file, write_file, read_file, move_file
from executors.os_exec import open_app
from voice.tts import speak
from voice.stt import listen_and_transcribe

print("✅ All components loaded")
print("\n" + "="*50)
print("🤖 AI ASSISTANT READY")
print("="*50)

speak("AI Assistant ready!")

while True:
    try:
        print("\n💬 Type command, 'v' for voice, or 'exit':")
        user_input = input(">> ").strip()
        
        if user_input.lower() == 'exit':
            speak("Goodbye!")
            break
        
        if user_input.lower() == 'v':
            speak("Listening...")
            user_input = listen_and_transcribe()
            print(f"🎤 You said: {user_input}")
        
        if not user_input:
            continue
        
        print("🔄 Processing...")
        speak("Processing")
        
        # Get intent from LLM
        json_response = ask_llm(user_input)
        print(f"📄 LLM Response: {json_response}")
        
        try:
            data = json.loads(json_response)
            steps = data.get("steps", [])
            
            if not steps:
                speak("I didn't understand that command")
                print("⚠️ No steps in response")
                continue
            
            # Execute each step
            for step in steps:
                action = step.get("action")
                target = step.get("target", "")
                content = step.get("content", "")
                
                print(f"⚡ Executing: {action} -> {target}")
                
                if action == "create_file":
                    create_file(target, content)
                    speak(f"Created {target}")
                
                elif action == "write_file":
                    write_file(target, content)
                    speak(f"Wrote to {target}")
                
                elif action == "read_file":
                    result = read_file(target)
                    if result:
                        speak(f"File says: {result[:50]}...")
                        print(f"📖 Content: {result}")
                    else:
                        speak("File not found")
                
                elif action == "move_file":
                    move_file(target, content)
                    speak(f"Moved to {content}")
                
                elif action == "open_app":
                    open_app(target)
                    speak(f"Opening {target}")
                
                elif action == "open_url":
                    print(f"🌐 Would open: {target}")
                    speak(f"Opening {target}")
                    # If you have web_exec installed:
                    try:
                        from executors.web_exec import WebExecutor
                        web = WebExecutor()
                        web.open_url(target)
                        web.close()
                    except:
                        print("⚠️ Web features not available")
                
                else:
                    speak(f"Unknown action: {action}")
            
            speak("Task completed!")
            
        except json.JSONDecodeError:
            speak("Sorry, I couldn't process that command")
            print("❌ Invalid JSON from LLM")
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        speak("Goodbye")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
        speak("An error occurred")

print("\nAssistant shutdown complete.")