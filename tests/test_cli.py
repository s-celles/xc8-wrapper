"""
Tests for CLI module

Test suite for the command-line interface functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from xc8_wrapper.cli import create_argument_parser, main


class TestArgumentParser:
    """Test argument parser creation and functionality"""

    def test_create_argument_parser(self):
        """Test that argument parser is created correctly"""
        parser = create_argument_parser()
        assert parser is not None
        assert parser.prog == "xc8-wrapper"

    def test_parser_help_contains_version(self):
        """Test that help contains version option"""
        parser = create_argument_parser()
        help_text = parser.format_help()
        assert "--version" in help_text

    def test_parser_default_values(self):
        """Test parser default values"""
        parser = create_argument_parser()
        args = parser.parse_args(["--cpu", "PIC16F876A", "--xc8-version", "3.00"])

        assert args.tool == "cc"
        assert args.build_dir == "build"
        assert args.source_dir == "src"
        assert args.main_c_file == "main.c"
        assert args.output_hex == "main.hex"


class TestMainFunction:
    """Test main function"""

    @patch("xc8_wrapper.cli.handle_cc_tool")
    def test_main_with_cc_tool(self, mock_handle_cc):
        """Test main function with cc tool"""
        mock_handle_cc.return_value = None

        # Test that it doesn't raise an exception
        try:
            main(["--cpu", "PIC16F876A", "--xc8-version", "3.00"])
            mock_handle_cc.assert_called_once()
        except SystemExit:
            # handle_cc_tool might call sys.exit, which is expected
            pass

    @patch("sys.exit")
    def test_main_with_unsupported_tool(self, mock_exit):
        """Test main function with unsupported tool"""
        main(["--tool", "unsupported", "--cpu", "PIC16F876A", "--xc8-version", "3.00"])
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    pytest.main([__file__])
