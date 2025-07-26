#!/usr/bin/env python3
"""
Command-line interface for XC8 Wrapper

This module provides the main entry point for the XC8 toolchain wrapper using Typer.
"""

import sys
from typing import Annotated, List, Optional

import typer
from colorama import init

from .core import handle_cc_tool, handle_as_tool, get_xc8_validated_tool_path, run_command
from .install import check_xc8_installation, get_xc8_download_url, install_xc8_if_needed
from .logger import log

# Initialize colorama for cross-platform support
init(autoreset=True)

# Version information
__version__ = "0.1.0"

# Create main Typer app
app = typer.Typer(
    name="xc8-wrapper",
    help="XC8 toolchain wrapper for PIC microcontrollers",
    add_completion=False,
    rich_markup_mode="rich",
)


@app.callback()
def main_callback(
    version: Annotated[
        bool, typer.Option("--version", help="Show version information")
    ] = False,
) -> None:
    """XC8 toolchain wrapper for PIC microcontrollers"""
    if version:
        log.info(f"xc8-wrapper version {__version__}")
        raise typer.Exit()


# Installation command
@app.command("install")
def install_command(
    check: Annotated[
        bool, typer.Option("--check", help="Check if XC8 is installed")
    ] = False,
    force: Annotated[
        bool, typer.Option("--force", help="Force installation even if XC8 is present")
    ] = False,
    version: Annotated[
        str, typer.Option("--version", help="XC8 version to install")
    ] = "3.00",
    url: Annotated[
        bool, typer.Option("--url", help="Show download URL for current platform")
    ] = False,
) -> None:
    """Install XC8 compiler"""
    log.info("=== XC8 INSTALLATION ===")

    if url:
        from .install import get_platform_name

        platform_name = get_platform_name()
        download_url = get_xc8_download_url(version, platform_name)
        log.info(f"Platform: {platform_name}")
        log.info(f"XC8 v{version} download URL:")
        log.info(download_url)
        return

    if check or not force:
        # Check installation status
        status = check_xc8_installation()
        log.info(f"XC8 installed: {'Yes' if status['installed'] else 'No'}")

        if status["installed"]:
            if "version" in status:
                log.info(f"Detected version: {status['version']}")
            if "path" in status:
                log.info(f"XC8 path: {status['path']}")
            if "version_string" in status:
                log.info(f"XC8 version: {status['version_string']}")
            if "error" in status:
                log.warning(f"Warning: Could not get XC8 details: {status['error']}")

        if check:
            raise typer.Exit(0 if status["installed"] else 1)

    if force or not check_xc8_installation()["installed"]:
        if force:
            log.info(f"Force installing XC8 v{version}...")
        else:
            log.info(f"Installing XC8 v{version} if needed...")

        success = install_xc8_if_needed(version, force=force)

        if success:
            log.info("XC8 installation completed successfully")
            raise typer.Exit(0)
        else:
            log.error("XC8 installation failed")
            raise typer.Exit(1)


