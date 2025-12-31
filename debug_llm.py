import sys
sys.path.append('.')

print("🧪 Testing LLM only...")

from controller.llm import ask_llm

test_commands = [
    "create hello.txt in ab1",
    "open google.com",
    "write test to file.txt",
    "read notes.txt",
    "open notepad",
]

for cmd in test_commands:
    print(f"\n{'='*50}")
    print(f"Testing: '{cmd}'")
    result = ask_llm(cmd)
    print(f"Result: {result}")
    
    # Try to parse
    import json
    try:
        data = json.loads(result)
        if data.get("steps"):
            print(f"✅ SUCCESS: {len(data['steps'])} steps")
            for step in data["steps"]:
                print(f"   Action: {step.get('action')}, Target: {step.get('target')}")
        else:
            print("❌ FAILED: Empty steps")
    except:
        print("❌ FAILED: Invalid JSON")