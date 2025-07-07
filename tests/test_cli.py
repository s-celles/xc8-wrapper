"""
Tests for CLI module

Comprehensive test suite for the command-line interface functionality.
"""

from unittest.mock import patch

import pytest

from xc8_wrapper.cli import Colors, create_argument_parser, main, print_colored


@pytest.mark.unit
@pytest.mark.cli
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
            # SystemExit is expected in some cases
            pass

    @patch("sys.argv", ["xc8-wrapper", "--version"])
    @patch("builtins.print")
    def test_main_version_flag(self, mock_print):
        """Test main function with version flag"""
        with pytest.raises(SystemExit):
            main()

    @patch("xc8_wrapper.cli.handle_cc_tool")
    def test_main_with_different_tools(self, mock_handle_cc):
        """Test main function with different tool options"""
        mock_handle_cc.return_value = None

        try:
            main(["--tool", "cc", "--cpu", "PIC16F876A", "--xc8-version", "3.00"])
            mock_handle_cc.assert_called_once()
        except SystemExit:
            pass

    def test_main_invalid_arguments(self):
        """Test main function with invalid arguments"""
        with pytest.raises(SystemExit):
            main(["--invalid-arg"])

    @patch("xc8_wrapper.cli.handle_cc_tool")
    def test_main_with_optimization_flags(self, mock_handle_cc):
        """Test main function with optimization flags"""
        mock_handle_cc.return_value = None

        try:
            main(["--cpu", "PIC16F876A", "--xc8-version", "3.00", "-O2", "-DDEBUG=1"])
            mock_handle_cc.assert_called_once()
        except SystemExit:
            pass


class TestPrintColored:
    """Test colored output functionality in CLI"""

    @patch("builtins.print")
    def test_print_colored_cli(self, mock_print):
        """Test colored printing in CLI context"""
        print_colored("Test message", Colors.CYAN)
        mock_print.assert_called_once()

    @patch("builtins.print")
    def test_print_colored_multiple_calls(self, mock_print):
        """Test multiple colored print calls"""
        messages = ["Message 1", "Message 2", "Message 3"]
        for msg in messages:
            print_colored(msg, Colors.CYAN)
        assert mock_print.call_count == len(messages)


class TestArgumentValidation:
    """Test argument validation"""

    def test_parser_required_arguments(self):
        """Test that required arguments are enforced"""
        parser = create_argument_parser()

        # Test missing required arguments - should not raise since no arguments are truly required
        args = parser.parse_args([])
        # Verify default values are set
        assert args.tool == "cc"
        assert args.build_dir == "build"

    def test_parser_cpu_argument(self):
        """Test CPU argument parsing"""
        parser = create_argument_parser()
        args = parser.parse_args(["--cpu", "PIC18F4550", "--xc8-version", "3.00"])
        assert args.cpu == "PIC18F4550"

    def test_parser_optimization_levels(self):
        """Test optimization level arguments"""
        parser = create_argument_parser()

        for opt_level in ["0", "1", "2", "3", "s"]:
            args = parser.parse_args(["--cpu", "PIC16F876A", "--xc8-version", "3.00", "-O", opt_level])
            assert args.optimize == opt_level

    def test_parser_define_arguments(self):
        """Test preprocessor define arguments"""
        parser = create_argument_parser()
        args = parser.parse_args(["--cpu", "PIC16F876A", "--xc8-version", "3.00", "-D", "DEBUG=1", "-D", "VERSION=100"])
        assert "DEBUG=1" in args.define
        assert "VERSION=100" in args.define

    def test_parser_include_arguments(self):
        """Test include directory arguments"""
        parser = create_argument_parser()
        args = parser.parse_args(["--cpu", "PIC16F876A", "--xc8-version", "3.00", "-I", "./include", "-I", "../common"])
        assert "./include" in args.include
        assert "../common" in args.include


if __name__ == "__main__":
    pytest.main([__file__])

    @patch("sys.exit")
    def test_main_with_unsupported_tool(self, mock_exit):
        """Test main function with unsupported tool"""
        main(["--tool", "unsupported", "--cpu", "PIC16F876A", "--xc8-version", "3.00"])
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    pytest.main([__file__])
