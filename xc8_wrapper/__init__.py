"""
XC8 Wrapper Package

A Python wrapper for Microchip's XC8 toolchain for PIC microcontrollers.
"""

__version__ = "0.1.0"
__author__ = "Sébastien Celles"
__email__ = "s.celles@gmail.com"

from .core import (
    SUPPORTED_XC8_TOOLS,
    Colors,
    get_xc8_tool_path,
    handle_cc_tool,
    print_colored,
    run_command,
    validate_xc8_tool,
)

__all__ = [
    "get_xc8_tool_path",
    "validate_xc8_tool",
    "run_command",
    "handle_cc_tool",
    "SUPPORTED_XC8_TOOLS",
    "Colors",
    "print_colored",
]
