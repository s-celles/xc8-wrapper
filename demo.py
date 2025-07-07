#!/usr/bin/env python3
"""
Demo script for XC8 Wrapper Package

This script demonstrates how to use the XC8 wrapper package.
"""

from xc8_wrapper import get_xc8_tool_path, SUPPORTED_XC8_TOOLS, Colors, print_colored


def demo_tool_path_resolution():
    """Demonstrate tool path resolution"""
    print_colored("=== DEMO: XC8 Tool Path Resolution ===", Colors.CYAN)

    # Show supported tools
    print_colored("Supported XC8 tools:", Colors.BLUE)
    for tool_name, tool_info in SUPPORTED_XC8_TOOLS.items():
        print_colored(f"  - {tool_name}: {tool_info['description']}", Colors.GRAY)

    # Demonstrate path resolution with version
    try:
        print_colored("\nResolving tool path with version:", Colors.BLUE)
        path, version_info = get_xc8_tool_path("cc", version="3.00")
        print_colored(f"  Tool: xc8-cc.exe", Colors.GRAY)
        print_colored(f"  Path: {path}", Colors.GRAY)
        print_colored(f"  Version: {version_info}", Colors.GRAY)
    except Exception as e:
        print_colored(f"  Error: {e}", Colors.RED)

    # Demonstrate path resolution with custom path
    try:
        print_colored("\nResolving tool path with custom path:", Colors.BLUE)
        custom_path = r"C:\custom\path\xc8-cc.exe"
        path, version_info = get_xc8_tool_path("cc", custom_path=custom_path)
        print_colored(f"  Tool: xc8-cc.exe", Colors.GRAY)
        print_colored(f"  Path: {path}", Colors.GRAY)
        print_colored(f"  Version: {version_info}", Colors.GRAY)
    except Exception as e:
        print_colored(f"  Error: {e}", Colors.RED)


def demo_cli_usage():
    """Demonstrate CLI usage examples"""
    print_colored("\n=== DEMO: CLI Usage Examples ===", Colors.CYAN)

    examples = [
        "# Basic compilation",
        "xc8-wrapper --cpu PIC16F876A --xc8-version 3.00",
        "",
        "# With optimization level 2",
        "xc8-wrapper --cpu PIC16F876A --xc8-version 3.00 -O2",
        "",
        "# With custom directories",
        "xc8-wrapper --cpu PIC16F876A --xc8-version 3.00 --source-dir my_src --build-dir my_build",
        "",
        "# With preprocessor definitions",
        "xc8-wrapper --cpu PIC16F876A --xc8-version 3.00 -DDEBUG=1 -DVERSION=100",
        "",
        "# Compile only (no linking)",
        "xc8-wrapper --cpu PIC16F876A --xc8-version 3.00 -c",
        "",
        "# With custom XC8 path",
        'xc8-wrapper --cpu PIC16F876A --xc8-path "C:\\Custom\\XC8\\bin\\xc8-cc.exe"',
    ]

    for example in examples:
        if example.startswith("#"):
            print_colored(example, Colors.BLUE)
        elif example == "":
            print()
        else:
            print_colored(example, Colors.GRAY)


def demo_package_info():
    """Show package information"""
    print_colored("\n=== DEMO: Package Information ===", Colors.CYAN)

    import xc8_wrapper

    print_colored(f"Package version: {xc8_wrapper.__version__}", Colors.GREEN)
    print_colored(f"Author: {xc8_wrapper.__author__}", Colors.GREEN)
    print_colored(f"Email: {xc8_wrapper.__email__}", Colors.GREEN)

    print_colored("\nAvailable imports:", Colors.BLUE)
    for item in xc8_wrapper.__all__:
        print_colored(f"  - {item}", Colors.GRAY)


def main():
    """Main demo function"""
    print_colored("XC8 WRAPPER PACKAGE DEMONSTRATION", Colors.CYAN)
    print_colored("=" * 40, Colors.CYAN)

    demo_package_info()
    demo_tool_path_resolution()
    demo_cli_usage()

    print_colored("\n" + "=" * 40, Colors.CYAN)
    print_colored("Demo completed! Try the CLI commands above.", Colors.GREEN)


if __name__ == "__main__":
    main()
