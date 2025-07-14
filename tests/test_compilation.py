"""
Tests for XC8 Compilation functionality

This module tests the actual compilation of PIC C code using xc8-wrapper.
Uses the install.py module for XC8 installation if needed in CI environments.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from xc8_wrapper.core import get_xc8_tool_path
from xc8_wrapper.install import (
    is_xc8_installed,
    install_xc8_if_needed,
    get_installed_xc8_version,
)

# Sample PIC C code for testing
SAMPLE_PIC_CODE = """#include <xc.h>

// Configuration bits for PIC16F876A
#pragma config FOSC = HS        // HS Oscillator
#pragma config WDTE = OFF       // Watchdog Timer disabled
#pragma config PWRTE = ON       // Power-up Timer enabled
#pragma config BOREN = ON       // Brown-out Reset enabled
#pragma config LVP = OFF        // Low Voltage Programming disabled
#pragma config CPD = OFF        // Data EEPROM Code Protection disabled
#pragma config WRT = OFF        // Flash Program Memory Write Enable disabled
#pragma config CP = OFF         // Flash Program Memory Code Protection disabled

#define _XTAL_FREQ 4000000      // Oscillator frequency 4MHz

void main(void) {
    // Configure PORTC as output
    TRISC = 0x00;

    while(1) {
        // Turn on all LEDs on PORTC
        PORTC = 0xFF;
        __delay_ms(500);

        // Turn off all LEDs
        PORTC = 0x00;
        __delay_ms(500);
    }
}
"""


@pytest.mark.integration
@pytest.mark.slow
class TestXC8Compilation:
    """Test XC8 compilation functionality"""

    def test_xc8_installation_check(self):
        """Test XC8 installation detection"""
        # This test should always pass, just checking detection logic
        is_installed = is_xc8_installed()
        print(f"XC8 installed: {is_installed}")

        if is_installed:
            # Get the detected version
            detected_version = get_installed_xc8_version()
            print(f"Detected XC8 version: {detected_version}")

            try:
                # Use detected version if available, otherwise try without version
                if detected_version and detected_version != "unknown":
                    xc8_path, _ = get_xc8_tool_path("cc", version=detected_version)
                else:
                    xc8_path, _ = get_xc8_tool_path("cc")
                print(f"XC8 path: {xc8_path}")
                assert Path(xc8_path).exists()
            except Exception as e:
                pytest.fail(f"XC8 path detection failed: {e}")

    @pytest.mark.skipif(
        os.environ.get("CI") == "true" and os.environ.get("INSTALL_XC8") != "true",
        reason="XC8 installation skipped in CI (set INSTALL_XC8=true to enable)",
    )
    def test_install_xc8_if_needed(self):
        """Test XC8 installation if needed"""
        # Try to install XC8 if not present
        success = install_xc8_if_needed()

        if not success and not is_xc8_installed():
            pytest.skip("XC8 installation failed or skipped")

        # Verify XC8 is now available
        assert is_xc8_installed(), (
            "XC8 should be installed after install_xc8_if_needed()"
        )

    @pytest.mark.skipif(
        not is_xc8_installed() and os.environ.get("INSTALL_XC8") != "true",
        reason="XC8 not installed (set INSTALL_XC8=true to enable auto-install)",
    )
    def test_compile_simple_pic_program(self):
        """Test compilation of a simple PIC C program"""
        # Install XC8 if needed
        if not is_xc8_installed():
            success = install_xc8_if_needed()
            if not success:
                pytest.skip("XC8 installation failed")

        # Create temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            main_c = temp_path / "main.c"

            # Write test C code
            main_c.write_text(SAMPLE_PIC_CODE)

            # Create build directory
            build_dir = temp_path / "build"
            build_dir.mkdir(exist_ok=True)

            # Try to compile using xc8-wrapper
            try:
                from xc8_wrapper.cli import main as xc8_main

                # Mock sys.argv for xc8-wrapper
                test_args = [
                    "xc8-wrapper",
                    "cc",
                    "--cpu",
                    "PIC16F876A",
                    "--xc8-version",
                    "3.00",
                    "-o",
                    str(build_dir / "main.hex"),
                    str(main_c),
                ]

                with patch.object(sys, "argv", test_args):
                    # Capture any exceptions from compilation
                    try:
                        xc8_main()
                        compilation_success = True
                    except SystemExit as e:
                        compilation_success = e.code == 0
                    except Exception as e:
                        compilation_success = False
                        print(f"Compilation error: {e}")

                # Check if output files were created
                build_dir = temp_path / "build"
                hex_file = build_dir / "main.hex"

                if compilation_success and hex_file.exists():
                    print(f"Compilation successful: {hex_file}")

                    # Verify HEX file content
                    hex_content = hex_file.read_text()
                    assert hex_content.startswith(":"), "HEX file should start with ':'"
                    assert len(hex_content.strip()) > 10, "HEX file should contain data"

                else:
                    # List files in temp directory for debugging
                    print("Files in temp directory:")
                    for file in temp_path.iterdir():
                        print(f"  {file}")

                    if not compilation_success:
                        pytest.fail("Compilation failed")
                    else:
                        pytest.fail("HEX file was not created")

            except ImportError:
                pytest.skip("xc8-wrapper not properly installed")

    @pytest.mark.skipif(
        not is_xc8_installed() and os.environ.get("INSTALL_XC8") != "true",
        reason="XC8 not installed (set INSTALL_XC8=true to enable auto-install)",
    )
    def test_xc8_version_check(self):
        """Test XC8 version checking"""
        if not is_xc8_installed():
            success = install_xc8_if_needed()
            if not success:
                pytest.skip("XC8 installation failed")

        try:
            # Get the detected version
            detected_version = get_installed_xc8_version()

            # Use detected version if available, otherwise try without version
            if detected_version and detected_version != "unknown":
                xc8_path, _ = get_xc8_tool_path("cc", version=detected_version)
            else:
                xc8_path, _ = get_xc8_tool_path("cc")

            # Run version check
            result = subprocess.run(
                [xc8_path, "--version"], capture_output=True, text=True, timeout=30
            )

            assert result.returncode == 0, "XC8 version check should succeed"
            assert "XC8" in result.stdout or "XC8" in result.stderr, (
                "Output should contain 'XC8'"
            )

            print(f"XC8 version output: {result.stdout.strip()}")

        except Exception as e:
            pytest.fail(f"XC8 version check failed: {e}")


@pytest.mark.unit
class TestXC8InstallationIntegration:
    """Test integration with install.py module"""

    def test_is_xc8_installed_function(self):
        """Test that is_xc8_installed function works"""
        # This should not raise an exception
        result = is_xc8_installed()
        assert isinstance(result, bool)

    def test_get_installed_xc8_version_function(self):
        """Test that get_installed_xc8_version function works"""
        # This should not raise an exception
        result = get_installed_xc8_version()
        assert result is None or isinstance(result, str)

    @pytest.mark.skipif(
        os.environ.get("CI") == "true" and os.environ.get("INSTALL_XC8") != "true",
        reason="XC8 installation skipped in CI (set INSTALL_XC8=true to enable)",
    )
    def test_install_xc8_if_needed_function(self):
        """Test that install_xc8_if_needed function works"""
        # This should not raise an exception
        result = install_xc8_if_needed()
        assert isinstance(result, bool)


class TestCoreUtilities:
    """Test core utility functions for better coverage"""

    def test_get_xc8_tool_path_unsupported_tool(self) -> None:
        """Test error handling for unsupported tool"""
        with pytest.raises(ValueError, match="Unsupported XC8 tool"):
            get_xc8_tool_path("invalid_tool", "3.00")

    @patch("xc8_wrapper.core.find_available_xc8_versions")
    def test_get_xc8_tool_path_no_version_or_path(self, mock_find_versions) -> None:
        """Test auto-detection when neither version nor path provided"""
        # Mock available versions for auto-detection
        mock_find_versions.return_value = ["3.00", "2.46"]

        # Should trigger auto-detection
        result = get_xc8_tool_path("cc")
        assert result is not None
        assert len(result) == 2
        path, version = result
        assert isinstance(path, str)
        assert isinstance(version, str)
        assert version == "v3.00"  # Should use the latest version

    @patch("xc8_wrapper.core.find_available_xc8_versions")
    def test_get_xc8_tool_path_no_version_or_path_no_installations(
        self, mock_find_versions
    ) -> None:
        """Test auto-detection when no XC8 installations are found (CI scenario)"""
        # Mock no available versions (CI environment without XC8)
        mock_find_versions.return_value = []

        # Should raise ValueError when no installations found
        with pytest.raises(ValueError, match="No XC8 installation found"):
            get_xc8_tool_path("cc")

    def test_get_xc8_tool_path_invalid_version_format(self) -> None:
        """Test error handling for invalid version format"""
        with pytest.raises(ValueError, match="Invalid version format"):
            get_xc8_tool_path("cc", "3.00; rm -rf /")

    def test_get_xc8_tool_path_invalid_custom_path(self) -> None:
        """Test custom path security validation"""
        # Test path with directory traversal
        with pytest.raises(ValueError, match="Invalid path provided"):
            get_xc8_tool_path("cc", custom_path="../../../bin/xc8-cc")

    def test_get_xc8_tool_path_windows_paths(self) -> None:
        """Test Windows path detection"""
        with patch("sys.platform", "win32"):
            tool_path, version_info = get_xc8_tool_path("cc", "3.00")
            assert "xc8-cc.exe" in tool_path
            assert "v3.00" == version_info
            assert "Program Files" in tool_path

    def test_get_xc8_tool_path_macos_paths(self) -> None:
        """Test macOS path detection"""
        with patch("sys.platform", "darwin"):
            tool_path, version_info = get_xc8_tool_path("cc", "3.00")
            assert "xc8-cc" in tool_path
            assert "v3.00" == version_info
            # Use normalized paths to handle Windows vs Unix separators
            normalized_path = tool_path.replace("\\", "/")
            assert (
                "/Applications/microchip" in normalized_path
                or "/opt/microchip" in normalized_path
            )

    def test_get_xc8_tool_path_linux_paths(self) -> None:
        """Test Linux path detection"""
        with patch("sys.platform", "linux"):
            tool_path, version_info = get_xc8_tool_path("cc", "3.00")
            assert "xc8-cc" in tool_path
            assert "v3.00" == version_info

    def test_validate_xc8_tool_not_found(self) -> None:
        """Test validation when tool doesn't exist"""
        from xc8_wrapper.core import validate_xc8_tool

        result = validate_xc8_tool("/nonexistent/path/xc8-cc", "cc", "v3.00")
        assert not result

    def test_validate_xc8_tool_custom_path_not_found(self) -> None:
        """Test validation when custom path doesn't exist"""
        from xc8_wrapper.core import validate_xc8_tool

        result = validate_xc8_tool("/custom/path/xc8-cc", "cc", "custom path")
        assert not result

    def test_run_command_empty_command(self) -> None:
        """Test run_command with empty command"""
        from xc8_wrapper.core import run_command

        result = run_command([], "test command")
        assert not result

    def test_run_command_unauthorized_executable(self) -> None:
        """Test run_command with unauthorized executable"""
        from xc8_wrapper.core import run_command

        result = run_command(["/bin/rm", "-rf", "/"], "dangerous command")
        assert not result

    def test_run_command_timeout_exception(self) -> None:
        """Test run_command timeout handling"""
        from xc8_wrapper.core import run_command

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 300)):
            result = run_command(["sleep", "1000"], "timeout test")
            assert not result

    def test_run_command_general_exception(self) -> None:
        """Test run_command general exception handling"""
        from xc8_wrapper.core import run_command

        with patch("subprocess.run", side_effect=Exception("Test error")):
            result = run_command(["echo", "test"], "error test")
            assert not result

    def test_validate_path_security_valid_paths(self) -> None:
        """Test path security validation with valid paths"""
        from xc8_wrapper.core import _validate_path_security

        # These should be considered safe
        safe_paths = [
            "/opt/microchip/xc8/v3.00/bin/xc8-cc",
            "C:\\Program Files\\Microchip\\xc8\\v3.00\\bin\\xc8-cc.exe",
            "/Applications/microchip/xc8/v3.00/bin/xc8-cc",
        ]

        for path in safe_paths:
            assert _validate_path_security(path), f"Path should be valid: {path}"

    def test_validate_path_security_invalid_paths(self) -> None:
        """Test path security validation with invalid paths"""
        from xc8_wrapper.core import _validate_path_security

        # These should be considered unsafe due to path traversal patterns
        unsafe_paths = [
            "../../../bin/xc8-cc",
            "/opt/microchip/../../../bin/rm",
            "C:\\..\\..\\Windows\\System32\\cmd.exe",
        ]

        for path in unsafe_paths:
            assert not _validate_path_security(path), f"Path should be invalid: {path}"

    def test_handle_cc_tool_missing_version_and_path(self) -> None:
        """Test handle_cc_tool when version and path are missing"""
        from xc8_wrapper.core import handle_cc_tool

        # Mock args object
        class MockArgs:
            xc8_version = None
            xc8_path = None
            cpu = "PIC16F877A"
            files = ["test.c"]
            output = "test.hex"

            # Add other required attributes with default values
            def __getattr__(self, name):
                return None

        args = MockArgs()

        # This should handle missing version gracefully
        with patch("xc8_wrapper.core.get_xc8_tool_path") as mock_get_path:
            mock_get_path.side_effect = ValueError("No XC8 installation found")

            with pytest.raises(SystemExit):
                handle_cc_tool(args)
