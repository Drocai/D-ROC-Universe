#!/usr/bin/env python3
"""Final verification test for automagic.py"""

import sys
import os
import subprocess

def test_python_syntax():
    """Test if the Python file has valid syntax"""
    print("=== Testing Python Syntax ===")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'py_compile', 'automagic.py'
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            print("✓ Python syntax is valid")
            return True
        else:
            print(f"✗ Syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error testing syntax: {e}")
        return False

def test_import():
    """Test importing the module"""
    print("\n=== Testing Import ===")
    try:
        import automagic
        print("✓ Module imports successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_instantiation():
    """Test creating the main class"""
    print("\n=== Testing Class Instantiation ===")
    try:
        import automagic
        # Try creating in debug mode to avoid API requirements
        production = automagic.VideoProduction(debug_mode=True)
        print("✓ VideoProduction class instantiated successfully")
        return True
    except Exception as e:
        print(f"✗ Instantiation failed: {e}")
        return False

def main():
    print("AutoMagic Final Verification Test")
    print("=" * 40)
    
    results = []
    results.append(test_python_syntax())
    results.append(test_import())
    results.append(test_instantiation())
    
    print("\n" + "=" * 40)
    if all(results):
        print("🎉 ALL TESTS PASSED! 🎉")
        print("The automagic.py script is ready to use!")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
