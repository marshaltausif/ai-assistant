import subprocess
import json
import re
import time

MODEL = "gemma3:1b"  # ✅ Updated to correct name

def ask_llm(user_input: str) -> str:
    """
    Convert natural language to JSON using gemma3:1b
    """
    # SIMPLE prompt for small model
    prompt = f"""User command: {user_input}

Convert this command to executable JSON. Available actions: create_file, write_file, read_file, open_app, open_url.

Rules:
- Files go in AB1, AB2, or AB3 folders
- ab1 = AB1, ab2 = AB2, ab3 = AB3
- Output ONLY JSON, no other text

Examples:
Command: "create notes.txt in ab2"
Output: {{"steps": [{{"action": "create_file", "target": "AB2/notes.txt", "content": null}}]}}

Command: "open google.com"
Output: {{"steps": [{{"action": "open_url", "target": "https://google.com", "content": null}}]}}

Now convert this command:
Command: "{user_input}"
Output:"""
    
    try:
        print(f"🤖 Sending to {MODEL}: {user_input[:50]}...")
        
        # Run Ollama
        result = subprocess.run(
            ["ollama", "run", MODEL],
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=20  # Give it more time
        )
        
        output = result.stdout.strip()
        
        # Debug output
        print(f"📥 Raw response ({len(output)} chars): {output[:200]}...")
        
        if not output:
            print("⚠️ Empty response from LLM")
            return fallback_parser(user_input)
        
        # Clean the output
        cleaned = output.strip()
        
        # Remove markdown if present
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        
        # Try to parse as JSON
        try:
            data = json.loads(cleaned)
            if isinstance(data, dict) and "steps" in data:
                print(f"✅ Valid JSON with {len(data['steps'])} steps")
                return json.dumps(data)
        except json.JSONDecodeError:
            # Try to find JSON in the text
            pass
        
        # Search for JSON pattern
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                data = json.loads(json_str)
                if isinstance(data, dict) and "steps" in data:
                    print(f"✅ Found JSON in text: {len(data['steps'])} steps")
                    return json.dumps(data)
            except json.JSONDecodeError:
                pass
        
        # If no valid JSON, use fallback
        print("⚠️ No valid JSON found, using fallback parser")
        return fallback_parser(user_input)
        
    except subprocess.TimeoutExpired:
        print("⏰ LLM timeout after 20 seconds")
        return fallback_parser(user_input)
    except FileNotFoundError:
        print("❌ Ollama not found. Make sure it's installed and running")
        return fallback_parser(user_input)
    except Exception as e:
        print(f"❌ LLM error: {e}")
        return fallback_parser(user_input)

def fallback_parser(user_input: str) -> str:
    """Fallback when LLM fails"""
    print(f"🔄 Using fallback parser for: {user_input}")
    
    text = user_input.lower().strip()
    
    # CREATE FILE
    if "create" in text or "make" in text:
        # Find filename
        import re
        filename_match = re.search(r'(\w+\.\w+)', user_input)
        if filename_match:
            filename = filename_match.group(1)
        else:
            # Create a default filename
            import time
            filename = f"file_{int(time.time())}.txt"
        
        # Find folder
        folder = "AB1"  # default
        if "ab2" in text or "a2" in text:
            folder = "AB2"
        elif "ab3" in text or "a3" in text:
            folder = "AB3"
        
        return json.dumps({
            "steps": [{
                "action": "create_file",
                "target": f"{folder}/{filename}",
                "content": None
            }]
        })
    
    # WRITE FILE
    elif "write" in text:
        # Try pattern: write "content" to file.txt
        import re
        pattern1 = re.search(r'write\s+"([^"]+)"\s+to\s+(\S+)', text)
        if pattern1:
            content = pattern1.group(1)
            target = pattern1.group(2)
        elif " to " in text:
            # Pattern: write content to file.txt
            parts = text.split(" to ")
            if len(parts) == 2:
                content = parts[0].replace("write", "").strip().strip('"\'')
                target = parts[1].strip()
            else:
                content = "text"
                target = "file.txt"
        else:
            content = "text"
            target = "file.txt"
        
        return json.dumps({
            "steps": [{
                "action": "write_file",
                "target": target,
                "content": content
            }]
        })
    
    # READ FILE
    elif "read" in text:
        target = text.replace("read", "").strip()
        if not target.endswith(('.txt', '.py', '.json')):
            target += ".txt"
        
        return json.dumps({
            "steps": [{
                "action": "read_file",
                "target": target,
                "content": None
            }]
        })
    
    # OPEN
    elif "open" in text:
        thing = text.replace("open", "").strip()
        
        # Check if it's a URL
        if "http" in thing or "www" in thing or ".com" in thing:
            if not thing.startswith("http"):
                thing = "https://" + thing
            return json.dumps({
                "steps": [{
                    "action": "open_url",
                    "target": thing,
                    "content": None
                }]
            })
        # It's an app
        else:
            return json.dumps({
                "steps": [{
                    "action": "open_app",
                    "target": thing,
                    "content": None
                }]
            })
    
    # SEARCH
    elif "search" in text:
        query = text.replace("search", "").replace("for", "").strip()
        return json.dumps({
            "steps": [{
                "action": "search_web",
                "target": query,
                "content": None
            }]
        })
    
    # MOVE
    elif "move" in text and " to " in text:
        parts = text.split(" to ")
        if len(parts) == 2:
            source = parts[0].replace("move", "").strip()
            destination = parts[1].strip()
            return json.dumps({
                "steps": [{
                    "action": "move_file",
                    "target": source,
                    "content": destination
                }]
            })
    
    # Default empty response
    return json.dumps({"steps": []})