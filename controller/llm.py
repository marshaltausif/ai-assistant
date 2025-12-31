import subprocess
import json
import re
import os

MODEL = "gemma3:1b"

def load_prompt():
    """Load the prompt from prompt.txt file"""
    prompt_file = os.path.join(os.path.dirname(__file__), "prompt.txt")
    if os.path.exists(prompt_file):
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    # Fallback prompt
    return """You are a local AI assistant running on a user's computer.

Your job is to understand the user's request, internally plan the required steps,
and output ONLY the final executable intent in structured JSON.

IMPORTANT:
- You may think and plan internally.
- You must NOT reveal your reasoning.
- You must output ONLY valid JSON.
- No explanations, no extra text.
- If the user specifies a storage location (folder name or alias),
  you MUST include a move_file step to that location.

If the task requires multiple steps, break it into ordered steps.
If the task is unclear, use action "none".

ALLOWED ACTIONS:
open_app
close_app
open_url
create_file
write_file
read_file
move_file
search_web
schedule_event
delete_file
none

JSON FORMAT:
{
  "steps": [
    {
      "action": "<allowed_action>",
      "target": "<string or null>",
      "content": "<string or null>"
    }
  ]
}

RULES:
1. All files must be in AutoBox folders: AB1, AB2, AB3
2. Folder aliases: ab1/a1/av1 → AB1, ab2/a2/av2 → AB2, ab3/a3/av3 → AB3
3. For create_file: if content is list, convert to comma-separated string
4. For greetings (hello, hi, how are you), use action: "none"
5. For questions, use action: "none"

EXAMPLES:
User: "create hello.txt in ab2"
Output: {"steps": [{"action": "create_file", "target": "AB2/hello.txt", "content": null}]}

User: "write 'test content' to file.txt"
Output: {"steps": [{"action": "write_file", "target": "file.txt", "content": "test content"}]}

User: "hello how are you"
Output: {"steps": [{"action": "none", "target": null, "content": null}]}

User: "open google.com"
Output: {"steps": [{"action": "open_url", "target": "https://google.com", "content": null}]}

User: "search for AI news"
Output: {"steps": [{"action": "search_web", "target": "AI news", "content": null}]}

Now process this command:"""

def ask_llm(user_input: str) -> str:
    """
    Convert natural language command to JSON intent using local LLM.
    """
    # Load and prepare prompt
    base_prompt = load_prompt()
    full_prompt = f"{base_prompt}\n\nUser: \"{user_input}\"\nOutput:"
    
    print(f"🤖 Processing: {user_input[:50]}...")
    
    try:
        # Run Ollama
        result = subprocess.run(
            ["ollama", "run", MODEL],
            input=full_prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=20
        )
        
        output = result.stdout.strip()
        
        # Debug
        print(f"📥 Raw LLM output ({len(output)} chars): {output[:100]}...")
        
        # Clean the output
        cleaned = output.strip()
        
        # Remove markdown code blocks
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
                return json.dumps(data, ensure_ascii=False)
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
                    return json.dumps(data, ensure_ascii=False)
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
    """Fallback parser when LLM fails"""
    print(f"🔄 Using fallback parser for: {user_input}")
    
    text = user_input.lower().strip()
    
    # Check for greetings/chat
    greetings = ["hello", "hi", "hey", "how are you", "what's up", "good morning", "good evening"]
    for greeting in greetings:
        if greeting in text:
            return json.dumps({"steps": [{"action": "none", "target": None, "content": None}]})
    
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
    
    # OPEN URL
    elif "open" in text and ("http" in text or "www" in text or ".com" in text):
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
    
    # OPEN APP
    elif "open" in text:
        app = user_input.replace("open", "").strip()
        return json.dumps({
            "steps": [{
                "action": "open_app",
                "target": app,
                "content": None
            }]
        })
    
    # SEARCH
    elif "search" in text:
        query = user_input.replace("search", "").replace("for", "").strip()
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
    
    # DELETE
    elif "delete" in text or "remove" in text:
        target = text.replace("delete", "").replace("remove", "").strip()
        return json.dumps({
            "steps": [{
                "action": "delete_file",
                "target": target,
                "content": None
            }]
        })
    
    # Default: none action for chat
    return json.dumps({"steps": [{"action": "none", "target": None, "content": None}]})