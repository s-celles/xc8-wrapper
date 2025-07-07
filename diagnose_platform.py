#!/usr/bin/env python3
"""
Platform diagnostic script

This script helps diagnose platform-specific issues that might affect CI.
"""

import locale
import os
import platform
import sys
from pathlib import Path


def main():
    """Run platform diagnostics"""
    print("=" * 60)
    print("PLATFORM DIAGNOSTICS")
    print("=" * 60)

    # Python information
    print("\n--- Python Information ---")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Python platform: {sys.platform}")
    print(f"Default encoding: {sys.getdefaultencoding()}")
    print(f"File system encoding: {sys.getfilesystemencoding()}")

    # Platform information
    print("\n--- Platform Information ---")
    print(f"Platform: {platform.platform()}")
    print(f"System: {platform.system()}")
    print(f"Machine: {platform.machine()}")
    print(f"Architecture: {platform.architecture()}")

    # Locale information
    print("\n--- Locale Information ---")
    try:
        print(f"Default locale: {locale.getdefaultlocale()}")
        print(f"Preferred encoding: {locale.getpreferredencoding()}")
    except Exception as e:
        print(f"Error getting locale: {e}")

    # Environment variables
    print("\n--- Environment Variables ---")
    env_vars = ["PYTHONIOENCODING", "PYTHONLEGACYWINDOWSSTDIO", "LC_ALL", "LANG", "LANGUAGE", "PATH"]
    for var in env_vars:
        value = os.environ.get(var, "Not set")
        print(f"{var}: {value}")

    # Path information
    print("\n--- Path Information ---")
    print(f"Current working directory: {Path.cwd()}")
    print(f"Script location: {Path(__file__).parent}")  # Package imports
    print("\n--- Package Import Test ---")
    try:
        import xc8_wrapper

        print("✅ xc8_wrapper imported successfully")
        version = getattr(xc8_wrapper, "__version__", "Unknown")
        print(f"   Version: {version}")
        print(f"   Location: {xc8_wrapper.__file__}")
    except Exception as e:
        print(f"❌ Failed to import xc8_wrapper: {e}")

    # Dependencies
    print("\n--- Dependencies Test ---")
    deps = ["colorama", "pytest", "black", "flake8", "mypy"]
    for dep in deps:
        try:
            __import__(dep)
            print(f"✅ {dep} imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import {dep}: {e}")

    # File operations test
    print("\n--- File Operations Test ---")
    try:
        test_file = Path("test_encoding.txt")
        test_content = "Hello, 世界! 🌍 Testing Unicode"

        # Test writing
        test_file.write_text(test_content, encoding="utf-8")
        print("✅ UTF-8 file write successful")

        # Test reading
        read_content = test_file.read_text(encoding="utf-8")
        if read_content == test_content:
            print("✅ UTF-8 file read successful")
        else:
            print("❌ UTF-8 file read mismatch")

        # Cleanup
        test_file.unlink()

    except Exception as e:
        print(f"❌ File operations failed: {e}")

    print("\n" + "=" * 60)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
