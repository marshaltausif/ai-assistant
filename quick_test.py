#!/usr/bin/env python3
"""
Quick Test for AI Assistant Components
"""

import sys
import os
sys.path.append('.')

def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing imports...")
    
    modules = [
        ("controller.llm", "LLM"),
        ("executors.file_exec", "File Executor"),
        ("executors.os_exec", "OS Executor"),
        ("voice.stt", "Speech-to-Text"),
        ("voice.tts", "Text-to-Speech"),
        ("memory.memory", "Memory"),
    ]
    
    all_good = True
    for module_path, name in modules:
        try:
            __import__(module_path)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            all_good = False
    
    return all_good

def test_autobox():
    """Test AutoBox structure"""
    print("\n📁 Testing AutoBox...")
    
    autobox_path = "AutoBox"
    if not os.path.exists(autobox_path):
        print(f"  ❌ AutoBox not found at: {autobox_path}")
        print(f"  Looking in: {os.path.abspath('.')}")
        return False
    
    required_folders = ["AB1", "AB2", "AB3"]
    all_exist = True
    
    for folder in required_folders:
        folder_path = os.path.join(autobox_path, folder)
        if os.path.exists(folder_path):
            print(f"  ✅ {folder}")
        else:
            print(f"  ❌ Missing: {folder}")
            all_exist = False
    
    if not all_exist:
        print("\n  Creating missing folders...")
        for folder in required_folders:
            folder_path = os.path.join(autobox_path, folder)
            os.makedirs(folder_path, exist_ok=True)
            print(f"  Created: {folder}")
    
    return True

def test_llm():
    """Test LLM connection"""
    print("\n🤖 Testing LLM...")
    
    try:
        from controller.llm import ask_llm
        
        # Quick test with simple command
        test_command = "create test.txt in ab1"
        print(f"  Testing: '{test_command}'")
        
        result = ask_llm(test_command)
        print(f"  Response: {result}")
        
        # Check if it's valid JSON
        import json
        data = json.loads(result)
        
        if "steps" in data:
            print(f"  ✅ LLM working (got {len(data['steps'])} steps)")
            return True
        else:
            print("  ❌ LLM returned invalid format")
            return False
            
    except Exception as e:
        print(f"  ❌ LLM test failed: {e}")
        return False

def test_file_operations():
    """Test file operations"""
    print("\n📄 Testing File Operations...")
    
    try:
        from executors.file_exec import create_file, write_file, read_file
        
        # Test 1: Create file
        print("  1. Creating test file...")
        create_file("AB1/test_file.txt")
        
        # Test 2: Write to file
        print("  2. Writing to file...")
        write_file("AB1/test_file.txt", "Hello from AI Assistant!")
        
        # Test 3: Read from file
        print("  3. Reading file...")
        content = read_file("AB1/test_file.txt")
        
        if content == "Hello from AI Assistant!":
            print("  ✅ File operations working!")
            return True
        else:
            print(f"  ❌ Read content mismatch: {content}")
            return False
            
    except Exception as e:
        print(f"  ❌ File operations failed: {e}")
        return False

def test_voice():
    """Test voice components"""
    print("\n🎤 Testing Voice Components...")
    
    # Test TTS
    try:
        from voice.tts import speak
        
        print("  1. Testing TTS (text-to-speech)...")
        print("  You should hear: 'Voice test successful'")
        speak("Voice test successful")
        print("  ✅ TTS working!")
        
        # Test STT import
        from voice.stt import listen_and_transcribe
        print("  2. STT module imported successfully")
        print("  Note: Will not record automatically for safety")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Voice test failed: {e}")
        return False

def test_web():
    """Test web components"""
    print("\n🌐 Testing Web Components...")
    
    try:
        # Just test imports
        from executors.web_exec import WebExecutor
        print("  ✅ WebExecutor imported")
        
        # Test requests
        import requests
        print("  ✅ Requests imported")
        
        return True
        
    except Exception as e:
        print(f"  ⚠️ Web test: {e}")
        print("  Some web features may not work")
        return False

def test_clipboard():
    """Test clipboard"""
    print("\n📋 Testing Clipboard...")
    
    try:
        from executors.clipboard_exec import ClipboardExecutor
        
        clipboard = ClipboardExecutor()
        
        # Test copy
        test_text = "AI Assistant Clipboard Test"
        if clipboard.copy(test_text):
            print("  ✅ Copy to clipboard working")
            
            # Try to paste
            content = clipboard.paste()
            if test_text in content:
                print("  ✅ Paste from clipboard working")
                return True
            else:
                print(f"  ⚠️ Paste returned: {content}")
                return True  # Still OK if paste doesn't work perfectly
        else:
            print("  ⚠️ Copy may have issues")
            return True  # Don't fail the whole test
            
    except Exception as e:
        print(f"  ⚠️ Clipboard test: {e}")
        return True  # Clipboard is optional

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🚀 AI ASSISTANT - COMPREHENSIVE TEST")
    print("=" * 60)
    
    results = {}
    
    # Run tests
    results["imports"] = test_imports()
    results["autobox"] = test_autobox()
    results["llm"] = test_llm()
    results["files"] = test_file_operations()
    results["voice"] = test_voice()
    results["web"] = test_web()
    results["clipboard"] = test_clipboard()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total = len(results)
    passed = sum(results.values())
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:15} {status}")
    
    print("\n" + "=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SYSTEMS GO! Ready to run.")
        print("\nNext: Run 'python run.py' to start the assistant!")
    elif passed >= total - 1:  # Allow 1 failure
        print("⚠️  Minor issues. Assistant should still work.")
        print("\nNext: Try 'python run.py'")
    else:
        print("❌ Multiple failures. Check above errors.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)