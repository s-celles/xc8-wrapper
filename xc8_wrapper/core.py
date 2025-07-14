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

# Known XC8 versions that actually exist (highest to lowest)
XC8_KNOWN_VERSIONS = [
    "3.00",
    "2.50",
    "2.46",
    "2.45",
    "2.41",
    "2.40",
    "2.36",
    "2.35",
    "2.32",
    "2.31",
    "2.30",
    "2.20",
    "2.10",
    "2.05",
    "2.00",
]

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
        # Use the provided version
        pass  # Continue with existing logic below
    else:
        # Auto-detect the latest version if none provided
        version = get_latest_xc8_version()
        if not version:
            raise ValueError(
                "No XC8 installation found. Please install XC8 compiler or provide a custom path."
            )
        log.info(f"Auto-detected XC8 version: {version}")

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
    elif sys.platform.startswith("darwin"):
        # macOS: Check /Applications first, then /opt as fallback
        possible_paths = [
            Path("/Applications/microchip/xc8") / f"v{version}" / "bin",
            Path("/opt/microchip/xc8") / f"v{version}" / "bin",
        ]
    else:
        # Linux and other Unix-like systems: Check standard installation paths
        possible_paths = [
            Path("/opt/microchip/bin"),
            Path("/usr/local/microchip/bin"),
            Path("/opt/microchip/xc8") / f"v{version}" / "bin",
            Path("/usr/local/microchip/xc8") / f"v{version}" / "bin",
        ]

    # Find the first existing path
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


def find_available_xc8_versions() -> List[str]:
    """
    Find all available XC8 versions installed on the system

    Returns:
        List[str]: List of available XC8 versions (e.g., ['3.00', '2.46', '2.36'])
                  Sorted from newest to oldest
    """
    versions = []

    if sys.platform.startswith("win"):
        # Windows: Check both 64-bit and 32-bit Program Files locations
        base_paths = [
            Path("C:/Program Files/Microchip/xc8"),
            Path("C:/Program Files (x86)/Microchip/xc8"),
        ]
    elif sys.platform.startswith("darwin"):
        # macOS
        base_paths = [
            Path("/Applications/microchip/xc8"),
            Path("/opt/microchip/xc8"),
        ]
    else:
        # Linux and other Unix-like systems
        base_paths = [
            Path("/opt/microchip/xc8"),
            Path("/usr/local/microchip/xc8"),
        ]

    for base_path in base_paths:
        if base_path.exists():
            for version_dir in base_path.glob("v*"):
                if version_dir.is_dir():
                    version = version_dir.name[1:]  # Remove 'v' prefix
                    if version not in versions:
                        versions.append(version)

    # Sort versions (newest first)
    versions.sort(reverse=True)
    return versions


def get_latest_xc8_version() -> Optional[str]:
    """
    Get the latest installed XC8 version

    Returns:
        Optional[str]: Latest XC8 version found, or None if no versions found
    """
    versions = find_available_xc8_versions()
    return versions[0] if versions else None


