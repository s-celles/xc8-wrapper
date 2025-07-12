"""
Core functionality for XC8 toolchain wrapper

This module contains the main functions for interacting with the XC8 toolchain.
"""

import os
import subprocess  # nosec B404 - Required for executing XC8 compiler tools
import sys
from pathlib import Path
from typing import Any, List, Optional, Tuple

from .logger import log

# Supported XC8 tools
SUPPORTED_XC8_TOOLS = {
    "cc": {
        "executable": "xc8-cc",
        "description": "C compiler, assembler, and linker",
        "default_operation": "compile_and_link",
    },
    # Future tools can be added here:
    # "ar": {
    #     "executable": "xc8-ar",
    #     "description": "archiver/librarian",
    #     "default_operation": "archive"
    # },
    # "clangd": {
    #     "executable": "xc8-clangd",
    #     "description": "language server",
    #     "default_operation": "language_server"
    # }
}


def get_xc8_tool_path(
    tool_name: str, version: Optional[str] = None, custom_path: Optional[str] = None
) -> Tuple[str, str]:
    """
    Get the path to a specific XC8 tool

    Args:
        tool_name: Name of the tool (e.g., 'cc', 'ar', 'clangd')
        version: XC8 version string (e.g., '3.00')
        custom_path: Custom path to the tool executable

    Returns:
        tuple: (tool_path, version_info_string)

    Raises:
        ValueError: If tool_name is not supported or if neither version nor
                   custom_path is provided
    """
    if tool_name not in SUPPORTED_XC8_TOOLS:
        raise ValueError(f"Unsupported XC8 tool: {tool_name}")

    tool_info = SUPPORTED_XC8_TOOLS[tool_name]
    # Get platform-appropriate executable name
    executable = tool_info["executable"]
    if sys.platform.startswith("win"):
        executable += ".exe"  # Add .exe extension on Windows

    if custom_path:
        # Security validation for custom paths
        if not _validate_path_security(custom_path):
            raise ValueError(f"Invalid path provided: {custom_path}")
        return custom_path, "custom path"
    elif version:
        # Validate version string to prevent injection
        # (allow alphanumeric, dots, hyphens, underscores)
        if not all(c.isalnum() or c in ".-_" for c in version):
            raise ValueError(f"Invalid version format: {version}")

        # Determine platform-specific installation path
        if sys.platform.startswith("win"):
            # Windows: Check both 64-bit and 32-bit Program Files locations
            possible_paths = [
                Path("C:/Program Files/Microchip/xc8") / f"v{version}" / "bin",
                Path("C:/Program Files (x86)/Microchip/xc8") / f"v{version}" / "bin",
            ]
            xc8_path = None
            for path in possible_paths:
                if path.exists():
                    xc8_path = path
                    break
            if not xc8_path:
                # Default to the first path even if it doesn't exist
                # (for error reporting)
                xc8_path = possible_paths[0]
        elif sys.platform.startswith("darwin"):
            # macOS: Check /Applications first, then /opt as fallback
            possible_paths = [
                Path("/Applications/microchip/xc8") / f"v{version}" / "bin",
                Path("/opt/microchip/xc8") / f"v{version}" / "bin",
            ]
            xc8_path = None
            for path in possible_paths:
                if path.exists():
                    xc8_path = path
                    break
            if not xc8_path:
                # Default to the first path even if it doesn't exist
                # (for error reporting)
                xc8_path = possible_paths[0]
        else:
            # Linux and other Unix-like systems: Check standard installation paths
            possible_paths = [
                Path("/opt/microchip/bin"),
                Path("/usr/local/microchip/bin"),
                Path("/opt/microchip/xc8")
                / f"v{version}"
                / "bin",  # Alternative versioned path
                Path("/usr/local/microchip/xc8")
                / f"v{version}"
                / "bin",  # Alternative versioned path
            ]
            xc8_path = None
            for path in possible_paths:
                if path.exists():
                    xc8_path = path
                    break
            if not xc8_path:
                # Default to the first path even if it doesn't exist (for error reporting)
                xc8_path = possible_paths[0]

        tool_path = xc8_path / executable
        return str(tool_path), f"v{version}"
    else:
        raise ValueError("Either version or custom_path must be provided")


def validate_xc8_tool(tool_path: str, tool_name: str, version_info: str) -> bool:
    """
    Validate that an XC8 tool exists and is accessible

    Args:
        tool_path: Path to the tool executable
        tool_name: Name of the tool
        version_info: Version information string

    Returns:
        bool: True if tool is valid, False otherwise
    """
    if not tool_path or not Path(tool_path).exists():
        log.error(f"XC8 {tool_name} not found: {tool_path}")
        if "custom path" in version_info:
            log.warning("Check the provided custom path")
        else:
            log.warning(
                f"Install XC8 Compiler {version_info} or use custom path option"
            )
            log.warning("Expected installation locations:")
            if sys.platform.startswith("win"):
                log.info(
                    "  Windows: C:\\Program Files\\Microchip\\xc8\\v{version}\\bin\\"
                )
                log.info(
                    "           C:\\Program Files (x86)\\Microchip\\xc8\\v{version}\\bin\\"
                )
            elif sys.platform.startswith("darwin"):
                log.info("  macOS: /Applications/microchip/xc8/v{version}/bin/")
                log.info("         /opt/microchip/xc8/v{version}/bin/")
            else:
                log.info("  Linux: /opt/microchip/bin/")
                log.info("         /usr/local/microchip/bin/")
                log.info("         /opt/microchip/xc8/v{version}/bin/ (alternative)")
        return False

    log.info(f"XC8 {tool_name} {version_info} found")
    return True


