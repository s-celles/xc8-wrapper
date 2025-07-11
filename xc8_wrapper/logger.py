"""
Logging configuration with colorama and logbook
"""

import sys

from colorama import Fore, Style, init
from logbook import Logger, StreamHandler

init()  # Initialize colorama


class ColoredFormatter:
    def __init__(self):
        self.colors = {
            "DEBUG": Fore.CYAN,
            "INFO": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "CRITICAL": Fore.MAGENTA,
        }

    def format(self, record):
        color = self.colors.get(record.level_name, "")
        return f"{record.time:%H:%M:%S} {color}[{record.level_name}]{Style.RESET_ALL} {record.message}"


# Create logger
log = Logger("XC8Wrapper")

# Setup handler with custom formatter
handler = StreamHandler(sys.stdout)
formatter = ColoredFormatter()
handler.formatter = lambda record, handler: formatter.format(record)
handler.push_application()
