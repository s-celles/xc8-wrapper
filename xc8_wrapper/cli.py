#!/usr/bin/env python3
"""
Command-line interface for XC8 Wrapper

This module provides the main entry point for the XC8 toolchain wrapper.
"""

import argparse
import sys
from typing import Any, List, Optional

from colorama import init

from .core import SUPPORTED_XC8_TOOLS, Colors, handle_ar_tool, handle_cc_tool, print_colored

# Initialize colorama for cross-platform support
init(autoreset=True)

# Version information
__version__ = "0.1.0"


def create_base_parser() -> argparse.ArgumentParser:
    """Create the base argument parser with common arguments"""
    parser = argparse.ArgumentParser(description="XC8 toolchain wrapper for PIC microcontrollers", prog="xc8-wrapper")

    # Version argument
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    # Tool selection
    parser.add_argument(
        "tool",
        choices=list(SUPPORTED_XC8_TOOLS.keys()),
        help="XC8 tool to use",
    )

    # Common tool path/version arguments
    parser.add_argument(
        "--xc8-version",
        help="XC8 toolchain version to use (ignored if --xc8-path is provided)",
    )
    parser.add_argument("--xc8-path", help="Full path to XC8 tool executable (overrides --xc8-version)")

    return parser


def create_cc_subparser(subparsers: Any) -> argparse.ArgumentParser:
    """Create argument parser for xc8-cc tool"""
    cc_parser: argparse.ArgumentParser = subparsers.add_parser("cc", help="C compiler, assembler, and linker")

    # Required arguments for cc tool
    cc_parser.add_argument("--cpu", required=True, help="Target microcontroller")

    # Tool path/version arguments (inherited from base)
    cc_parser.add_argument(
        "--xc8-version",
        help="XC8 toolchain version to use (ignored if --xc8-path is provided)",
    )
    cc_parser.add_argument("--xc8-path", help="Full path to XC8 tool executable (overrides --xc8-version)")

    # Preprocessor arguments
    cc_parser.add_argument(
        "-D",
        "--define",
        action="append",
        help="Define preprocessor symbol (can be used multiple times)",
    )
    cc_parser.add_argument(
        "-U",
        "--undefine",
        action="append",
        help="Undefine preprocessor symbol (can be used multiple times)",
    )
    cc_parser.add_argument(
        "-I",
        "--include",
        action="append",
        help="Specify include path (can be used multiple times)",
    )
    cc_parser.add_argument(
        "-C",
        "--keep-comments",
        action="store_true",
        help="Tell the preprocessor not to discard comments",
    )
    cc_parser.add_argument("-E", "--preprocess-only", action="store_true", help="Preprocess only")
    cc_parser.add_argument("-H", "--list-headers", action="store_true", help="List included header files")
    cc_parser.add_argument("-dM", "--list-macros", action="store_true", help="List all defined macros")

    # Compiler mode arguments
    cc_parser.add_argument(
        "-c",
        "--compile-only",
        action="store_true",
        help="Compile/assemble to intermediate/object file",
    )
    cc_parser.add_argument("-S", "--assembly-only", action="store_true", help="Compile to assembly file")
    cc_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    cc_parser.add_argument("-w", "--suppress-warnings", action="store_true", help="Suppress all warnings")
    cc_parser.add_argument("--save-temps", action="store_true", help="Do not delete intermediate files")

    # Optimization arguments
    cc_parser.add_argument(
        "-O",
        "--optimize",
        choices=["0", "1", "2", "3", "g", "s"],
        help="Optimization level (0=none, 1-3=levels, g=debug, s=size)",
    )

    # Language standard arguments
    cc_parser.add_argument("--std", help="Specify language standard (c89, c90, c99, c11, etc.)")

    # Advanced compilation flags (for anything not covered above)
    cc_parser.add_argument(
        "--compile-flag",
        action="append",
        help="Add additional compilation flag (can be used multiple times)",
    )
    cc_parser.add_argument(
        "--link-flag",
        action="append",
        help="Add additional linking flag (can be used multiple times)",
    )
    cc_parser.add_argument("--build-dir", default="build", help="Build directory (default: build)")
    cc_parser.add_argument("--source-dir", default="src", help="Source directory (default: src)")
    cc_parser.add_argument("--main-c-file", default="main.c", help="Main C file (default: main.c)")
    cc_parser.add_argument("--output-hex", default="main.hex", help="Output HEX file (default: main.hex)")
    cc_parser.add_argument("--output-elf", default="main.elf", help="Output ELF file (default: main.elf)")
    cc_parser.add_argument("--output-p1", default="main.p1", help="Output P1 file (default: main.p1)")
    cc_parser.add_argument("--output-map", default="main.map", help="Output MAP file (default: main.map)")
    cc_parser.add_argument(
        "--memory-file",
        default="memoryfile.xml",
        help="Memory file (default: memoryfile.xml)",
    )

    return cc_parser


def create_ar_subparser(subparsers: Any) -> argparse.ArgumentParser:
    """Create argument parser for xc8-ar tool"""
    ar_parser: argparse.ArgumentParser = subparsers.add_parser(
        "ar", help="Archiver/librarian for creating and managing library archives"
    )

    # Tool path/version arguments (inherited from base)
    ar_parser.add_argument(
        "--xc8-version",
        help="XC8 toolchain version to use (ignored if --xc8-path is provided)",
    )
    ar_parser.add_argument("--xc8-path", help="Full path to XC8 tool executable (overrides --xc8-version)")

    # Archiver operation arguments
    ar_parser.add_argument(
        "operation",
        choices=["r", "c", "d", "t", "x"],
        help="Archive operation: r=replace/add, c=create, d=delete, t=list, x=extract",
    )

    # Archive file
    ar_parser.add_argument("archive", help="Archive file (.a)")

    # Object files
    ar_parser.add_argument("files", nargs="*", help="Object files (.o, .p1) to process")

    # Modifiers
    ar_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    ar_parser.add_argument("-u", "--update", action="store_true", help="Update only newer files")
    ar_parser.add_argument("-s", "--index", action="store_true", help="Write an object-file index")

    return ar_parser


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the hierarchical argument parser"""
    # Create main parser with tool selection
    parser = argparse.ArgumentParser(description="XC8 toolchain wrapper for PIC microcontrollers", prog="xc8-wrapper")

    # Version argument at top level
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    # Create subparsers for each tool
    subparsers = parser.add_subparsers(dest="tool", help="XC8 tool to use", required=True)

    # Add tool-specific subparsers
    create_cc_subparser(subparsers)
    create_ar_subparser(subparsers)

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

    # Route to appropriate tool handler
    if args.tool == "cc":
        handle_cc_tool(args)
    elif args.tool == "ar":
        handle_ar_tool(args)
    else:
        print_colored(f"✗ Tool '{args.tool}' is not yet implemented", Colors.RED)
        print_colored(f"Currently supported tools: {', '.join(SUPPORTED_XC8_TOOLS.keys())}", Colors.YELLOW)
        sys.exit(1)


if __name__ == "__main__":
    main()
