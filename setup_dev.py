#!/usr/bin/env python3
"""
Development setup script for XC8 Wrapper

This script sets up the development environment for the XC8 wrapper project.
"""

import os
import subprocess  # nosec B404
import sys
from pathlib import Path


# Color codes for output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_colored(text: str, color: str) -> None:
    """Print colored text"""
    print(f"{color}{text}{Colors.END}")


def run_command(cmd: list[str], description: str, check: bool = True) -> bool:
    """Run a command and report results"""
    print_colored(f"🔧 {description}...", Colors.BLUE)
    print(f"   Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)  # nosec B603
        if result.returncode == 0:
            print_colored(f"✅ {description} - Success", Colors.GREEN)
            return True
        else:
            print_colored(f"❌ {description} - Failed", Colors.RED)
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ {description} - Failed", Colors.RED)
        print(f"   Error: {e}")
        return False
    except FileNotFoundError:
        print_colored(f"❌ {description} - Command not found", Colors.RED)
        return False


def check_python_version() -> bool:
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major != 3 or version.minor < 9:
        print_colored("❌ Python 3.9+ is required", Colors.RED)
        return False
    print_colored(
        f"✅ Python {version.major}.{version.minor} is compatible", Colors.GREEN
    )
    return True


def check_git() -> bool:
    """Check if git is available"""
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)  # nosec B603 B607
        if result.returncode == 0:
            print_colored("✅ Git is available", Colors.GREEN)
            return True
        else:
            print_colored("❌ Git is not available", Colors.RED)
            return False
    except FileNotFoundError:
        print_colored("❌ Git is not installed", Colors.RED)
        return False


def setup_virtual_environment() -> bool:
    """Set up virtual environment"""
    venv_path = Path(".venv")

    if venv_path.exists():
        print_colored("ℹ️  Virtual environment already exists", Colors.YELLOW)
        return True

    return run_command(
        [sys.executable, "-m", "venv", ".venv"], "Creating virtual environment"
    )


def get_python_executable() -> Path:
    """Get the Python executable path for the virtual environment"""
    if os.name == "nt":  # Windows
        return Path(".venv") / "Scripts" / "python.exe"
    else:  # Unix-like
        return Path(".venv") / "bin" / "python"


def install_package_dev() -> bool:
    """Install package in development mode"""
    python_exe = get_python_executable()

    commands = [
        (
            [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"],
            "Upgrading pip",
        ),
        (
            [str(python_exe), "-m", "pip", "install", "-e", ".[dev]"],
            "Installing package in development mode",
        ),
    ]

    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False

    return True


def setup_pre_commit() -> bool:
    """Set up pre-commit hooks"""
    python_exe = get_python_executable()

    commands = [
        (
            [str(python_exe), "-m", "pre_commit", "install"],
            "Installing pre-commit hooks",
        ),
        (
            [str(python_exe), "-m", "pre_commit", "autoupdate"],
            "Updating pre-commit hooks",
        ),
    ]

    for cmd, desc in commands:
        if not run_command(
            cmd, desc, check=False
        ):  # Don't fail if pre-commit isn't available
            continue

    return True


def run_initial_tests() -> bool:
    """Run initial tests to verify setup"""
    python_exe = get_python_executable()

    commands = [
        (
            [
                str(python_exe),
                "-c",
                "import xc8_wrapper; print('✅ Package import successful')",
            ],
            "Testing package import",
        ),
        (
            [str(python_exe), "-m", "pytest", "tests/test_core.py", "-v"],
            "Running core tests",
        ),
        (
            [str(python_exe), "-m", "ruff", "check", "xc8_wrapper"],
            "Running linting",
        ),
    ]

    success_count = 0
    for cmd, desc in commands:
        if run_command(cmd, desc, check=False):
            success_count += 1

    return success_count == len(commands)


def create_development_config() -> None:
    """Create development configuration files"""
    configs = [
        (
            ".vscode/settings.json",
            """{
    "python.defaultInterpreterPath": ".venv/Scripts/python.exe",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "python.linting.enabled": true,
    "ruff.enable": true,
    "ruff.lint.enable": true,
    "ruff.format.enable": true,
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".coverage": true,
        "htmlcov/": true,
        "dist/": true,
        "build/": true,
        "*.egg-info/": true
    }
}""",
        ),
        (
            ".vscode/launch.json",
            """{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Python: Demo Script",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/demo.py",
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Python: Test with Coverage",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "--cov=xc8_wrapper", "--cov-report=term-missing"],
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}""",
        ),
    ]

    for file_path, content in configs:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if not path.exists():
            path.write_text(content)
            print_colored(f"✅ Created {file_path}", Colors.GREEN)
        else:
            print_colored(f"ℹ️  {file_path} already exists", Colors.YELLOW)


def main() -> int:
    """Main setup function"""
    print_colored("🚀 XC8 Wrapper Development Setup", Colors.BOLD + Colors.CYAN)
    print("=" * 50)

    # Check prerequisites
    if not check_python_version():
        return 1

    if not check_git():
        print_colored("⚠️  Git is recommended for development", Colors.YELLOW)

    # Setup steps
    steps = [
        ("Setting up virtual environment", setup_virtual_environment),
        ("Installing package in development mode", install_package_dev),
        ("Setting up pre-commit hooks", setup_pre_commit),
        ("Creating development configuration", create_development_config),
        ("Running initial tests", run_initial_tests),
    ]

    print_colored("\n🛠️  Running setup steps...", Colors.BOLD + Colors.BLUE)

    success_count = 0
    for description, func in steps:
        print_colored(f"\n📋 {description}", Colors.CYAN)
        if func():
            success_count += 1
        else:
            print_colored(f"⚠️  {description} had issues", Colors.YELLOW)

    # Summary
    print_colored("\n📊 Setup Summary", Colors.BOLD + Colors.CYAN)
    print("=" * 50)

    if success_count == len(steps):
        print_colored("🎉 All setup steps completed successfully!", Colors.GREEN)
        print_colored(
            "\n🚀 You're ready to start developing!", Colors.BOLD + Colors.GREEN
        )
        print("\nNext steps:")
        print(
            "1. Activate virtual environment: .venv/Scripts/activate (Windows) or source .venv/bin/activate (Unix)"
        )
        print("2. Run tests: python -m pytest tests/ -v")
        print("3. Run demo: python demo.py")
        print("4. Start coding! 🎯")
        return 0
    else:
        print_colored(
            f"⚠️  {success_count}/{len(steps)} steps completed successfully",
            Colors.YELLOW,
        )
        print_colored(
            "Some setup steps had issues. Please check the output above.", Colors.YELLOW
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