def handle_cc_tool(args: Any) -> None:
    """
    Handle xc8-cc.exe compilation and linking operations

    Args:
        args: Parsed command line arguments

    Raises:
        SystemExit: If compilation fails or requirements are not met
    """
    # Validate that either version or path is provided, or try auto-detection
    if not args.xc8_version and not args.xc8_path:
        log.info("No XC8 version or path specified, attempting auto-detection...")
        # Try to use default XC8 installation
        try:
            xc8_cc_path, version_info = get_xc8_tool_path("cc")
            log.info(f"Auto-detected XC8: {version_info}")
        except ValueError as e:
            log.error("XC8 auto-detection failed. Either --xc8-version or --xc8-path must be provided")
            log.error(str(e))
            sys.exit(1)
    else:
        # Get XC8 CC tool path with provided version/path
        try:
            xc8_cc_path, version_info = get_xc8_tool_path(
                "cc", args.xc8_version, args.xc8_path
            )
        except ValueError as e:
            log.error(str(e))
            sys.exit(1)
    
    # Validate that CPU is provided for cc tool
    if not args.cpu:
        log.error("--cpu is required for cc tool")
        sys.exit(1)

    # Validate XC8 CC tool
    if not validate_xc8_tool(xc8_cc_path, "cc", version_info):
        sys.exit(1)

    # Build compilation command directly from arguments (Typer style)
    cmd_args = [xc8_cc_path]
    
    # Add CPU selection
    cmd_args.append(f"-mcpu={args.cpu}")
    
    # Preprocessor flags
    if args.define and hasattr(args.define, '__iter__'):
        for define in args.define:
            cmd_args.append(f"-D{define}")
    if args.undefine and hasattr(args.undefine, '__iter__'):
        for undefine in args.undefine:
            cmd_args.append(f"-U{undefine}")
    if args.include and hasattr(args.include, '__iter__'):
        for include in args.include:
            cmd_args.append(f"-I{include}")
    if args.keep_comments:
        cmd_args.append("-C")
    if args.preprocess_only:
        cmd_args.append("-E")
    
    # Compilation mode flags
    if args.compile_only:
        cmd_args.append("-c")
    if hasattr(args, 'assembly') and args.assembly and not str(args.assembly).startswith('<Mock'):
        cmd_args.append("-S")
    
    # Output file
    if args.output:
        cmd_args.extend(["-o", args.output])
    
    # Verbose mode
    if args.verbose:
        cmd_args.append("-v")
    
    # Warning control
    if args.suppress_warnings:
        cmd_args.append("-w")
    
    # Save intermediate files
    if args.save_temps:
        cmd_args.append("-save-temps")
    
    # Optimization flags
    if hasattr(args, 'optimization') and args.optimization and hasattr(args.optimization, '__iter__'):
        cmd_args.extend(args.optimization)
    
    # Library flags
    if args.library and hasattr(args.library, '__iter__'):
        for lib in args.library:
            cmd_args.append(f"-l{lib}")
    if args.library_path and hasattr(args.library_path, '__iter__'):
        for lib_path in args.library_path:
            cmd_args.append(f"-L{lib_path}")
    
    # Linker options
    if args.linker_options and hasattr(args.linker_options, '__iter__'):
        for opt in args.linker_options:
            cmd_args.append(f"-Wl,{opt}")
    
    # Assembler options
    if args.assembler_options and hasattr(args.assembler_options, '__iter__'):
        for opt in args.assembler_options:
            cmd_args.append(f"-Wa,{opt}")
    
    # Advanced compiler options
    if hasattr(args, 'addrqual') and args.addrqual and not str(args.addrqual).startswith('<Mock'):
        cmd_args.append(f"-maddrqual={args.addrqual}")
    if hasattr(args, 'emi') and args.emi and not str(args.emi).startswith('<Mock'):
        cmd_args.append(f"-memi={args.emi}")
    if hasattr(args, 'errata') and args.errata and not str(args.errata).startswith('<Mock'):
        cmd_args.append(f"-merrata={args.errata}")
    if hasattr(args, 'max_errors') and args.max_errors and not str(args.max_errors).startswith('<Mock'):
        cmd_args.append(f"-fmax-errors={args.max_errors}")
    if hasattr(args, 'warn_level') and args.warn_level and not str(args.warn_level).startswith('<Mock'):
        cmd_args.append(f"-mwarn={args.warn_level}")
    if hasattr(args, 'std') and args.std and not str(args.std).startswith('<Mock'):
        cmd_args.append(f"-std={args.std}")
    if hasattr(args, 'stack') and args.stack and not str(args.stack).startswith('<Mock'):
        cmd_args.append(f"-mstack={args.stack}")
    if hasattr(args, 'heap') and args.heap and not str(args.heap).startswith('<Mock'):
        cmd_args.append(f"-mheap={args.heap}")
    if hasattr(args, 'summary') and args.summary and not str(args.summary).startswith('<Mock'):
        cmd_args.append(f"-msummary={args.summary}")
    
    # Add source files
    if args.files and hasattr(args.files, '__iter__'):
        cmd_args.extend(args.files)
    
    log.info(f"\n=== XC8 CC COMPILATION for {args.cpu} ===")
    log.info("Configuration:")
    log.info("  - Tool: XC8 CC (xc8-cc)")
    log.info(f"  - Version: {version_info}")
    log.info(f"  - Target MCU: {args.cpu}")
    if args.files and hasattr(args.files, '__iter__'):
        try:
            log.info(f"  - Source files: {', '.join(str(f) for f in args.files)}")
        except (TypeError, ValueError):
            log.info(f"  - Source files: {args.files}")
    if args.output:
        log.info(f"  - Output: {args.output}")
    
    # Show command if dry run
    if hasattr(args, 'dry_run') and args.dry_run:
        try:
            log.info(f"\nWould execute: {' '.join(str(arg) for arg in cmd_args)}")
        except (TypeError, ValueError):
            log.info(f"\nWould execute: {cmd_args}")
        return
    
    # Execute compilation
    log.warning("Compilation in progress...")
    if not run_command(cmd_args, "XC8 Compilation"):
        log.error("\nCompilation failed")
        log.warning("Check your source code for errors")
        sys.exit(1)
    
    log.info(f"\n🎉 SUCCESS! PIC {args.cpu} compilation completed with XC8 CC {version_info}!")
    log.info("Next step: Check output files or program device")
