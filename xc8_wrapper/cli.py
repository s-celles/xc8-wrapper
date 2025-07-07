#!/usr/bin/env python3
"""
Command-line interface for XC8 Wrapper

This module provides the main entry point for the XC8 toolchain wrapper.
"""

import argparse
import sys
from typing import List, Optional
from colorama import init, Fore, Style

# Initialize colorama for cross-platform support
init(autoreset=True)

from .core import handle_cc_tool, SUPPORTED_XC8_TOOLS

# Version information
__version__ = "0.1.0"


def print_colored(text: str, color: str) -> None:
    """Print text with specified color using colorama"""
    print(f"{color}{text}{Style.RESET_ALL}")


# Color constants
class Colors:
    CYAN = Fore.CYAN


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser"""
    parser = argparse.ArgumentParser(
        description="XC8 toolchain wrapper for PIC microcontrollers", prog="xc8-wrapper"
    )

    # Version argument
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    # Tool selection (currently only cc is implemented)
    parser.add_argument(
        "--tool",
        choices=list(SUPPORTED_XC8_TOOLS.keys()),
        default="cc",
        help="XC8 tool to use (default: cc)",
    )

    # Tool path/version arguments
    parser.add_argument(
        "--xc8-version",
        help="XC8 toolchain version to use (ignored if --xc8-path is provided)",
    )
    parser.add_argument(
        "--xc8-path", help="Full path to XC8 tool executable (overrides --xc8-version)"
    )

    # Compilation-specific arguments (when tool=cc)
    parser.add_argument("--cpu", help="Target microcontroller (required for cc tool)")

    # Preprocessor arguments
    parser.add_argument(
        "-D",
        "--define",
        action="append",
        help="Define preprocessor symbol (can be used multiple times)",
    )
    parser.add_argument(
        "-U",
        "--undefine",
        action="append",
        help="Undefine preprocessor symbol (can be used multiple times)",
    )
    parser.add_argument(
        "-I",
        "--include",
        action="append",
        help="Specify include path (can be used multiple times)",
    )
    parser.add_argument(
        "-C",
        "--keep-comments",
        action="store_true",
        help="Tell the preprocessor not to discard comments",
    )
    parser.add_argument(
        "-E", "--preprocess-only", action="store_true", help="Preprocess only"
    )
    parser.add_argument(
        "-H", "--list-headers", action="store_true", help="List included header files"
    )
    parser.add_argument(
        "-dM", "--list-macros", action="store_true", help="List all defined macros"
    )

    # Compiler mode arguments
    parser.add_argument(
        "-c",
        "--compile-only",
        action="store_true",
        help="Compile/assemble to intermediate/object file",
    )
    parser.add_argument(
        "-S", "--assembly-only", action="store_true", help="Compile to assembly file"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "-w", "--suppress-warnings", action="store_true", help="Suppress all warnings"
    )
    parser.add_argument(
        "--save-temps", action="store_true", help="Do not delete intermediate files"
    )

    # Optimization arguments
    parser.add_argument(
        "-O",
        "--optimize",
        choices=["0", "1", "2", "3", "g", "s"],
        help="Optimization level (0=none, 1-3=levels, g=debug, s=size)",
    )

    # Language standard arguments
    parser.add_argument(
        "--std", help="Specify language standard (c89, c90, c99, c11, etc.)"
    )

    # Advanced compilation flags (for anything not covered above)
    parser.add_argument(
        "--compile-flag",
        action="append",
        help="Add additional compilation flag (can be used multiple times)",
    )
    parser.add_argument(
        "--link-flag",
        action="append",
        help="Add additional linking flag (can be used multiple times)",
    )
    parser.add_argument(
        "--build-dir", default="build", help="Build directory (default: build)"
    )
    parser.add_argument(
        "--source-dir", default="src", help="Source directory (default: src)"
    )
    parser.add_argument(
        "--main-c-file", default="main.c", help="Main C file (default: main.c)"
    )
    parser.add_argument(
        "--output-hex", default="main.hex", help="Output HEX file (default: main.hex)"
    )
    parser.add_argument(
        "--output-elf", default="main.elf", help="Output ELF file (default: main.elf)"
    )
    parser.add_argument(
        "--output-p1", default="main.p1", help="Output P1 file (default: main.p1)"
    )
    parser.add_argument(
        "--output-map", default="main.map", help="Output MAP file (default: main.map)"
    )
    parser.add_argument(
        "--memory-file",
        default="memoryfile.xml",
        help="Memory file (default: memoryfile.xml)",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    """
    Main entry point for the XC8 wrapper CLI

    Args:
        argv: Command line arguments (defaults to sys.argv)
    """
    print_colored("=== XC8 TOOLCHAIN WRAPPER ===", Colors.CYAN)

    parser = create_argument_parser()
    args = parser.parse_args(argv)

    # Validate tool-specific requirements
    if args.tool == "cc":
        handle_cc_tool(args)
    else:
        print_colored(f"✗ Tool '{args.tool}' is not yet implemented", Colors.RED)
        print_colored("Currently supported tools: cc", Colors.YELLOW)
        sys.exit(1)


if __name__ == "__main__":
    main()
