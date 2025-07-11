#!/usr/bin/env python3
"""
Quick test runner for development

Run this script to quickly test the package during development.
"""

import os
import subprocess  # nosec B404
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    # Set environment variables to fix encoding issues on Windows
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONLEGACYWINDOWSSTDIO"] = "1"

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            encoding="utf-8",
            errors="replace",
        )  # nosec B603
    except UnicodeDecodeError:
        # Fallback to running without capture if encoding fails
        result = subprocess.run(cmd, env=env)  # nosec B603
        return result.returncode == 0

    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        if result.stdout:
            print("STDOUT:", result.stdout)
    else:
        print(f"❌ {description} - FAILED")
        if result.stdout:
            print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

    return result.returncode == 0


def main():
    """Run quick tests"""
    print("XC8 Wrapper - Quick Test Runner")
    print("=" * 60)

    # Change to project directory
    os.chdir(Path(__file__).parent)

    # List of tests to run
    tests = [
        (["python", "-m", "pytest", "tests/", "-v"], "Unit Tests"),
        (
            [
                "python",
                "-m",
                "pytest",
                "tests/",
                "--cov=xc8_wrapper",
                "--cov-report=term-missing",
            ],
            "Coverage Test",
        ),
        (
            ["python", "-c", "import xc8_wrapper; print('Import successful')"],
            "Import Test",
        ),
        (["python", "demo.py"], "Demo Script"),
        (
            ["python", "-m", "flake8", "xc8_wrapper", "--count", "--statistics"],
            "Linting",
        ),
        (["python", "-m", "black", "--check", "xc8_wrapper"], "Code Formatting Check"),
        (
            ["python", "-m", "mypy", "xc8_wrapper", "--ignore-missing-imports"],
            "Type Checking",
        ),
    ]

    results = []

    for cmd, description in tests:
        try:
            success = run_command(cmd, description)
            results.append((description, success))
        except Exception as e:
            print(f"❌ {description} - ERROR: {e}")
            results.append((description, False))

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{description:<30} {status}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