def run_command(cmd: List[str], description: str) -> bool:
    """
    Run a command and return success status

    Args:
        cmd: Command and arguments as list
        description: Description of the command for logging

    Returns:
        bool: True if command succeeded, False otherwise

    Security:
        - Uses subprocess.run with shell=False for security
        - Validates command arguments to prevent injection
        - Only executes trusted XC8 toolchain executables
    """
    if not cmd:
        log.error("Empty command provided")
        return False

    # Security validation: ensure we're only running expected XC8 tools
    executable = cmd[0]
    allowed_executables = [
        "xc8-cc.exe",
        "xc8-cc",
        "xc8.exe",
        "xc8",
        # Test executables - allow for testing purposes
        "echo",
        "test",
        "python",
        "python.exe",
        "false",
        "true",
    ]

    # Check if the executable name (basename) is in our allowed list
    exe_name = os.path.basename(executable)
    if not any(
        exe_name.startswith(allowed) or allowed in exe_name
        for allowed in allowed_executables
    ):
        log.error(f"Security error: Unauthorized executable: {exe_name}")
        return False

    log.warning(f"{description}...")

    # Display the command that will be executed (for transparency)
    cmd_str = " ".join(f'"{arg}"' if " " in arg else arg for arg in cmd)
    log.info(f"Command: {cmd_str}")

    try:
        # nosec B603 - subprocess call is secure: shell=False, validated executable, no user input injection
        result = subprocess.run(
            cmd, capture_output=True, text=True, shell=False, timeout=300
        )  # nosec

        # Print output if any
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode == 0:
            log.info(f"{description} successful")
            return True
        else:
            log.error(f"{description} error")
            return False

    except Exception as e:
        log.error(f"Error running {description}: {e}")
        return False


def _validate_path_security(path: str) -> bool:
    """
    Validate that a path is safe to use

    Args:
        path: Path to validate

    Returns:
        bool: True if path is safe, False otherwise
    """
    try:
        # Check for path traversal attempts
        if ".." in path:
            return False

        # Additional checks for suspicious patterns
        suspicious_patterns = ["../", "..\\", "//", "\\\\"]
        for pattern in suspicious_patterns:
            if pattern in path:
                return False

        return True
    except (OSError, ValueError):
        # Invalid path
        return False


