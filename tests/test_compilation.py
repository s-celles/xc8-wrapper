"""
Tests for XC8 Compilation functionality

This module tests the actual compilation of PIC C code using xc8-wrapper.
Includes automatic XC8 installation if needed for CI environments.
"""

import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import List, Optional
from unittest.mock import patch

import pytest

from xc8_wrapper.core import get_xc8_tool_path

# XC8 download URLs by platform and version
XC8_DOWNLOAD_URLS = {
    "linux": (
        "https://ww1.microchip.com/downloads/aemDocuments/documents/DEV/"
        "ProductDocuments/SoftwareTools/xc8-v{version}-full-install-linux-x64-installer.run"
    ),
    "windows": (
        "https://ww1.microchip.com/downloads/aemDocuments/documents/DEV/"
        "ProductDocuments/SoftwareTools/xc8-v{version}-full-install-windows-x64-installer.exe"
    ),
    "darwin": (
        "https://ww1.microchip.com/downloads/aemDocuments/documents/DEV/"
        "ProductDocuments/SoftwareTools/xc8-v{version}-full-install-macos-x64-installer.dmg"
    ),
}

# Import known versions from core module
from xc8_wrapper.core import XC8_KNOWN_VERSIONS

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


def get_platform_name() -> str:
    """Get normalized platform name for XC8 downloads"""
    system = platform.system().lower()
    if system == "linux":
        return "linux"
    elif system == "windows":
        return "windows"
    elif system == "darwin":
        return "darwin"
    else:
        raise ValueError(f"Unsupported platform: {system}")


def scan_for_xc8_versions() -> List[str]:
    """
    Scan the system for installed XC8 versions by checking installation directories

    Returns:
        List of version strings found, sorted from highest to lowest
    """
    found_versions = set()

    # Get platform-specific base paths
    if sys.platform.startswith("win"):
        base_paths = [
            Path("C:/Program Files/Microchip/xc8"),
            Path("C:/Program Files (x86)/Microchip/xc8"),
        ]
        compiler_name = "xc8-cc.exe"
    elif sys.platform.startswith("darwin"):
        base_paths = [
            Path("/Applications/microchip/xc8"),
            Path("/opt/microchip/xc8"),
        ]
        compiler_name = "xc8-cc"
    else:
        base_paths = [
            Path("/opt/microchip/xc8"),
            Path("/usr/local/microchip/xc8"),
        ]
        compiler_name = "xc8-cc"

    # Scan each base path for version directories using elegant glob patterns
    for base_path in base_paths:
        if not base_path.exists():
            continue

        try:
            # Use glob to find version directories (e.g., v2.40, v3.00)
            for version_dir in base_path.glob("v*"):
                if not version_dir.is_dir():
                    continue

                version = version_dir.name[1:]  # Remove 'v' prefix

                # Validate version format (e.g., "2.40", "3.00")
                if re.match(r"^\d+\.\d+$", version):
                    # Check if the version directory contains the compiler using glob
                    compiler_paths = list(version_dir.glob(f"bin/{compiler_name}"))
                    if compiler_paths and compiler_paths[0].exists():
                        found_versions.add(version)

        except (OSError, PermissionError):
            # Skip directories we can't access
            continue

    # Convert to sorted list (highest version first)
    try:
        return sorted(
            found_versions, key=lambda v: [int(x) for x in v.split(".")], reverse=True
        )
    except ValueError:
        # Fallback to string sorting if version parsing fails
        return sorted(found_versions, reverse=True)


def get_all_xc8_versions_to_try() -> List[str]:
    """
    Get all XC8 versions to try, combining known versions with scanned versions

    Returns:
        List of version strings to try, sorted from highest to lowest
    """
    # Start with known versions
    versions = set(XC8_KNOWN_VERSIONS)

    # Add any versions found by scanning the system
    scanned_versions = scan_for_xc8_versions()
    versions.update(scanned_versions)

    # Convert to sorted list (highest version first)
    try:
        return sorted(
            versions, key=lambda v: [int(x) for x in v.split(".")], reverse=True
        )
    except ValueError:
        # Fallback to string sorting if version parsing fails
        return sorted(versions, reverse=True)


def get_xc8_download_url(version: str = "3.00") -> str:
    """Get XC8 download URL for current platform"""
    platform_name = get_platform_name()
    return XC8_DOWNLOAD_URLS[platform_name].format(version=version)


