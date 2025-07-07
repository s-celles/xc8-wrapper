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


def safe_print(text):
    """Print text safely, handling encoding issues"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback to ASCII-safe output
        safe_text = text.encode("ascii", errors="replace").decode("ascii")
        print(safe_text)


def main():
    """Run platform diagnostics"""
    safe_print("=" * 60)
    safe_print("PLATFORM DIAGNOSTICS")
    safe_print("=" * 60)

    # Python information
    safe_print("\n--- Python Information ---")
    safe_print(f"Python version: {sys.version}")
    safe_print(f"Python executable: {sys.executable}")
    safe_print(f"Python platform: {sys.platform}")
    safe_print(f"Default encoding: {sys.getdefaultencoding()}")
    safe_print(f"File system encoding: {sys.getfilesystemencoding()}")

    # Platform information
    safe_print("\n--- Platform Information ---")
    safe_print(f"Platform: {platform.platform()}")
    safe_print(f"System: {platform.system()}")
    safe_print(f"Machine: {platform.machine()}")
    safe_print(f"Architecture: {platform.architecture()}")

    # Locale information
    safe_print("\n--- Locale Information ---")
    try:
        safe_print(f"Default locale: {locale.getdefaultlocale()}")
        safe_print(f"Preferred encoding: {locale.getpreferredencoding()}")
    except Exception as e:
        safe_print(f"Error getting locale: {e}")

    # Environment variables
    safe_print("\n--- Environment Variables ---")
    env_vars = [
        "PYTHONIOENCODING",
        "PYTHONLEGACYWINDOWSSTDIO",
        "LC_ALL",
        "LANG",
        "LANGUAGE",
        "PATH",
    ]
    for var in env_vars:
        value = os.environ.get(var, "Not set")
        safe_print(f"{var}: {value}")

    # Path information
    safe_print("\n--- Path Information ---")
    safe_print(f"Current working directory: {Path.cwd()}")
    safe_print(f"Script location: {Path(__file__).parent}")

    # Package imports
    safe_print("\n--- Package Import Test ---")
    try:
        import xc8_wrapper

        safe_print("[OK] xc8_wrapper imported successfully")
        version = getattr(xc8_wrapper, "__version__", "Unknown")
        safe_print(f"   Version: {version}")
        safe_print(f"   Location: {xc8_wrapper.__file__}")
    except Exception as e:
        safe_print(f"[FAIL] Failed to import xc8_wrapper: {e}")

    # Dependencies
    safe_print("\n--- Dependencies Test ---")
    deps = ["colorama", "pytest", "black", "flake8", "mypy"]
    for dep in deps:
        try:
            __import__(dep)
            safe_print(f"[OK] {dep} imported successfully")
        except ImportError as e:
            safe_print(f"[FAIL] Failed to import {dep}: {e}")

    # File operations test
    safe_print("\n--- File Operations Test ---")
    try:
        test_file = Path("test_encoding.txt")
        test_content = "Hello, World! Testing Unicode and encoding"

        # Test writing
        test_file.write_text(test_content, encoding="utf-8")
        safe_print("[OK] UTF-8 file write successful")

        # Test reading
        read_content = test_file.read_text(encoding="utf-8")
        if read_content == test_content:
            safe_print("[OK] UTF-8 file read successful")
        else:
            safe_print("[FAIL] UTF-8 file read mismatch")

        # Cleanup
        test_file.unlink()

    except Exception as e:
        safe_print(f"[FAIL] File operations failed: {e}")

    safe_print("\n" + "=" * 60)
    safe_print("DIAGNOSTICS COMPLETE")
    safe_print("=" * 60)


if __name__ == "__main__":
    main()
