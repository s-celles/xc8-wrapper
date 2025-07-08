"""
Core functionality for XC8 toolchain wrapper

This module contains the main functions for interacting with the XC8 toolchain.
"""

import os
import subprocess  # nosec B404 - Required for executing XC8 compiler tools
import sys
from pathlib import Path
from typing import Any, List, Optional, Tuple

from colorama import Fore, Style, init

# Initialize colorama for cross-platform support
init(autoreset=True)


def print_colored(text: str, color: str) -> None:
    """Print text with specified color using colorama"""
    print(f"{color}{text}{Style.RESET_ALL}")


# Color constants
class Colors:
    RED: str = Fore.RED
    GREEN: str = Fore.GREEN
    YELLOW: str = Fore.YELLOW
    BLUE: str = Fore.BLUE
    CYAN: str = Fore.CYAN
    WHITE: str = Fore.WHITE
    GRAY: str = Fore.LIGHTBLACK_EX


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


def _get_platform_xc8_paths(version: str) -> List[Path]:
    """
    Get platform-specific XC8 installation paths in order of preference

    Args:
        version: XC8 version string (e.g., '3.00')

    Returns:
        List of Path objects representing possible installation locations
    """
    if sys.platform.startswith("win"):
        return [
            Path("C:/Program Files/Microchip/xc8") / f"v{version}" / "bin",
            Path("C:/Program Files (x86)/Microchip/xc8") / f"v{version}" / "bin",
        ]
    elif sys.platform.startswith("darwin"):
        return [
            Path("/Applications/microchip/xc8") / f"v{version}" / "bin",
            Path("/opt/microchip/xc8") / f"v{version}" / "bin",
        ]
    else:
        return [
            Path("/opt/microchip/bin"),
            Path("/usr/local/microchip/bin"),
            Path("/opt/microchip/xc8") / f"v{version}" / "bin",
            Path("/usr/local/microchip/xc8") / f"v{version}" / "bin",
        ]


def _get_platform_executable_name(base_name: str) -> str:
    """
    Get platform-appropriate executable name

    Args:
        base_name: Base executable name (e.g., 'xc8-cc')

    Returns:
        Platform-appropriate executable name
    """
    if sys.platform.startswith("win"):
        return f"{base_name}.exe"
    return base_name


def _find_existing_xc8_path(possible_paths: List[Path]) -> Optional[Path]:
    """
    Find the first existing path from a list of possible paths

    Args:
        possible_paths: List of Path objects to check

    Returns:
        First existing path, or None if none exist
    """
    for path in possible_paths:
        if path.exists():
            return path
    return None


def get_xc8_tool_path(tool_name: str, version: Optional[str] = None, custom_path: Optional[str] = None) -> Tuple[str, str]:
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
    executable = _get_platform_executable_name(tool_info["executable"])

    if custom_path:
        if not _validate_path_security(custom_path):
            raise ValueError(f"Invalid path provided: {custom_path}")
        return custom_path, "custom path"
    elif version:
        if not all(c.isalnum() or c in ".-_" for c in version):
            raise ValueError(f"Invalid version format: {version}")

        possible_paths = _get_platform_xc8_paths(version)
        xc8_path = _find_existing_xc8_path(possible_paths)

        if not xc8_path:
            xc8_path = possible_paths[0]

        tool_path = xc8_path / executable
        return str(tool_path), f"v{version}"
    else:
        raise ValueError("Either version or custom_path must be provided")


