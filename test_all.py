#!/usr/bin/env python3
"""
Comprehensive test for all AI Assistant capabilities
"""

import sys
import os
import time
import json
from datetime import datetime

# Add project root to path
sys.path.append('.')

def run_test(test_name, function, *args):
    """Run a single test and report result"""
    print(f"\n🧪 Testing: {test_name}")
    print("-" * 50)
    
    try:
        start = time.time()
        result = function(*args)
        elapsed = time.time() - start
        
        if result:
            print(f"✅ PASS ({elapsed:.2f}s)")
        else:
            print(f"❌ FAIL ({elapsed:.2f}s)")
        
        return result
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_operations():
    """Test file executor"""
    from executors.file_exec import FileExecutor
    
    fe = FileExecutor()
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Create file
    total_tests += 1
    if run_test("Create file", fe.create_file, "AB1/test_file.txt", "Test content"):
        tests_passed += 1
    
    # Test 2: Read file
    total_tests += 1
    if run_test("Read file", fe.read_file, "AB1/test_file.txt"):
        tests_passed += 1
    
    # Test 3: Write file
    total_tests += 1
    if run_test("Write file", fe.write_file, "AB1/test_file.txt", "Updated content"):
        tests_passed += 1
    
    # Test 4: Move file
    total_tests += 1
    if run_test("Move file", fe.move_file, "AB1/test_file.txt", "AB2"):
        tests_passed += 1
    
    # Test 5: Delete file
    total_tests += 1
    if run_test("Delete file", fe.delete_file, "AB2/test_file.txt"):
        tests_passed += 1
    
    print(f"\n📁 File Operations: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def test_web_operations():
    """Test web executor"""
    from executors.web_exec import WebExecutor
    
    we = WebExecutor()
    tests_passed = 0
    total_tests = 0
    
    try:
        # Test 1: Extract content (lightweight)
        total_tests += 1
        content = run_test("Extract web content", we.extract_content, "http://example.com")
        if content and "Example Domain" in content:
            tests_passed += 1
            print(f"   Extracted: {len(content)} characters")
    
    finally:
        we.close()
    
    print(f"\n🌐 Web Operations: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def test_clipboard():
    """Test clipboard executor"""
    from executors.clipboard_exec import ClipboardExecutor
    
    cb = ClipboardExecutor()
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Copy text
    total_tests += 1
    if run_test("Copy to clipboard", cb.copy, "Test clipboard content"):
        tests_passed += 1
    
    # Test 2: Paste text
    total_tests += 1
    content = run_test("Paste from clipboard", cb.paste)
    if content == "Test clipboard content":
        tests_passed += 1
    
    print(f"\n📋 Clipboard: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def test_llm_intent():
    """Test LLM intent generation"""
    from controller.llm import AdvancedLLM
    
    llm = AdvancedLLM("gemma:4b")
    tests_passed = 0
    total_tests = 0
    
    test_commands = [
        "create a file called notes.txt in AB1",
        "open google.com in browser",
        "search for artificial intelligence news"
    ]
    
    for cmd in test_commands:
        total_tests += 1
        print(f"\nTesting: '{cmd}'")
        intent = run_test("Generate intent", llm.get_intent, cmd)
        
        if intent and isinstance(intent, dict) and "steps" in intent:
            print(f"   Steps: {len(intent['steps'])}")
            tests_passed += 1
    
    print(f"\n🤖 LLM Intent: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def test_full_integration():
    """Test complete assistant pipeline"""
    print("\n🔗 Testing Full Integration")
    print("=" * 50)
    
    # Create a simple test command
    test_command = "create a test file and write hello world to it"
    
    from controller.llm import AdvancedLLM
    from executors.file_exec import FileExecutor
    
    llm = AdvancedLLM()
    fe = FileExecutor()
    
    # Get intent
    intent = llm.get_intent(test_command)
    print(f"Generated intent: {json.dumps(intent, indent=2)}")
    
    # Execute
    if intent.get("steps"):
        for step in intent["steps"]:
            action = step.get("action")
            target = step.get("target")
            content = step.get("content")
            
            if action == "file_create":
                fe.create_file(target, content)
            elif action == "file_write":
                fe.write_file(target, content)
    
    # Verify
    check_file = "AB1/test.txt"  # Adjust based on actual output
    content = fe.read_file(check_file)
    
    if content and "hello world" in content.lower():
        print("✅ Full integration test passed")
        return True
    else:
        print("❌ Full integration test failed")
        return False

def main():
    """Run all tests"""
    print("🚀 AI ASSISTANT COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    all_passed = True
    test_results = {}
    
    # Run component tests
    print("\n1. Testing File Operations...")
    test_results["file_ops"] = test_file_operations()
    all_passed &= test_results["file_ops"]
    
    print("\n2. Testing Web Operations...")
    test_results["web_ops"] = test_web_operations()
    all_passed &= test_results["web_ops"]
    
    print("\n3. Testing Clipboard...")
    test_results["clipboard"] = test_clipboard()
    all_passed &= test_results["clipboard"]
    
    print("\n4. Testing LLM Intent Generation...")
    test_results["llm"] = test_llm_intent()
    all_passed &= test_results["llm"]
    
    print("\n5. Testing Full Integration...")
    test_results["integration"] = test_full_integration()
    all_passed &= test_results["integration"]
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Assistant is ready.")
    else:
        print("⚠️  SOME TESTS FAILED. Check above for details.")
    
    # Save results
    results_file = "test_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "all_passed": all_passed,
            "results": test_results
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())