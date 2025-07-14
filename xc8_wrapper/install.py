"""
XC8 Installation Module

This module handles XC8 installation functionality integrated into the main CLI.
"""

import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import List, Optional

from .logger import log

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
from .core import XC8_KNOWN_VERSIONS


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


def get_xc8_download_url(version: str) -> str:
    """Get download URL for XC8 version and current platform"""
    platform_name = get_platform_name()
    return XC8_DOWNLOAD_URLS[platform_name].format(version=version)


def get_all_xc8_versions_to_try() -> List[str]:
    """Get list of XC8 versions to try, in order of preference"""
    return XC8_KNOWN_VERSIONS.copy()


def is_xc8_installed() -> bool:
    """Check if XC8 is installed and accessible"""
    try:
        from .core import get_xc8_tool_path
        get_xc8_tool_path("cc")
        return True
    except Exception:
        return False


def get_installed_xc8_version() -> str:
    """Get the version of the installed XC8 compiler"""
    try:
        from .core import get_xc8_tool_path
        xc8_path, _ = get_xc8_tool_path("cc")
        
        # Try to get version
        result = subprocess.run(
            [xc8_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            version_line = (
                result.stdout.split("\n")[0]
                if result.stdout
                else result.stderr.split("\n")[0]
            )
            # Extract version number from output like "XC8 C Compiler V3.00"
            import re
            match = re.search(r'[Vv]?(\d+\.\d+)', version_line)
            if match:
                return match.group(1)
        return "unknown"
    except Exception:
        return "unknown"


def download_file(url: str, destination: Path) -> bool:
    """Download file from URL to destination path"""
    try:
        log.info(f"Downloading from: {url}")
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                log.error(f"HTTP error {response.status} downloading XC8 installer")
                return False
            
            total_size = response.headers.get('Content-Length')
            if total_size:
                total_size = int(total_size)
                log.info(f"File size: {total_size / 1024 / 1024:.1f} MB")
            
            with open(destination, 'wb') as f:
                shutil.copyfileobj(response, f)
            
        log.info(f"Downloaded to: {destination}")
        return True
    except Exception as e:
        log.error(f"Error downloading file: {e}")
        return False


def install_xc8_linux(installer_path: Path) -> bool:
    """Install XC8 on Linux"""
    try:
        # Make installer executable
        installer_path.chmod(0o755)
        
        # Run installer with --mode unattended
        result = subprocess.run(
            [str(installer_path), "--mode", "unattended"],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes timeout
        )
        
        if result.returncode == 0:
            log.info("XC8 installation completed successfully")
            return True
        else:
            log.error(f"XC8 installation failed with return code {result.returncode}")
            if result.stderr:
                log.error(f"Installation error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        log.error("XC8 installation timed out")
        return False
    except Exception as e:
        log.error(f"Error during XC8 installation: {e}")
        return False


def install_xc8_windows(installer_path: Path) -> bool:
    """Install XC8 on Windows"""
    try:
        # Run installer with /S for silent mode
        result = subprocess.run(
            [str(installer_path), "/S"],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes timeout
        )
        
        if result.returncode == 0:
            log.info("XC8 installation completed successfully")
            return True
        else:
            log.error(f"XC8 installation failed with return code {result.returncode}")
            if result.stderr:
                log.error(f"Installation error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        log.error("XC8 installation timed out")
        return False
    except Exception as e:
        log.error(f"Error during XC8 installation: {e}")
        return False


def install_xc8_macos(installer_path: Path) -> bool:
    """Install XC8 on macOS"""
    try:
        # Mount DMG first
        mount_result = subprocess.run(
            ["hdiutil", "attach", str(installer_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        
        if mount_result.returncode != 0:
            log.error("Failed to mount XC8 DMG")
            return False
        
        # Find the mounted volume
        mount_point = None
        for line in mount_result.stdout.split('\n'):
            if '.dmg' in line and '/Volumes/' in line:
                mount_point = line.split('\t')[-1].strip()
                break
        
        if not mount_point:
            log.error("Could not find mounted XC8 volume")
            return False
        
        # Find installer package
        installer_pkg = None
        for item in Path(mount_point).iterdir():
            if item.suffix == '.pkg':
                installer_pkg = item
                break
        
        if not installer_pkg:
            log.error("Could not find XC8 installer package in DMG")
            return False
        
        # Run installer
        result = subprocess.run(
            ["sudo", "installer", "-pkg", str(installer_pkg), "-target", "/"],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes timeout
        )
        
        # Unmount DMG
        subprocess.run(["hdiutil", "detach", mount_point], capture_output=True)
        
        if result.returncode == 0:
            log.info("XC8 installation completed successfully")
            return True
        else:
            log.error(f"XC8 installation failed with return code {result.returncode}")
            if result.stderr:
                log.error(f"Installation error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        log.error("XC8 installation timed out")
        return False
    except Exception as e:
        log.error(f"Error during XC8 installation: {e}")
        return False


def install_xc8_if_needed(version: Optional[str] = None, force: bool = False) -> bool:
    """
    Install XC8 if not already installed.

    Args:
        version: Specific version to install (e.g., "3.00"). If None, tries highest available.
        force: Force installation even if XC8 is already installed
    """
    if not force and is_xc8_installed():
        log.info("XC8 already installed")
        return True

    log.info("XC8 not found, attempting to install...")

    # Skip installation in certain CI environments or when explicitly disabled
    if os.environ.get("SKIP_XC8_INSTALL", "false").lower() == "true":
        log.warning("XC8 installation skipped (SKIP_XC8_INSTALL=true)")
        return False

    # Determine which versions to try
    if version:
        versions_to_try = [version]
    else:
        versions_to_try = get_all_xc8_versions_to_try()

    platform_name = get_platform_name()

    # Try each version until one succeeds
    for v in versions_to_try:
        log.info(f"Attempting to install XC8 version {v}...")

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

            log.info(f"Downloading XC8 {v} for {platform_name}...")
            if not download_file(url, installer_path):
                log.error(f"Failed to download XC8 installer for version {v}")
                continue  # Try next version

            log.info(f"Installing XC8 version {v}...")

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
                    log.info(f"XC8 version {v} installation completed")
                    if is_xc8_installed():  # Verify installation
                        log.info(f"XC8 version {v} installation verified")
                        return True
                    else:
                        log.warning(f"XC8 version {v} installation failed verification")
                        continue  # Try next version
                else:
                    log.error(f"XC8 version {v} installation failed")
                    continue  # Try next version

            except Exception as e:
                log.error(f"Failed to install XC8 version {v}: {e}")
                continue  # Try next version

    # If we get here, all versions failed
    versions_str = ", ".join(versions_to_try)
    log.error(f"Failed to install any XC8 version. Tried: {versions_str}")
    return False


def check_xc8_installation() -> dict:
    """Check XC8 installation status and return detailed information"""
    is_installed = is_xc8_installed()
    result = {"installed": is_installed}
    
    if is_installed:
        detected_version = get_installed_xc8_version()
        result["version"] = detected_version
        
        try:
            from .core import get_xc8_tool_path
            # Use detected version if available, otherwise try without version
            if detected_version and detected_version != "unknown":
                xc8_path, _ = get_xc8_tool_path("cc", version=detected_version)
            else:
                xc8_path, _ = get_xc8_tool_path("cc")
            result["path"] = xc8_path
            
            # Try to get version string
            result_proc = subprocess.run(
                [xc8_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result_proc.returncode == 0:
                version_line = (
                    result_proc.stdout.split("\n")[0]
                    if result_proc.stdout
                    else result_proc.stderr.split("\n")[0]
                )
                result["version_string"] = version_line.strip()

        except Exception as e:
            result["error"] = str(e)
    
    return result