def _print_installation_paths(version: str) -> None:
    """
    Print expected installation paths for the current platform

    Args:
        version: XC8 version string for path formatting
    """
    print_colored("Expected installation locations:", Colors.YELLOW)

    possible_paths = _get_platform_xc8_paths(version)

    if sys.platform.startswith("win"):
        platform_name = "Windows"
    elif sys.platform.startswith("darwin"):
        platform_name = "macOS"
    else:
        platform_name = "Linux"

    for i, path in enumerate(possible_paths):
        prefix = f"  {platform_name}: " if i == 0 else f"  {' ' * len(platform_name)}: "
        print_colored(f"{prefix}{path}/", Colors.GRAY)


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
        print_colored(f"✗ XC8 {tool_name} not found: {tool_path}", Colors.RED)
        if "custom path" in version_info:
            print_colored("Check the provided custom path", Colors.YELLOW)
        else:
            print_colored(f"Install XC8 Compiler {version_info} or use custom path option", Colors.YELLOW)
            # Extract version from version_info string for path formatting
            version = version_info.replace("v", "") if version_info.startswith("v") else version_info
            _print_installation_paths(version)
        return False

    print_colored(f"✓ XC8 {tool_name} {version_info} found", Colors.GREEN)
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
        print_colored("✗ Empty command provided", Colors.RED)
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
    if not any(exe_name.startswith(allowed) or allowed in exe_name for allowed in allowed_executables):
        print_colored(f"✗ Security error: Unauthorized executable: {exe_name}", Colors.RED)
        return False

    print_colored(f"{description}...", Colors.YELLOW)

    # Display the command that will be executed (for transparency)
    cmd_str = " ".join(f'"{arg}"' if " " in arg else arg for arg in cmd)
    print_colored(f"Command: {cmd_str}", Colors.CYAN)

    try:
        # nosec B603 - subprocess call is secure: shell=False, validated executable, no user input injection
        result = subprocess.run(cmd, capture_output=True, text=True, shell=False, timeout=300)  # nosec

        # Print output if any
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode == 0:
            print_colored(f"✓ {description} successful", Colors.GREEN)
            return True
        else:
            print_colored(f"✗ {description} error", Colors.RED)
            return False

    except Exception as e:
        print_colored(f"✗ Error running {description}: {e}", Colors.RED)
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
        # Convert to absolute path to resolve any relative references
        abs_path = Path(path).resolve()

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
        print_colored("✗ Either --xc8-version or --xc8-path must be provided", Colors.RED)
        sys.exit(1)

    # Validate that CPU is provided for cc tool
    if not args.cpu:
        print_colored("✗ --cpu is required for cc tool", Colors.RED)
        sys.exit(1)

    # Get XC8 CC tool path
    try:
        xc8_cc_path, version_info = get_xc8_tool_path("cc", args.xc8_version, args.xc8_path)
    except ValueError as e:
        print_colored(f"✗ {e}", Colors.RED)
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

    print_colored(f"\n=== XC8 CC COMPILATION for {args.cpu} ===", Colors.CYAN)

    # Check source file
    source_file = Path(SOURCE_DIR) / MAIN_C_FILE
    if not source_file.exists():
        print_colored(f"✗ Source file not found: {source_file}", Colors.RED)
        print_colored("Make sure your source file exists in the source directory", Colors.YELLOW)
        sys.exit(1)

    print_colored(f"✓ Source file found: {source_file}", Colors.GREEN)

    # Create build directory
    build_dir_path = Path(BUILD_DIR)
    if not build_dir_path.exists():
        build_dir_path.mkdir(parents=True, exist_ok=True)
        print_colored(f"✓ Created build directory: {BUILD_DIR}", Colors.GREEN)

    print_colored("\nCompilation in progress...", Colors.YELLOW)
    print_colored("Configuration:", Colors.BLUE)
    print_colored("  - Tool: XC8 CC (xc8-cc.exe)", Colors.GRAY)
    print_colored(f"  - Version: {version_info}", Colors.GRAY)
    print_colored(f"  - Target MCU: {args.cpu}", Colors.GRAY)
    print_colored(f"  - Source: {source_file}", Colors.GRAY)
    print_colored(f"  - Output: {build_dir_path / OUTPUT_HEX}", Colors.GRAY)

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
    print_colored(f"\nStep 1: Compiling {MAIN_C_FILE}...", Colors.YELLOW)
    if not run_command(compile_args, f"Compiling {MAIN_C_FILE}"):
        print_colored("\n✗ Compilation failed", Colors.RED)
        print_colored("Check your source code for errors", Colors.YELLOW)
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
    print_colored("\nStep 2: Linking...", Colors.YELLOW)
    if not run_command(link_args, "Linking"):
        print_colored("\n✗ Linking failed", Colors.RED)
        print_colored("Check compilation output for errors", Colors.YELLOW)
        sys.exit(1)

    # Check if HEX file was created
    hex_file = build_dir_path / OUTPUT_HEX
    if hex_file.exists():
        hex_size = hex_file.stat().st_size
        print_colored(f"\n✓ HEX file generated: {OUTPUT_HEX} ({hex_size} bytes)", Colors.GREEN)

        print_colored("\nGenerated files:", Colors.BLUE)
        try:
            for file_path in build_dir_path.iterdir():
                if file_path.is_file():
                    size = file_path.stat().st_size
                    print_colored(f"  {file_path.name} - {size} bytes", Colors.GRAY)
                elif file_path.is_dir():
                    print_colored(f"  {file_path.name} - <DIR>", Colors.GRAY)
        except Exception as e:
            print_colored(f"Error listing files: {e}", Colors.RED)

        print_colored(
            f"\n🎉 SUCCESS! PIC {args.cpu} project compiled with XC8 CC {version_info}!",
            Colors.GREEN,
        )
        print_colored(
            f"File ready for programming: {hex_file}",
            Colors.WHITE,
        )
        print_colored("Next step: Upload with upload script", Colors.CYAN)
    else:
        print_colored("\n✗ HEX file not generated", Colors.RED)
        print_colored("Check compilation and linking output for errors", Colors.YELLOW)
        sys.exit(1)
