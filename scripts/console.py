from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass
from typing import TextIO


RESET = '\033[0m'


class Color:
    MAGENTA = '\033[95m'
    CYAN = '\033[36m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'


@dataclass(frozen=True)
class ColorShortcut:
    color: str
    stream: TextIO = sys.stdout

    def __call__(self, message: str) -> None:
        write(message, self.color, stream=self.stream)


TASK = ColorShortcut(Color.MAGENTA)
INFO = ColorShortcut(Color.CYAN)
SUCCESS = ColorShortcut(Color.GREEN)
WARNING = ColorShortcut(Color.YELLOW)
ERROR = ColorShortcut(Color.RED, stream=sys.stderr)

OK = SUCCESS
WARN = WARNING
ERR = ERROR

task = TASK
info = INFO
success = SUCCESS
warning = WARNING
error = ERROR


def write(message: str, color: str, *, stream: TextIO = sys.stdout) -> None:
    if supports_color(stream):
        print(f'{color}{message}{RESET}', file=stream)
        return

    print(message, file=stream)


def supports_color(stream: TextIO) -> bool:
    if os.environ.get('NO_COLOR'):
        return False

    if not hasattr(stream, 'isatty') or not stream.isatty():
        return False

    if sys.platform == 'win32':
        return enable_windows_ansi()

    return True


def enable_windows_ansi() -> bool:
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)

    if handle in (0, -1):
        return False

    mode = ctypes.c_uint()
    if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        return False

    return bool(kernel32.SetConsoleMode(handle, mode.value | 0x0004))