# CC (Compiler) command - matches vendor xc8-cc options
@app.command("cc")
def cc_command(
    files: Annotated[
        Optional[List[str]], typer.Argument(help="Source files to compile")
    ] = None,
    # Basic options matching vendor help
    c: Annotated[
        bool, typer.Option("-c", help="Compile/assemble to intermediate/object file")
    ] = False,
    preprocess_comments: Annotated[
        bool, typer.Option("-C", help="Tell the preprocessor not to discard comments")
    ] = False,
    assembly: Annotated[
        bool, typer.Option("-S", help="Compile to assembly file")
    ] = False,
    verbose: Annotated[bool, typer.Option("-v", help="Verbose")] = False,
    preprocess_only: Annotated[
        bool, typer.Option("-E", help="Preprocess only")
    ] = False,
    output: Annotated[
        Optional[str], typer.Option("-o", help="Specify output file")
    ] = None,
    define: Annotated[
        Optional[List[str]], typer.Option("-D", help="Define preprocessor symbol")
    ] = None,
    undefine: Annotated[
        Optional[List[str]], typer.Option("-U", help="Undefine preprocessor symbol")
    ] = None,
    include: Annotated[
        Optional[List[str]], typer.Option("-I", help="Specify include path")
    ] = None,
    library: Annotated[
        Optional[List[str]], typer.Option("-l", help="Specify library")
    ] = None,
    library_path: Annotated[
        Optional[List[str]], typer.Option("-L", help="Specify library search path")
    ] = None,
    list_headers: Annotated[
        bool, typer.Option("-H", help="List included header files")
    ] = False,
    list_macros: Annotated[
        bool, typer.Option("-dM", help="List all defined macros")
    ] = False,
    linker_options: Annotated[
        Optional[List[str]],
        typer.Option("-Wl", help="Pass comma-separated options directly to the linker"),
    ] = None,
    xlinker: Annotated[
        Optional[List[str]],
        typer.Option("-Xlinker", help="Pass option directly to the linker"),
    ] = None,
    assembler_options: Annotated[
        Optional[List[str]],
        typer.Option("-Wa", help="Pass comma-separated options on to the assembler"),
    ] = None,
    xparser: Annotated[
        Optional[List[str]],
        typer.Option("-Xparser", help="Pass option directly to the parser"),
    ] = None,
    xp1: Annotated[
        Optional[List[str]],
        typer.Option("-Xp1", help="Pass option directly to the parser"),
    ] = None,
    xclang: Annotated[
        Optional[List[str]],
        typer.Option("-Xclang", help="Pass option directly to the parser"),
    ] = None,
    xassembler: Annotated[
        Optional[List[str]],
        typer.Option("-Xassembler", help="Pass option directly to the assembler"),
    ] = None,
    language: Annotated[
        Optional[str],
        typer.Option("-x", help="Specify the language of the input files"),
    ] = None,
    xassembler_with_cpp: Annotated[
        bool,
        typer.Option(
            "-xassembler-with-cpp",
            help="Request that assembly source files be preprocessed",
        ),
    ] = False,
    preprocessor_options: Annotated[
        Optional[List[str]],
        typer.Option(
            "-Wp", help="Pass comma-separated options directly to the preprocessor"
        ),
    ] = None,
    xpreprocessor: Annotated[
        Optional[List[str]],
        typer.Option("-Xpreprocessor", help="Pass option directly to the preprocessor"),
    ] = None,
    dry_run: Annotated[
        bool, typer.Option("-###", help="Show command lines but do not execute")
    ] = False,
    target_help: Annotated[
        bool, typer.Option("--target-help", help="Target help")
    ] = False,
    print_devices: Annotated[
        bool, typer.Option("-mprint-devices", help="List supported devices")
    ] = False,
    print_builtins: Annotated[
        bool, typer.Option("-mprint-builtins", help="List built in functions")
    ] = False,
    # CPU selection (required for compilation)
    cpu: Annotated[
        Optional[str], typer.Option("-mcpu", "--cpu", help="Select device")
    ] = None,
    # XC8 wrapper specific options
    xc8_version: Annotated[
        Optional[str],
        typer.Option("--xc8-version", help="XC8 toolchain version to use"),
    ] = None,
    xc8_path: Annotated[
        Optional[str],
        typer.Option("--xc8-path", help="Full path to XC8 tool executable"),
    ] = None,
    # Additional vendor options
    addrqual: Annotated[
        Optional[str],
        typer.Option("-maddrqual", help="Specify address space qualifier handling"),
    ] = None,
    make_deps: Annotated[
        bool, typer.Option("-M", help="Generate make dependencies")
    ] = False,
    make_deps_md: Annotated[
        bool, typer.Option("-MD", help="Generate make dependencies")
    ] = False,
    make_deps_file: Annotated[
        Optional[str], typer.Option("-MF", help="Generate make dependencies")
    ] = None,
    make_deps_mm: Annotated[
        bool, typer.Option("-MM", help="Generate make dependencies")
    ] = False,
    make_deps_mmd: Annotated[
        bool, typer.Option("-MMD", help="Generate make dependencies")
    ] = False,
    emi: Annotated[
        Optional[str],
        typer.Option("-memi", help="Specify external memory interface mode"),
    ] = None,
    errata: Annotated[
        Optional[str], typer.Option("-merrata", help="Apply errata work-arounds")
    ] = None,
    max_errors: Annotated[
        Optional[int],
        typer.Option(
            "-fmax-errors", help="Specify the maximum number of errors to report"
        ),
    ] = None,
    cci: Annotated[
        bool, typer.Option("-mcci", help="Use CCI Language extension")
    ] = False,
    ext: Annotated[
        Optional[str], typer.Option("-mext", help="Use specified language extensions")
    ] = None,
    warn_level: Annotated[
        Optional[str], typer.Option("-mwarn", help="Set warning level")
    ] = None,
    maxichip: Annotated[
        bool,
        typer.Option(
            "-mmaxichip", help="Build for hyperthetical maximized-resource device"
        ),
    ] = False,
    maxipic: Annotated[
        bool,
        typer.Option(
            "-mmaxipic", help="Build for hyperthetical maximized-resource device"
        ),
    ] = False,
    c90lib: Annotated[
        bool, typer.Option("-mc90lib", help="Link in standard C90 libraries")
    ] = False,
    nostdlib: Annotated[
        bool,
        typer.Option(
            "-nostdlib", help="Do not link the standard system startup or C library"
        ),
    ] = False,
    nostdinc: Annotated[
        bool,
        typer.Option(
            "-nostdinc",
            help="Do not search the standard C library include directories for headers",
        ),
    ] = False,
    nodefaultlibs: Annotated[
        bool, typer.Option("-nodefaultlibs", help="Do not link the standard C library")
    ] = False,
    nostartfiles: Annotated[
        bool,
        typer.Option(
            "-nostartfiles", help="Do not link the standard system startup module"
        ),
    ] = False,
    suppress_warnings: Annotated[
        bool, typer.Option("-w", help="Suppress all warnings")
    ] = False,
    save_temps: Annotated[
        bool, typer.Option("-save-temps", help="Do not delete intermediate files")
    ] = False,
    # Optimization levels
    og: Annotated[
        bool, typer.Option("-Og", help="Favor accurate debug over optimization")
    ] = False,
    os: Annotated[
        bool, typer.Option("-Os", help="Optimize for space rather than speed")
    ] = False,
    o0: Annotated[bool, typer.Option("-O0", help="Optimize level 0 (default)")] = False,
    o1: Annotated[bool, typer.Option("-O1", help="Optimize level 1")] = False,
    o2: Annotated[bool, typer.Option("-O2", help="Optimize level 2")] = False,
    o3: Annotated[bool, typer.Option("-O3", help="Optimize level 3")] = False,
    # Additional optimization options
    flocal: Annotated[
        bool, typer.Option("-flocal", help="Localized optimizations")
    ] = False,
    fcacheconst: Annotated[
        bool, typer.Option("-fcacheconst", help="Cached constants optimizations")
    ] = False,
    fasmfile: Annotated[
        bool, typer.Option("-fasmfile", help="Optimize assembler source files")
    ] = False,
    # More vendor options
    undefints: Annotated[
        bool, typer.Option("-mundefints", help="Program unassigned interrupt vectors")
    ] = False,
    ansi: Annotated[
        bool, typer.Option("-ansi", help="Use the C90 language standard")
    ] = False,
    std: Annotated[
        Optional[str], typer.Option("-std", help="Specify language standard")
    ] = None,
    pedantic: Annotated[
        bool, typer.Option("-Wpedantic", help="Flag use of non-standard keywords")
    ] = False,
    stack: Annotated[
        Optional[str],
        typer.Option("-mstack", help="Specify default stack model and size"),
    ] = None,
    heap: Annotated[
        Optional[str], typer.Option("-mheap", help="Specify maximum heap size")
    ] = None,
    summary: Annotated[
        Optional[str],
        typer.Option("-msummary", help="Specify compilation summary information"),
    ] = None,
    shroud: Annotated[
        bool,
        typer.Option(
            "-mshroud", help="Shroud (obfuscate) generated intermediate files"
        ),
    ] = False,
    # Passthrough option for raw xc8-cc arguments
    passthrough: Annotated[
        Optional[str],
        typer.Option(
            "--passthrough",
            "-p",
            help="Pass options directly to xc8-cc (e.g., '--passthrough=\"-mplib -gdwarf-3\"')",
        ),
    ] = None,
    # Additional options truncated for brevity - can be expanded as needed
    xc8_help: Annotated[
        bool, typer.Option("--xc8-help", help="Show help for xc8-cc and exit")
    ] = False,
) -> None:
    """C compiler, assembler, and linker (matches xc8-cc)"""
    log.info("=== XC8 COMPILER ===")

    # Handle xc8-cc help option
    if xc8_help:
        xc8_cc_path, _ = get_xc8_validated_tool_path("cc", xc8_version, xc8_path)
        run_command([xc8_cc_path, "--help"], "XC8 Compiler Help")
        return

    # Handle help options
    if target_help:
        log.info("Target help requested")
        # Would show target-specific help
        return

    if print_devices:
        log.info("Supported devices would be listed here")
        # Would list supported devices
        return

    if print_builtins:
        log.info("Built-in functions would be listed here")
        # Would list built-in functions
        return

    # Create args object compatible with existing handler
    class Args:
        def __init__(self) -> None:
            # Basic compilation options
            self.cpu = cpu
            self.xc8_version = xc8_version
            self.xc8_path = xc8_path
            self.files = files or []

            # Preprocessor options
            self.define = define or []
            self.undefine = undefine or []
            self.include = include or []
            self.keep_comments = preprocess_comments
            self.preprocess_only = preprocess_only

            # Compilation options
            self.compile_only = c
            self.assembly = assembly
            self.output = output
            self.verbose = verbose

            # Library options
            self.library = library or []
            self.library_path = library_path or []

            # Tool options
            self.linker_options = linker_options or []
            self.assembler_options = assembler_options or []

            # Advanced options
            self.dry_run = dry_run
            self.save_temps = save_temps
            self.suppress_warnings = suppress_warnings

            # Optimization
            optimization_flags = []
            if og:
                optimization_flags.append("-Og")
            if os:
                optimization_flags.append("-Os")
            if o0:
                optimization_flags.append("-O0")
            if o1:
                optimization_flags.append("-O1")
            if o2:
                optimization_flags.append("-O2")
            if o3:
                optimization_flags.append("-O3")
            self.optimization = optimization_flags

            # Additional vendor-specific options
            self.addrqual = addrqual
            self.emi = emi
            self.errata = errata
            self.max_errors = max_errors
            self.warn_level = warn_level
            self.std = std
            self.stack = stack
            self.heap = heap
            self.summary = summary

            # Passthrough option
            self.passthrough = passthrough

    args = Args()

    if passthrough:
        try:
            handle_cc_tool(args)
        except Exception as e:
            log.error(f"Compilation failed: {e}")
            raise typer.Exit(1)

    # Validate required arguments for compilation
    if not files and not (print_devices or print_builtins or target_help):
        log.error("No input files specified")
        raise typer.Exit(1)

    if not cpu and not (print_devices or print_builtins or target_help):
        log.error("CPU/device must be specified with -mcpu or --cpu")
        raise typer.Exit(1)

    try:
        handle_cc_tool(args)
    except Exception as e:
        log.error(f"Compilation failed: {e}")
        raise typer.Exit(1)


