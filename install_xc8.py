#!/usr/bin/env python3
"""
XC8 Installation Helper Script

This script helps install XC8 compiler for testing purposes.
It can be used standalone or as part of the test suite.
"""

import argparse
import sys
from pathlib import Path

# Add the test directory to Python path to import test utilities
sys.path.insert(0, str(Path(__file__).parent / "tests"))

try:
    from test_compilation import (
        get_installed_xc8_version,
        get_platform_name,
        get_xc8_download_url,
        install_xc8_if_needed,
        is_xc8_installed,
    )
except ImportError as e:
    print(f"Error importing test utilities: {e}")
    print("Make sure you're running this from the xc8-wrapper directory")
    sys.exit(1)


def main():
    """Main function for XC8 installation helper"""
    parser = argparse.ArgumentParser(
        description="Install XC8 compiler for testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python install_xc8.py --check                    # Check if XC8 is installed
  python install_xc8.py --install                  # Install XC8 if needed
  python install_xc8.py --install --version 2.40   # Install specific version
  python install_xc8.py --force                    # Force reinstall
  python install_xc8.py --url                      # Show download URL

Environment Variables:
  SKIP_XC8_INSTALL=true    # Skip installation (for CI)
  INSTALL_XC8=true         # Enable installation in CI
        """,
    )

    parser.add_argument(
        "--check", action="store_true", help="Check if XC8 is installed"
    )

    parser.add_argument(
        "--install", action="store_true", help="Install XC8 if not present"
    )

    parser.add_argument(
        "--force", action="store_true", help="Force installation even if XC8 is present"
    )

    parser.add_argument(
        "--version", default="3.00", help="XC8 version to install (default: 3.00)"
    )

    parser.add_argument(
        "--url", action="store_true", help="Show download URL for current platform"
    )

    parser.add_argument(
        "--platform",
        choices=["linux", "windows", "darwin"],
        help="Override platform detection",
    )

    args = parser.parse_args()

    # Handle platform override
    if args.platform:
        import test_compilation

        test_compilation.get_platform_name = lambda: args.platform

    try:
        if args.url:
            platform_name = get_platform_name()
            url = get_xc8_download_url(args.version)
            print(f"Platform: {platform_name}")
            print(f"XC8 v{args.version} download URL:")
            print(url)
            return 0

        if args.check or not (args.install or args.force):
            # Check installation status
            is_installed = is_xc8_installed()
            print(f"XC8 installed: {'✓ Yes' if is_installed else '✗ No'}")

            if is_installed:
                detected_version = get_installed_xc8_version()
                print(f"Detected version: {detected_version}")

                try:
                    from xc8_wrapper.core import get_xc8_tool_path

                    # Use detected version if available, otherwise try without version
                    if detected_version and detected_version != "unknown":
                        xc8_path, _ = get_xc8_tool_path("cc", version=detected_version)
                    else:
                        xc8_path, _ = get_xc8_tool_path("cc")
                    print(f"XC8 path: {xc8_path}")

                    # Try to get version
                    import subprocess  # nosec B404 - Required for XC8 version detection

                    result = subprocess.run(  # nosec B603 - trusted XC8 executable path
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
                        print(f"XC8 version: {version_line.strip()}")

                except Exception as e:
                    print(f"Warning: Could not get XC8 details: {e}")

            return 0 if is_installed else 1

        if args.force:
            print(f"Force installing XC8 v{args.version}...")
            # Temporarily override is_xc8_installed to return False
            import test_compilation

            original_is_installed = test_compilation.is_xc8_installed
            test_compilation.is_xc8_installed = lambda: False

            try:
                success = install_xc8_if_needed(args.version)
            finally:
                test_compilation.is_xc8_installed = original_is_installed
        else:
            print(f"Installing XC8 v{args.version} if needed...")
            success = install_xc8_if_needed(args.version)

        if success:
            print("✓ XC8 installation completed successfully")
            return 0
        else:
            print("✗ XC8 installation failed")
            return 1

    except KeyboardInterrupt:
        print("\nInstallation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
