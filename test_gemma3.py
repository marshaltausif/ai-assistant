import subprocess
import json

print("🧪 Testing gemma3:1b...")

# Test 1: Direct Ollama test
print("\n1. Testing direct Ollama command...")
try:
    result = subprocess.run(
        ["ollama", "run", "gemma3:1b", "hello"],
        capture_output=True,
        text=True,
        timeout=10
    )
    print(f"✅ Ollama response: {result.stdout[:100]}...")
except Exception as e:
    print(f"❌ Ollama test failed: {e}")

# Test 2: JSON conversion
print("\n2. Testing JSON conversion...")
test_prompt = '''Convert to JSON: "create hello.txt in ab2"

Output:'''
try:
    result = subprocess.run(
        ["ollama", "run", "gemma3:1b"],
        input=test_prompt,
        capture_output=True,
        text=True,
        timeout=15
    )
    output = result.stdout.strip()
    print(f"Raw output: {output}")
    
    # Try to parse
    import re
    json_match = re.search(r'\{.*\}', output, re.DOTALL)
    if json_match:
        print(f"✅ Found JSON: {json_match.group()[:100]}...")
    else:
        print("⚠️ No JSON found in output")
        
except Exception as e:
    print(f"❌ JSON test failed: {e}")

# Test 3: Memory check
print("\n3. Checking memory...")
import psutil
memory = psutil.virtual_memory()
print(f"Total RAM: {memory.total / 1024**3:.1f} GB")
print(f"Available: {memory.available / 1024**3:.1f} GB")
print(f"Used: {memory.percent}%")

print("\n✅ gemma3:1b test complete!")