# PIC-AS (Assembler) command - supports PIC assembler operations
@app.command("as")
def as_command(
    files: Annotated[
        Optional[List[str]], typer.Argument(help="Assembly source files to assemble")
    ] = None,
    # Essential options only
    output: Annotated[
        Optional[str], typer.Option("-o", help="Specify output file")
    ] = None,
    verbose: Annotated[bool, typer.Option("-v", help="Verbose")] = False,
    # CPU selection
    cpu: Annotated[
        Optional[str], typer.Option("-mcpu", "--cpu", help="Select target device")
    ] = None,
    dry_run: Annotated[
        bool, typer.Option("-###", help="Show command lines but do not execute")
    ] = False,
    # XC8 wrapper specific options
    xc8_version: Annotated[
        Optional[str],
        typer.Option("--xc8-version", help="XC8 toolchain version to use"),
    ] = None,
    xc8_path: Annotated[
        Optional[str],
        typer.Option("--xc8-path", help="Full path to pic-as executable"),
    ] = None,
    # Passthrough option for raw pic-as arguments - this is the main way to use pic-as options
    passthrough: Annotated[
        Optional[str],
        typer.Option(
            "--passthrough",
            "-p",
            help="Pass options directly to pic-as (e.g., '--passthrough=\"-mpic14 -g -inhx32\"')",
        ),
    ] = None,
    # Help options
    pic_as_help: Annotated[
        bool, typer.Option("--pic-as-help", help="Show help for pic-as and exit")
    ] = False,
) -> None:
    """PIC assembler - use --passthrough for most pic-as options"""
    log.info("=== PIC ASSEMBLER ===")

    # Handle pic-as help option
    if pic_as_help:
        pic_as_path, _ = get_xc8_validated_tool_path("as", xc8_version, xc8_path)
        run_command([pic_as_path, "--help"], "PIC Assembler Help")
        return

    # Create args object compatible with existing handler
    class Args:
        def __init__(self) -> None:
            # Basic assembler options
            self.cpu = cpu
            self.xc8_version = xc8_version
            self.xc8_path = xc8_path
            self.files = files or []

            # Assembly options
            self.output = output
            self.verbose = verbose
            self.dry_run = dry_run

            # Passthrough option
            self.passthrough = passthrough

    args = Args()

    # Validate required arguments for assembly (unless using passthrough with all args)
    if not passthrough and not files:
        log.error("No input assembly files specified")
        log.error("Either provide assembly files or use --passthrough with complete command")
        raise typer.Exit(1)

    try:
        handle_as_tool(args)
    except Exception as e:
        log.error(f"Assembly failed: {e}")
        raise typer.Exit(1)


# Archive command (placeholder for future AR tool support)
@app.command("ar")
def ar_command(
    operation: Annotated[
        str,
        typer.Argument(
            help="Archive operation: r=replace/add, c=create, d=delete, t=list, x=extract"
        ),
    ],
    archive: Annotated[str, typer.Argument(help="Archive file (.a)")],
    files: Annotated[
        Optional[List[str]], typer.Argument(help="Object files (.o, .p1) to process")
    ] = None,
    verbose: Annotated[bool, typer.Option("-v", help="Verbose output")] = False,
    update: Annotated[bool, typer.Option("-u", help="Update only newer files")] = False,
    index: Annotated[
        bool, typer.Option("-s", help="Write an object-file index")
    ] = False,
) -> None:
    """Archive/librarian tool (xc8-ar)"""
    log.info("=== XC8 ARCHIVER ===")
    log.error("AR tool is not yet implemented")
    raise typer.Exit(1)


def main(argv: Optional[List[str]] = None) -> None:
    """
    Main entry point for the XC8 wrapper CLI

    Args:
        argv: Command line arguments (defaults to sys.argv)
    """
    try:
        app(argv)
    except typer.Exit as e:
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        log.warning("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