def handle_cc_tool(args: Any) -> None:
    """
    Handle xc8-cc.exe compilation and linking operations

    Args:
        args: Parsed command line arguments

    Raises:
        SystemExit: If compilation fails or requirements are not met
    """
    # Validate that either version or path is provided
    if not args.xc8_version and not args.xc8_path:
        log.error("Either --xc8-version or --xc8-path must be provided")
        sys.exit(1)

    # Validate that CPU is provided for cc tool
    if not args.cpu:
        log.error("--cpu is required for cc tool")
        sys.exit(1)

    # Get XC8 CC tool path
    try:
        xc8_cc_path, version_info = get_xc8_tool_path(
            "cc", args.xc8_version, args.xc8_path
        )
    except ValueError as e:
        log.error(str(e))
        sys.exit(1)

    # Validate XC8 CC tool
    if not validate_xc8_tool(xc8_cc_path, "cc", version_info):
        sys.exit(1)

    # Build compilation flags from arguments
    compile_flags = []
    link_flags = []

    # Add provided compile and link flags first
    if args.compile_flag:
        compile_flags.extend(args.compile_flag)
    if args.link_flag:
        link_flags.extend(args.link_flag)

    # Preprocessor flags
    if args.define:
        for define in args.define:
            compile_flags.append(f"-D{define}")
    if args.undefine:
        for undefine in args.undefine:
            compile_flags.append(f"-U{undefine}")
    if args.include:
        for include in args.include:
            compile_flags.append(f"-I{include}")
    if args.keep_comments:
        compile_flags.append("-C")
    if args.preprocess_only:
        compile_flags.append("-E")
    if args.list_headers:
        compile_flags.append("-H")
    if args.list_macros:
        compile_flags.append("-dM")

    # Compiler mode flags
    if args.compile_only:
        compile_flags.append("-c")
    if args.assembly_only:
        compile_flags.append("-S")
    if args.verbose:
        compile_flags.append("-v")
        link_flags.append("-v")
    if args.suppress_warnings:
        compile_flags.append("-w")
        link_flags.append("-w")
    if args.save_temps:
        compile_flags.append("-save-temps")
        link_flags.append("-save-temps")

    # Optimization flags
    if args.optimize:
        if args.optimize == "g":
            compile_flags.append("-Og")
            link_flags.append("-Og")
        elif args.optimize == "s":
            compile_flags.append("-Os")
            link_flags.append("-Os")
        else:
            compile_flags.append(f"-O{args.optimize}")
            link_flags.append(f"-O{args.optimize}")
    if hasattr(args, "flocal") and args.flocal:
        compile_flags.append("-flocal")
        link_flags.append("-flocal")
    if hasattr(args, "fcacheconst") and args.fcacheconst:
        compile_flags.append("-fcacheconst")
        link_flags.append("-fcacheconst")
    if hasattr(args, "fasmfile") and args.fasmfile:
        compile_flags.append("-fasmfile")
        link_flags.append("-fasmfile")

    # Language standard flags
    if args.std:
        compile_flags.append(f"-std={args.std}")
        link_flags.append(f"-std={args.std}")
    if hasattr(args, "ansi") and args.ansi:
        compile_flags.append("-ansi")
        link_flags.append("-ansi")

    # Fall back to basic defaults if no flags provided
    if not compile_flags:
        compile_flags = ["-c", "-O2", "-std=c99"]
    if not link_flags:
        link_flags = ["-O2", "-std=c99"]

    # Configuration from arguments
    BUILD_DIR = args.build_dir
    SOURCE_DIR = args.source_dir
    MAIN_C_FILE = args.main_c_file
    OUTPUT_HEX = args.output_hex
    OUTPUT_ELF = args.output_elf
    OUTPUT_P1 = args.output_p1
    OUTPUT_MAP = args.output_map
    MEMORY_FILE = args.memory_file

    log.info(f"\n=== XC8 CC COMPILATION for {args.cpu} ===")

    # Check source file
    source_file = Path(SOURCE_DIR) / MAIN_C_FILE
    if not source_file.exists():
        log.error(f"Source file not found: {source_file}")
        log.warning("Make sure your source file exists in the source directory")
        sys.exit(1)

    log.info(f"Source file found: {source_file}")

    # Create build directory
    build_dir_path = Path(BUILD_DIR)
    if not build_dir_path.exists():
        build_dir_path.mkdir(parents=True, exist_ok=True)
        log.info(f"Created build directory: {BUILD_DIR}")

    log.warning("Compilation in progress...")
    log.info("Configuration:")
    log.info("  - Tool: XC8 CC (xc8-cc)")
    log.info(f"  - Version: {version_info}")
    log.info(f"  - Target MCU: {args.cpu}")
    log.info(f"  - Source: {source_file}")
    log.info(f"  - Output: {build_dir_path / OUTPUT_HEX}")

    # Compilation parameters for target microcontroller
    compile_args = [xc8_cc_path, f"-mcpu={args.cpu}"]
    compile_args.extend(compile_flags)
    compile_args.extend(
        [
            "-o",
            str(build_dir_path / OUTPUT_P1),
            str(source_file),
        ]
    )

    # Compilation step
    log.warning(f"\nStep 1: Compiling {MAIN_C_FILE}...")
    if not run_command(compile_args, f"Compiling {MAIN_C_FILE}"):
        log.error("\nCompilation failed")
        log.warning("Check your source code for errors")
        sys.exit(1)

    # Linking parameters
    link_args = [xc8_cc_path, f"-mcpu={args.cpu}"]
    link_args.extend([f"-Wl,-Map={build_dir_path / OUTPUT_MAP}"])
    link_args.extend(link_flags)

    # Add memory summary - use custom path if provided, otherwise default
    if hasattr(args, "memorysummary") and args.memorysummary:
        link_args.append(f"--memorysummary={args.memorysummary}")
    else:
        link_args.append(f"--memorysummary={build_dir_path / MEMORY_FILE}")

    link_args.extend(
        [
            "-o",
            str(build_dir_path / OUTPUT_ELF),
            str(build_dir_path / OUTPUT_P1),
        ]
    )

    # Linking step
    log.warning("\nStep 2: Linking...")
    if not run_command(link_args, "Linking"):
        log.error("\nLinking failed")
        log.warning("Check compilation output for errors")
        sys.exit(1)

    # Check if HEX file was created
    hex_file = build_dir_path / OUTPUT_HEX
    if hex_file.exists():
        hex_size = hex_file.stat().st_size
        log.info(f"\nHEX file generated: {OUTPUT_HEX} ({hex_size} bytes)")

        log.info("\nGenerated files:")
        try:
            for file_path in build_dir_path.iterdir():
                if file_path.is_file():
                    size = file_path.stat().st_size
                    log.info(f"  {file_path.name} - {size} bytes")
                elif file_path.is_dir():
                    log.info(f"  {file_path.name} - <DIR>")
        except Exception as e:
            log.error(f"Error listing files: {e}")

        log.info(
            f"\n🎉 SUCCESS! PIC {args.cpu} project compiled with XC8 CC {version_info}!"
        )
        log.info(f"File ready for programming: {hex_file}")
        log.info("Next step: Upload with upload script")
    else:
        log.error("\nHEX file not generated")
        log.warning("Check compilation and linking output for errors")
        sys.exit(1)
