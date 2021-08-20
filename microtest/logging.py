"""
Default logger for microtest.
ANSI coloring on Windows is done via colorama:

https://github.com/tartley/colorama


Author: Valtteri Rajalainen
"""

import sys
import os
import re
import traceback
import io

from typing import NewType

import microtest.assertion as assertion
from microtest.objects import Result, Output, Types


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

    if sys.platform.startswith('win'):
        try:
            import colorama
            colorama.init()
        
        except (ModuleNotFoundError, ImportError):
            info = '\n[ WARNING ]\n'
            info += 'You are running on a Windows platform where ANSI colors are not natively supported.\n'
            info += 'To enable coloring please install the colorama package: \n\n > python -m pip install colorama\n\n'
            sys.stderr.write(info)

            input('Press ENTER to continue... ')
            GREEN = RED = CYAN = RESET = ''


class DefaultLogger:
    
    MAX_WIDTH = 120
    MIN_WIDTH = 60
    DEFAULT_WIDTH = 75

    def __init__(self, output_mode=Output.DEFAULT, out: io.StringIO = sys.stdout):
        self.mode = output_mode
        self.out = out
        self.width = self.DEFAULT_WIDTH
        self.use_colors = False
        
        if out.isatty():
            self.use_colors = True
            cols, _ = os.get_terminal_size()
            self.width = max(self.MIN_WIDTH, min(cols, self.MAX_WIDTH))


    def write(self, text: str, *, color = None):
        if not self.use_colors or color is None:
            self.out.write(text)
            return
        
        self.out.write(color)
        self.out.write(text)
        self.out.write(Colors.RESET)
        self.out.flush()


    def format_separator(self, char: str, separation = 1):
        return (self.width // separation) * char + '\n'


    def format_traceback(self, exc_type, exc, tb):
        tb_lines = traceback.format_exception(exc_type, exc, tb)
        return '\n' + '\n'.join(tb_lines[1:])


    def log_start_info(self):
        self.write(self.format_separator('='))
        self.write('Started testing...\n')
        self.write(self.format_separator('='))


    def log_test_info(self, name: str, result: str, exc: Exception):
        padding = self.width - len(name) - len(result) - 3
        self.write(name)
        self.write(' ' + padding * '.' + ' ')
        self.write(result  + '\n', color = Colors.GREEN if result == Result.OK else Colors.RED)

        if exc:
            tb = exc.__traceback__
            exc_type = type(exc)

        if result == Result.FAILED:
            self.write(assertion.resolve_assertion_error(exc_type, exc, tb), color = Colors.RED)
            return

        if result == Result.ERROR:
            self.write(f'\nTraceback:\n', color=Colors.RED)
            self.write(self.format_traceback(exc_type, exc, tb), color = Colors.RED)
            return


    def log_module_exec_error(self, module_path: str, exc_type: Types.Class, exc: Exception, tb: Types.Traceback):
        self.write('\nTraceback for error raised during module execution:\n', color=Colors.RED)
        self.write(self.format_traceback(exc_type, exc, tb), color=Colors.RED)


    def log_module_info(self, module_path: str):
        self.write('\n' + module_path + '\n', color = Colors.CYAN)

    
    def log_results(self, tests: int, failed: int, errors: int, time: float):
        self.write('\n')
        self.write(self.format_separator('-'))
        self.write(f'Ran {tests} tests in {time}s.\n\n')

        if errors == 0 and failed == 0:
            self.write('OK.\n\n', color = Colors.GREEN)
            return

        self.write(f'ERRORS: ', color = Colors.RED)
        self.write(str(errors) + '\n')

        self.write(f'FAILED: ', color = Colors.RED)
        self.write(str(failed) + '\n')
        self.write('\n')


    def terminate(self):
        pass