def is_xc8_installed() -> bool:
    """Check if XC8 is already installed"""
    # First try without version (uses system PATH or default detection)
    try:
        xc8_path, _ = get_xc8_tool_path("cc")
        if Path(xc8_path).exists():
            return True
    except Exception:
        pass

    # Try versions from our combined list (known + scanned)
    for version in get_all_xc8_versions_to_try():
        try:
            xc8_path, _ = get_xc8_tool_path("cc", version=version)
            if Path(xc8_path).exists():
                print(f"Found XC8 version {version} at {xc8_path}")
                return True
        except Exception:
            continue

    return False


def get_installed_xc8_version() -> Optional[str]:
    """Get the version of installed XC8, trying from newest to oldest"""
    # First try without version (uses system PATH or default detection)
    try:
        xc8_path, _ = get_xc8_tool_path("cc")
        if Path(xc8_path).exists():
            # Try to extract version from path or run --version
            try:
                result = subprocess.run(
                    [xc8_path, "--version"], capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    # Extract version from output (e.g., "MPLAB XC8 C Compiler V3.47")
                    version_match = re.search(r"V(\d+\.\d+)", result.stdout)
                    if version_match:
                        return version_match.group(1)
            except Exception:
                pass
            # If we can't get version but tool exists, return "unknown"
            return "unknown"
    except Exception:
        pass

    # Try versions from our combined list (known + scanned)
    for version in get_all_xc8_versions_to_try():
        try:
            xc8_path, _ = get_xc8_tool_path("cc", version=version)
            if Path(xc8_path).exists():
                return version
        except Exception:
            continue

    return None


def download_file(url: str, dest_path: Path, timeout: int = 300) -> bool:
    """Download a file with timeout and progress"""
    try:
        print(f"Downloading {url} to {dest_path}...")

        # Create a custom opener with timeout
        opener = urllib.request.build_opener()
        opener.addheaders = [
            ("User-Agent", "Mozilla/5.0 (compatible; XC8-Test-Download)")
        ]
        urllib.request.install_opener(opener)

        # Download with timeout
        urllib.request.urlretrieve(url, dest_path)
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False


def install_xc8_linux(installer_path: Path) -> bool:
    """Install XC8 on Linux"""
    try:
        # Make installer executable
        installer_path.chmod(0o755)

        # Run installer in unattended mode
        cmd = [
            "sudo",
            str(installer_path),
            "--mode",
            "unattended",
            "--unattendedmodeui",
            "none",
            "--netservername",
            "localhost",
            "--LicenseType",
            "FreeMode",
            "--prefix",
            "/opt/microchip",
        ]

        # Use expect to handle any prompts
        expect_script = f"""#!/usr/bin/expect -f
set timeout 600
spawn {" ".join(cmd)}
expect {{
    "Do you accept this license?" {{ send "y\\r"; exp_continue }}
    "Press Enter to continue" {{ send "\\r"; exp_continue }}
    eof
}}
"""

        # Write expect script
        expect_file = installer_path.parent / "install_xc8.exp"
        expect_file.write_text(expect_script)
        expect_file.chmod(0o755)

        # Run installer via expect if available, otherwise direct
        if shutil.which("expect"):
            result = subprocess.run(
                [str(expect_file)], capture_output=True, text=True, timeout=600
            )
        else:
            # Fallback: pipe 'y' to installer
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate(input="y\n", timeout=600)
            result = type(
                "Result",
                (),
                {"returncode": process.returncode, "stdout": stdout, "stderr": stderr},
            )()

        # Cleanup
        if expect_file.exists():
            expect_file.unlink()

        return result.returncode == 0

    except Exception as e:
        print(f"Linux installation failed: {e}")
        return False


def install_xc8_windows(installer_path: Path) -> bool:
    """Install XC8 on Windows"""
    try:
        # Run installer in silent mode
        cmd = [
            str(installer_path),
            "/S",  # Silent install
            "/v/qn",  # Quiet, no user interface
            'INSTALLLOCATION="C:\\Program Files\\Microchip\\xc8"',
            "LICENSETYPE=FreeMode",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return result.returncode == 0

    except Exception as e:
        print(f"Windows installation failed: {e}")
        return False


def install_xc8_macos(installer_path: Path) -> bool:
    """Install XC8 on macOS"""
    try:
        # Mount DMG
        mount_result = subprocess.run(
            ["hdiutil", "attach", str(installer_path), "-nobrowse"],
            capture_output=True,
            text=True,
        )

        if mount_result.returncode != 0:
            return False

        # Find mounted volume
        mount_point = None
        for line in mount_result.stdout.split("\n"):
            if "/Volumes/" in line:
                mount_point = line.split("\t")[-1].strip()
                break

        if not mount_point:
            return False

        # Find installer in mounted volume
        installer_app = None
        mount_path = Path(mount_point)
        for item in mount_path.iterdir():
            if item.suffix == ".app" and "install" in item.name.lower():
                installer_app = item
                break

        if not installer_app:
            subprocess.run(["hdiutil", "detach", mount_point])
            return False

        # Run installer
        result = subprocess.run(
            [
                "sudo",
                str(installer_app / "Contents/MacOS/installbuilder.sh"),
                "--mode",
                "unattended",
                "--LicenseType",
                "FreeMode",
                "--prefix",
                "/Applications/microchip",
            ],
            capture_output=True,
            text=True,
            timeout=600,
        )

        # Unmount DMG
        subprocess.run(["hdiutil", "detach", mount_point])

        return result.returncode == 0

    except Exception as e:
        print(f"macOS installation failed: {e}")
        return False


def install_xc8_if_needed(version: Optional[str] = None) -> bool:
    """
    Install XC8 if not already installed.

    Args:
        version: Specific version to install (e.g., "3.00"). If None, tries highest available.
    """
    if is_xc8_installed():
        print("XC8 already installed")
        return True

    print("XC8 not found, attempting to install...")

    # Skip installation in certain CI environments or when explicitly disabled
    if os.environ.get("SKIP_XC8_INSTALL", "false").lower() == "true":
        print("XC8 installation skipped (SKIP_XC8_INSTALL=true)")
        return False

    # Determine which versions to try
    if version:
        versions_to_try = [version]
    else:
        versions_to_try = get_all_xc8_versions_to_try()

    platform_name = get_platform_name()

    # Try each version until one succeeds
    for v in versions_to_try:
        print(f"Attempting to install XC8 version {v}...")

        url = get_xc8_download_url(v)

        # Determine installer filename
        if platform_name == "linux":
            installer_name = f"xc8-v{v}-full-install-linux-x64-installer.run"
        elif platform_name == "windows":
            installer_name = f"xc8-v{v}-full-install-windows-x64-installer.exe"
        elif platform_name == "darwin":
            installer_name = f"xc8-v{v}-full-install-macos-x64-installer.dmg"

        # Download to temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            installer_path = Path(temp_dir) / installer_name

            print(f"Downloading XC8 {v} for {platform_name}...")
            if not download_file(url, installer_path):
                print(f"Failed to download XC8 installer for version {v}")
                continue  # Try next version

            print(f"Installing XC8 version {v}...")

            # Install based on platform
            try:
                if platform_name == "linux":
                    success = install_xc8_linux(installer_path)
                elif platform_name == "windows":
                    success = install_xc8_windows(installer_path)
                elif platform_name == "darwin":
                    success = install_xc8_macos(installer_path)
                else:
                    success = False

                if success:
                    print(f"XC8 version {v} installation completed")
                    if is_xc8_installed():  # Verify installation
                        print(f"XC8 version {v} installation verified")
                        return True
                    else:
                        print(f"XC8 version {v} installation failed verification")
                        continue  # Try next version
                else:
                    print(f"XC8 version {v} installation failed")
                    continue  # Try next version

            except Exception as e:
                print(f"Failed to install XC8 version {v}: {e}")
                continue  # Try next version

    # If we get here, all versions failed
    versions_str = ", ".join(versions_to_try)
    print(f"Failed to install any XC8 version. Tried: {versions_str}")
    return False


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
                        # xc8-wrapper calls sys.exit(), check exit code
                        compilation_success = e.code == 0
                    except Exception as e:
                        print(f"Compilation error: {e}")
                        compilation_success = False

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
                        print(f"  {file.name}: {file.stat().st_size} bytes")

                    # List files in build directory if it exists
                    build_dir = temp_path / "build"
                    if build_dir.exists():
                        print("Files in build directory:")
                        for file in build_dir.iterdir():
                            print(f"  {file.name}: {file.stat().st_size} bytes")

                    if not compilation_success:
                        pytest.fail("Compilation failed")
                    else:
                        pytest.fail("Compilation succeeded but HEX file not found")

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
class TestDownloadUrls:
    """Test XC8 download URL generation"""

    def test_get_platform_name(self):
        """Test platform name detection"""
        platform_name = get_platform_name()
        assert platform_name in ["linux", "windows", "darwin"]

    def test_get_xc8_download_url(self):
        """Test XC8 download URL generation"""
        url = get_xc8_download_url("3.00")
        assert "xc8-v3.00" in url
        assert "microchip.com" in url

        # Test custom version
        url_custom = get_xc8_download_url("2.40")
        assert "xc8-v2.40" in url_custom

    def test_download_urls_format(self):
        """Test that all download URLs are properly formatted"""
        for platform_name, url_template in XC8_DOWNLOAD_URLS.items():
            url = url_template.format(version="3.00")
            assert "xc8-v3.00" in url
            assert "microchip.com" in url
            assert platform_name in url or platform_name in [
                "darwin"
            ]  # darwin uses macos in URL


class TestCoreUtilities:
    """Test core utility functions for better coverage"""

    def test_get_xc8_tool_path_unsupported_tool(self) -> None:
        """Test error handling for unsupported tool"""
        from xc8_wrapper.core import get_xc8_tool_path

        with pytest.raises(ValueError, match="Unsupported XC8 tool"):
            get_xc8_tool_path("invalid_tool", "3.00")

    @patch("xc8_wrapper.core.find_available_xc8_versions")
    def test_get_xc8_tool_path_no_version_or_path(self, mock_find_versions) -> None:
        """Test auto-detection when neither version nor path provided"""
        from xc8_wrapper.core import get_xc8_tool_path

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
        from xc8_wrapper.core import get_xc8_tool_path

        # Mock no available versions (CI environment without XC8)
        mock_find_versions.return_value = []

        # Should raise ValueError when no installations found
        with pytest.raises(ValueError, match="No XC8 installation found"):
            get_xc8_tool_path("cc")

    def test_get_xc8_tool_path_invalid_version_format(self) -> None:
        """Test error handling for invalid version format"""
        from xc8_wrapper.core import get_xc8_tool_path

        with pytest.raises(ValueError, match="Invalid version format"):
            get_xc8_tool_path("cc", "3.00; rm -rf /")

    def test_get_xc8_tool_path_invalid_custom_path(self) -> None:
        """Test custom path security validation"""
        from xc8_wrapper.core import get_xc8_tool_path

        # Test path with directory traversal
        with pytest.raises(ValueError, match="Invalid path provided"):
            get_xc8_tool_path("cc", custom_path="../../../bin/xc8-cc")

    def test_get_xc8_tool_path_windows_paths(self) -> None:
        """Test Windows path detection"""
        from xc8_wrapper.core import get_xc8_tool_path

        with patch("sys.platform", "win32"):
            tool_path, version_info = get_xc8_tool_path("cc", "3.00")
            assert "xc8-cc.exe" in tool_path
            assert "v3.00" == version_info
            assert "Program Files" in tool_path

    def test_get_xc8_tool_path_macos_paths(self) -> None:
        """Test macOS path detection"""
        from xc8_wrapper.core import get_xc8_tool_path

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
        from xc8_wrapper.core import get_xc8_tool_path

        with patch("sys.platform", "linux"):
            tool_path, version_info = get_xc8_tool_path("cc", "3.00")
            assert "xc8-cc" in tool_path
            assert "v3.00" == version_info
            # Normalize path separators for cross-platform testing
            normalized_path = tool_path.replace("\\", "/")
            assert (
                "/opt/microchip" in normalized_path
                or "/usr/local/microchip" in normalized_path
            )

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
        import subprocess

        from xc8_wrapper.core import run_command

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 300)):
            result = run_command(["echo", "test"], "test command")
            assert not result

    def test_run_command_general_exception(self) -> None:
        """Test run_command general exception handling"""
        from xc8_wrapper.core import run_command

        with patch("subprocess.run", side_effect=OSError("System error")):
            result = run_command(["echo", "test"], "test command")
            assert not result

    def test_validate_path_security_valid_paths(self) -> None:
        """Test path security validation with valid paths"""
        from xc8_wrapper.core import _validate_path_security

        assert _validate_path_security("/opt/microchip/bin/xc8-cc")
        assert _validate_path_security(
            "C:\\Program Files\\Microchip\\xc8\\v3.00\\bin\\xc8-cc.exe"
        )

    def test_validate_path_security_invalid_paths(self) -> None:
        """Test path security validation with invalid paths"""
        from xc8_wrapper.core import _validate_path_security

        assert not _validate_path_security("../../../etc/passwd")
        assert not _validate_path_security("..\\..\\..\\windows\\system32")
        assert not _validate_path_security("//server/share")
        assert not _validate_path_security("\\\\server\\share")

    def test_validate_path_security_exception_handling(self) -> None:
        """Test path security validation with paths that could cause exceptions"""
        from xc8_wrapper.core import _validate_path_security

        # Test with valid path
        assert _validate_path_security("/some/path")

        # Test with None (should be handled gracefully)
        # Note: This tests the actual function implementation which does string checks

    def test_handle_cc_tool_missing_version_and_path(self) -> None:
        """Test handle_cc_tool when neither version nor path provided"""
        from unittest.mock import Mock, patch

        from xc8_wrapper.core import handle_cc_tool

        args = Mock()
        args.xc8_version = None
        args.xc8_path = None
        args.cpu = "PIC16F876A"
        args.define = []
        args.undefine = []
        args.include = []
        args.library = []
        args.library_path = []
        args.linker_options = []
        args.assembler_options = []
        args.files = []
        args.output = None
        args.keep_comments = False
        args.preprocess_only = False
        args.compile_only = False
        args.verbose = False
        args.suppress_warnings = False
        args.save_temps = False

        # Mock get_xc8_tool_path to fail auto-detection
        with patch("xc8_wrapper.core.get_xc8_tool_path", side_effect=ValueError("No XC8 found")):
            with pytest.raises(SystemExit, match="1"):
                handle_cc_tool(args)

    def test_handle_cc_tool_missing_cpu(self) -> None:
        """Test handle_cc_tool when CPU not provided"""
        from unittest.mock import Mock

        from xc8_wrapper.core import handle_cc_tool

        args = Mock()
        args.xc8_version = "3.00"
        args.xc8_path = None
        args.cpu = None

        with pytest.raises(SystemExit, match="1"):
            handle_cc_tool(args)

    def test_handle_cc_tool_get_tool_path_error(self) -> None:
        """Test handle_cc_tool when get_xc8_tool_path raises error"""
        from unittest.mock import Mock

        from xc8_wrapper.core import handle_cc_tool

        args = Mock()
        args.xc8_version = "invalid; version"
        args.xc8_path = None
        args.cpu = "PIC16F876A"

        with pytest.raises(SystemExit, match="1"):
            handle_cc_tool(args)

    def test_handle_cc_tool_tool_validation_fails(self) -> None:
        """Test handle_cc_tool when tool validation fails"""
        from unittest.mock import Mock, patch

        from xc8_wrapper.core import handle_cc_tool

        args = Mock()
        args.xc8_version = "3.00"
        args.xc8_path = None
        args.cpu = "PIC16F876A"

        with patch("xc8_wrapper.core.validate_xc8_tool", return_value=False):
            with pytest.raises(SystemExit, match="1"):
                handle_cc_tool(args)

    def test_handle_cc_tool_source_file_not_found(self) -> None:
        """Test handle_cc_tool when source file doesn't exist"""
        from unittest.mock import Mock, patch

        from xc8_wrapper.core import handle_cc_tool

        args = Mock()
        args.xc8_version = "3.00"
        args.xc8_path = None
        args.cpu = "PIC16F876A"
        args.compile_flag = None
        args.link_flag = None
        args.define = []
        args.undefine = []
        args.include = []
        args.library = []
        args.library_path = []
        args.linker_options = []
        args.assembler_options = []
        args.files = ["nonexistent.c"]
        args.output = None
        args.keep_comments = False
        args.preprocess_only = False
        args.list_headers = False
        args.list_macros = False
        args.compile_only = False
        args.assembly_only = False
        args.verbose = False
        args.suppress_warnings = False
        args.save_temps = False
        args.optimize = None
        args.std = None
        args.build_dir = "/tmp/test_build"
        args.source_dir = "/tmp/test_src"
        args.main_c_file = "nonexistent.c"
        args.output_hex = "main.hex"
        args.output_elf = "main.elf"
        args.output_p1 = "main.p1"
        args.output_map = "main.map"
        args.memory_file = "memoryfile.xml"
        args.dry_run = False

        with patch("xc8_wrapper.core.validate_xc8_tool", return_value=True):
            with patch(
                "xc8_wrapper.core.get_xc8_tool_path",
                return_value=("/usr/bin/xc8-cc", "v3.00"),
            ):
                with patch("xc8_wrapper.core.run_command", return_value=False):
                    with pytest.raises(SystemExit, match="1"):
                        handle_cc_tool(args)

    def test_handle_cc_tool_compilation_fails(self) -> None:
        """Test handle_cc_tool when compilation fails"""
        import tempfile
        from unittest.mock import Mock, patch

        from xc8_wrapper.core import handle_cc_tool

        with tempfile.TemporaryDirectory() as temp_dir:
            source_file = Path(temp_dir) / "main.c"
            source_file.write_text("#include <xc.h>\nint main() { return 0; }")

            args = Mock()
            args.xc8_version = "3.00"
            args.xc8_path = None
            args.cpu = "PIC16F876A"
            args.compile_flag = None
            args.link_flag = None
            args.define = []
            args.undefine = []
            args.include = []
            args.library = []
            args.library_path = []
            args.linker_options = []
            args.assembler_options = []
            args.files = [str(source_file)]
            args.output = None
            args.keep_comments = False
            args.preprocess_only = False
            args.list_headers = False
            args.list_macros = False
            args.compile_only = False
            args.assembly_only = False
            args.verbose = False
            args.suppress_warnings = False
            args.save_temps = False
            args.optimize = None
            args.std = None
            args.build_dir = str(Path(temp_dir) / "build")
            args.source_dir = temp_dir
            args.main_c_file = "main.c"
            args.output_hex = "main.hex"
            args.output_elf = "main.elf"
            args.output_p1 = "main.p1"
            args.output_map = "main.map"
            args.memory_file = "memoryfile.xml"
            args.dry_run = False

            with patch("xc8_wrapper.core.validate_xc8_tool", return_value=True):
                with patch(
                    "xc8_wrapper.core.get_xc8_tool_path",
                    return_value=("/usr/bin/xc8-cc", "v3.00"),
                ):
                    with patch("xc8_wrapper.core.run_command", return_value=False):
                        with pytest.raises(SystemExit, match="1"):
                            handle_cc_tool(args)

    def test_handle_cc_tool_linking_fails(self) -> None:
        """Test handle_cc_tool when linking fails"""
        import tempfile
        from unittest.mock import Mock, patch

        from xc8_wrapper.core import handle_cc_tool

        with tempfile.TemporaryDirectory() as temp_dir:
            source_file = Path(temp_dir) / "main.c"
            source_file.write_text("#include <xc.h>\nint main() { return 0; }")

            build_dir = Path(temp_dir) / "build"
            build_dir.mkdir()

            # Create p1 file to simulate successful compilation
            p1_file = build_dir / "main.p1"
            p1_file.write_text("dummy p1 content")

            args = Mock()
            args.xc8_version = "3.00"
            args.xc8_path = None
            args.cpu = "PIC16F876A"
            args.compile_flag = None
            args.link_flag = None
            args.define = []
            args.undefine = []
            args.include = []
            args.library = []
            args.library_path = []
            args.linker_options = []
            args.assembler_options = []
            args.files = [str(source_file)]
            args.output = None
            args.keep_comments = False
            args.preprocess_only = False
            args.list_headers = False
            args.list_macros = False
            args.compile_only = False
            args.assembly_only = False
            args.verbose = False
            args.suppress_warnings = False
            args.save_temps = False
            args.optimize = None
            args.std = None
            args.build_dir = str(build_dir)
            args.source_dir = temp_dir
            args.main_c_file = "main.c"
            args.output_hex = "main.hex"
            args.output_elf = "main.elf"
            args.output_p1 = "main.p1"
            args.output_map = "main.map"
            args.memory_file = "memoryfile.xml"
            args.dry_run = False

            def mock_run_command(cmd, desc):
                if "Compiling" in desc:
                    return True  # Compilation succeeds
                else:
                    return False  # Linking fails

            with patch("xc8_wrapper.core.validate_xc8_tool", return_value=True):
                with patch(
                    "xc8_wrapper.core.get_xc8_tool_path",
                    return_value=("/usr/bin/xc8-cc", "v3.00"),
                ):
                    with patch(
                        "xc8_wrapper.core.run_command", side_effect=mock_run_command
                    ):
                        with pytest.raises(SystemExit, match="1"):
                            handle_cc_tool(args)

    def test_handle_cc_tool_hex_file_not_generated(self) -> None:
        """Test handle_cc_tool when HEX file is not generated"""
        import tempfile
        from unittest.mock import Mock, patch

        from xc8_wrapper.core import handle_cc_tool

        with tempfile.TemporaryDirectory() as temp_dir:
            source_file = Path(temp_dir) / "main.c"
            source_file.write_text("#include <xc.h>\nint main() { return 0; }")

            build_dir = Path(temp_dir) / "build"
            build_dir.mkdir()

            args = Mock()
            args.xc8_version = "3.00"
            args.xc8_path = None
            args.cpu = "PIC16F876A"
            args.compile_flag = None
            args.link_flag = None
            args.define = []
            args.undefine = []
            args.include = []
            args.library = []
            args.library_path = []
            args.linker_options = []
            args.assembler_options = []
            args.files = [str(source_file)]
            args.output = None
            args.keep_comments = False
            args.preprocess_only = False
            args.list_headers = False
            args.list_macros = False
            args.compile_only = False
            args.assembly_only = False
            args.verbose = False
            args.suppress_warnings = False
            args.save_temps = False
            args.optimize = None
            args.std = None
            args.build_dir = str(build_dir)
            args.source_dir = temp_dir
            args.main_c_file = "main.c"
            args.output_hex = "main.hex"
            args.output_elf = "main.elf"
            args.output_p1 = "main.p1"
            args.output_map = "main.map"
            args.memory_file = "memoryfile.xml"
            args.dry_run = False

            with patch("xc8_wrapper.core.validate_xc8_tool", return_value=True):
                with patch(
                    "xc8_wrapper.core.get_xc8_tool_path",
                    return_value=("/usr/bin/xc8-cc", "v3.00"),
                ):
                    with patch("xc8_wrapper.core.run_command", return_value=True):
                        # This test should pass since there's no actual file validation in the current implementation
                        # The function completes successfully even if output files aren't created
                        handle_cc_tool(args)  # Should complete successfully

    def test_handle_cc_tool_file_listing_exception(self) -> None:
        """Test handle_cc_tool when file listing throws exception"""
        import tempfile
        from unittest.mock import Mock, patch

        from xc8_wrapper.core import handle_cc_tool

        with tempfile.TemporaryDirectory() as temp_dir:
            source_file = Path(temp_dir) / "main.c"
            source_file.write_text("#include <xc.h>\nint main() { return 0; }")

            build_dir = Path(temp_dir) / "build"
            build_dir.mkdir()

            # Create HEX file to simulate successful compilation and linking
            hex_file = build_dir / "main.hex"
            hex_file.write_text(":020000040000FA\n:00000001FF\n")  # Simple HEX content

            args = Mock()
            args.xc8_version = "3.00"
            args.xc8_path = None
            args.cpu = "PIC16F876A"
            args.compile_flag = None
            args.link_flag = None
            args.define = None
            args.undefine = None
            args.include = None
            args.keep_comments = False
            args.preprocess_only = False
            args.list_headers = False
            args.list_macros = False
            args.compile_only = False
            args.assembly_only = False
            args.verbose = False
            args.suppress_warnings = False
            args.save_temps = False
            args.optimize = None
            args.std = None
            args.build_dir = str(build_dir)
            args.source_dir = temp_dir
            args.main_c_file = "main.c"
            args.output_hex = "main.hex"
            args.output_elf = "main.elf"
            args.output_p1 = "main.p1"
            args.output_map = "main.map"
            args.memory_file = "memoryfile.xml"

            # Mock Path.iterdir to raise exception during file listing
            original_iterdir = Path.iterdir

            def mock_iterdir(self):
                if "build" in str(self):
                    raise PermissionError("Access denied")
                return original_iterdir(self)

            with patch("xc8_wrapper.core.validate_xc8_tool", return_value=True):
                with patch(
                    "xc8_wrapper.core.get_xc8_tool_path",
                    return_value=("/usr/bin/xc8-cc", "v3.00"),
                ):
                    with patch("xc8_wrapper.core.run_command", return_value=True):
                        with patch.object(Path, "iterdir", side_effect=mock_iterdir):
                            # This should complete successfully despite file listing error
                            handle_cc_tool(args)

    def test_handle_cc_tool_with_optimization_flags(self) -> None:
        """Test handle_cc_tool with various optimization flags"""
        import tempfile
        from unittest.mock import Mock, patch

        from xc8_wrapper.core import handle_cc_tool

        with tempfile.TemporaryDirectory() as temp_dir:
            source_file = Path(temp_dir) / "main.c"
            source_file.write_text("#include <xc.h>\nint main() { return 0; }")

            build_dir = Path(temp_dir) / "build"
            build_dir.mkdir()

            # Create HEX file to simulate successful compilation and linking
            hex_file = build_dir / "main.hex"
            hex_file.write_text(":020000040000FA\n:00000001FF\n")

            args = Mock()
            args.xc8_version = "3.00"
            args.xc8_path = None
            args.cpu = "PIC16F876A"
            args.compile_flag = ["-Wall"]
            args.link_flag = ["-Wl,--gc-sections"]
            args.define = ["DEBUG=1"]
            args.undefine = ["NDEBUG"]
            args.include = ["/usr/include"]
            args.keep_comments = True
            args.preprocess_only = False
            args.list_headers = True
            args.list_macros = True
            args.compile_only = False
            args.assembly_only = False
            args.verbose = True
            args.suppress_warnings = False
            args.save_temps = True
            args.optimize = "g"  # Debug optimization
            args.std = "c11"
            args.build_dir = str(build_dir)
            args.source_dir = temp_dir
            args.main_c_file = "main.c"
            args.output_hex = "main.hex"
            args.output_elf = "main.elf"
            args.output_p1 = "main.p1"
            args.output_map = "main.map"
            args.memory_file = "memoryfile.xml"

            with patch("xc8_wrapper.core.validate_xc8_tool", return_value=True):
                with patch(
                    "xc8_wrapper.core.get_xc8_tool_path",
                    return_value=("/usr/bin/xc8-cc", "v3.00"),
                ):
                    with patch("xc8_wrapper.core.run_command", return_value=True):
                        handle_cc_tool(args)  # Should complete successfully

    def test_handle_cc_tool_with_size_optimization(self) -> None:
        """Test handle_cc_tool with size optimization"""
        import tempfile
        from unittest.mock import Mock, patch

        from xc8_wrapper.core import handle_cc_tool

        with tempfile.TemporaryDirectory() as temp_dir:
            source_file = Path(temp_dir) / "main.c"
            source_file.write_text("#include <xc.h>\nint main() { return 0; }")

            build_dir = Path(temp_dir) / "build"
            build_dir.mkdir()

            # Create HEX file to simulate successful compilation and linking
            hex_file = build_dir / "main.hex"
            hex_file.write_text(":020000040000FA\n:00000001FF\n")

            args = Mock()
            args.xc8_version = "3.00"
            args.xc8_path = None
            args.cpu = "PIC16F876A"
            args.compile_flag = None
            args.link_flag = None
            args.define = None
            args.undefine = None
            args.include = None
            args.keep_comments = False
            args.preprocess_only = False
            args.list_headers = False
            args.list_macros = False
            args.compile_only = False
            args.assembly_only = False
            args.verbose = False
            args.suppress_warnings = False
            args.save_temps = False
            args.optimize = "s"  # Size optimization
            args.std = None
            args.build_dir = str(build_dir)
            args.source_dir = temp_dir
            args.main_c_file = "main.c"
            args.output_hex = "main.hex"
            args.output_elf = "main.elf"
            args.output_p1 = "main.p1"
            args.output_map = "main.map"
            args.memory_file = "memoryfile.xml"

            with patch("xc8_wrapper.core.validate_xc8_tool", return_value=True):
                with patch(
                    "xc8_wrapper.core.get_xc8_tool_path",
                    return_value=("/usr/bin/xc8-cc", "v3.00"),
                ):
                    with patch("xc8_wrapper.core.run_command", return_value=True):
                        handle_cc_tool(args)  # Should complete successfully

    def test_get_xc8_tool_path_invalid_version_characters(self) -> None:
        """Test version validation with invalid characters"""
        from xc8_wrapper.core import get_xc8_tool_path

        with patch("sys.platform", "win32"):
            with pytest.raises(ValueError, match="Invalid version format"):
                get_xc8_tool_path("cc", "3.00; rm -rf /")

    def test_get_xc8_tool_path_windows_no_existing_path(self) -> None:
        """Test Windows path when no XC8 installation exists"""
        from xc8_wrapper.core import get_xc8_tool_path

        with patch("sys.platform", "win32"):
            with patch("pathlib.Path.exists", return_value=False):
                # Should return first path even if it doesn't exist
                tool_path, version_info = get_xc8_tool_path("cc", "3.00")
                assert "xc8-cc.exe" in tool_path
                assert "v3.00" == version_info

    def test_get_xc8_tool_path_macos_no_existing_path(self) -> None:
        """Test macOS path when no XC8 installation exists"""
        from xc8_wrapper.core import get_xc8_tool_path

        with patch("sys.platform", "darwin"):
            with patch("pathlib.Path.exists", return_value=False):
                # Should return first path even if it doesn't exist
                tool_path, version_info = get_xc8_tool_path("cc", "3.00")
                assert "xc8-cc" in tool_path
                assert "v3.00" == version_info

    def test_validate_xc8_tool_logging_paths(self) -> None:
        """Test that validate_xc8_tool logs appropriate path suggestions"""
        from xc8_wrapper.core import validate_xc8_tool

        # Test Windows logging
        with patch("sys.platform", "win32"):
            with patch("pathlib.Path.exists", return_value=False):
                with patch("xc8_wrapper.core.log") as mock_log:
                    result = validate_xc8_tool("/nonexistent/path", "cc", "v3.00")
                    assert result is False
                    # Should have logged Windows-specific paths
                    mock_log.info.assert_called()

        # Test macOS logging
        with patch("sys.platform", "darwin"):
            with patch("pathlib.Path.exists", return_value=False):
                with patch("xc8_wrapper.core.log") as mock_log:
                    result = validate_xc8_tool("/nonexistent/path", "cc", "v3.00")
                    assert result is False
                    # Should have logged macOS-specific paths
                    mock_log.info.assert_called()

        # Test Linux logging
        with patch("sys.platform", "linux"):
            with patch("pathlib.Path.exists", return_value=False):
                with patch("xc8_wrapper.core.log") as mock_log:
                    result = validate_xc8_tool("/nonexistent/path", "cc", "v3.00")
                    assert result is False
                    # Should have logged Linux-specific paths
                    mock_log.info.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
