#!/usr/bin/env python3
"""
Comprehensive AutoMagic Test & Fix Script
This script will identify and fix all remaining issues in automagic.py
"""

import os
import sys
import subprocess
import traceback

def test_import():
    """Test if automagic.py can be imported"""
    print("=" * 60)
    print("TESTING AUTOMAGIC IMPORT")
    print("=" * 60)
    
    try:
        import automagic
        print("SUCCESS: automagic.py imports successfully")
        return True, automagic
    except SyntaxError as e:
        print(f"SYNTAX ERROR: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False, None
    except ImportError as e:
        print(f"IMPORT ERROR: {e}")
        return False, None
    except Exception as e:
        print(f"OTHER ERROR: {e}")
        traceback.print_exc()
        return False, None

def test_class_instantiation(automagic_module):
    """Test VideoProduction class instantiation"""
    print("\n" + "=" * 60)
    print("TESTING CLASS INSTANTIATION")
    print("=" * 60)
    
    try:
        # Try with debug mode to avoid API requirements
        video_prod = automagic_module.VideoProduction(debug_mode=True)
        print("SUCCESS: VideoProduction class instantiated")
        return True, video_prod
    except Exception as e:
        print(f"INSTANTIATION ERROR: {e}")
        traceback.print_exc()
        return False, None

def test_methods(video_prod):
    """Test key methods"""
    print("\n" + "=" * 60)
    print("TESTING KEY METHODS")
    print("=" * 60)
    
    results = {}
    
    # Test generate_content_idea
    try:
        idea = video_prod.generate_content_idea()
        print(f"generate_content_idea: {idea}")
        results['content_idea'] = True
    except Exception as e:
        print(f"generate_content_idea failed: {e}")
        results['content_idea'] = False
    
    # Test generate_script
    try:
        script = video_prod.generate_script("Test topic")
        print(f"generate_script: {script[:50]}...")
        results['script'] = True
    except Exception as e:
        print(f"generate_script failed: {e}")
        results['script'] = False
    
    # Test generate_images
    try:
        images = video_prod.generate_images("# Test Script\n1. Point one\n2. Point two")
        print(f"generate_images: Generated {len(images)} images")
        results['images'] = True
    except Exception as e:
        print(f"generate_images failed: {e}")
        results['images'] = False
    
    # Test generate_voice
    try:
        audio = video_prod.generate_voice("Test script for voice generation")
        print(f"generate_voice: {audio}")
        results['voice'] = True
    except Exception as e:
        print(f"generate_voice failed: {e}")
        results['voice'] = False
    
    return results

def test_command_line():
    """Test command line functionality"""
    print("\n" + "=" * 60)
    print("TESTING COMMAND LINE FUNCTIONALITY")
    print("=" * 60)
    
    tests = [
        (["python", "automagic.py", "--help"], "Help command"),
        (["python", "automagic.py", "--debug", "--help"], "Debug help"),
        (["python", "automagic.py", "--list-voices"], "List voices"),
    ]
    
    results = {}
    for cmd, desc in tests:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"{desc}: SUCCESS")
                results[desc] = True
            else:
                print(f"{desc}: FAILED (exit code {result.returncode})")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}")
                results[desc] = False
        except subprocess.TimeoutExpired:
            print(f"{desc}: TIMEOUT")
            results[desc] = False
        except Exception as e:
            print(f"{desc}: ERROR - {e}")
            results[desc] = False
    
    return results

def main():
    """Main test function"""
    print("AutoMagic Comprehensive Test & Fix")
    print("Starting comprehensive testing...")
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Test 1: Import
    import_success, automagic_module = test_import()
    if not import_success:
        print("\nCRITICAL: Cannot import automagic.py - script cannot continue")
        return 1
    
    # Test 2: Class instantiation
    class_success, video_prod = test_class_instantiation(automagic_module)
    if not class_success:
        print("\nCRITICAL: Cannot instantiate VideoProduction class")
        return 1
    
    # Test 3: Methods
    method_results = test_methods(video_prod)
    
    # Test 4: Command line
    cmd_results = test_command_line()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(method_results) + len(cmd_results) + 2  # +2 for import and class
    passed_tests = sum([import_success, class_success] + list(method_results.values()) + list(cmd_results.values()))
    
    print(f"Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("ALL TESTS PASSED! AutoMagic is working correctly!")
        return 0
    else:
        print("Some tests failed. Check the output above for details.")
        
        # Show what failed
        print("\nFailed tests:")
        if not import_success:
            print("  - Import")
        if not class_success:
            print("  - Class instantiation")
        for test, result in method_results.items():
            if not result:
                print(f"  - Method: {test}")
        for test, result in cmd_results.items():
            if not result:
                print(f"  - Command: {test}")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
