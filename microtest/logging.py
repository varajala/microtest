"""
Default logger for microtest.

Author: Valtteri Rajalainen
"""

import sys
import os
import re
import traceback
import io

import microtest.assertion as assertion

from microtest.data import *

class DefaultLogger:
    
    MAX_WIDTH = 120
    MIN_WIDTH = 60
    DEFAULT_WIDTH = 75

    def __init__(self, output_mode=Output.DEFAULT, out: io.StringIO = sys.stdout):
        self.mode = output_mode
        self.out = out
        self.width = self.DEFAULT_WIDTH
        
        if out.isatty():
            self.use_colors = True
            cols, _ = os.get_terminal_size()
            self.width = max(self.MIN_WIDTH, min(cols, self.MAX_WIDTH))


    def write_out(self, text, color=None):
        if not self.use_colors or color is None:
            self.out.write(text)
            return
        
        self.out.write(color)
        self.out.write(text)
        self.out.write(Colors.RESET)
        self.out.flush()


    def write_separator(self, char, separation=1):
        self.out.write((self.width // separation) * char)
        self.out.write('\n')


    def log_traceback(self, exc):
        tb = exc.__traceback__
        exc_type = type(exc)
        tb_lines = traceback.format_exception(exc_type, exc, tb)
        self.write_out('\n')
        self.write_out(''.join(tb_lines), Colors.RED)
        self.write_out('\n')


    def log_start_info(self):
        self.write_separator('=')
        self.write_out('Started testing...\n')
        self.write_separator('=')


    def log_test_info(self, name, result, exc):
        self.write_out(name)
        padding = self.width - len(name) - len(result) - 3
        self.write_out(' ' + padding * '.' + ' ')
        color = Colors.GREEN if result == Result.OK else Colors.RED
        self.write_out(result + '\n', color)

        if result == Result.FAILED:
            tb = exc.__traceback__
            exc_type = type(exc)
            msg = assertion.resolve_assertion_error(exc_type, exc, tb)
            self.write_out(msg, Colors.RED)
            return

        if result == Result.ERROR:
            self.log_traceback(exc)


    def log_module_exec_error(self, module_path, exc_type, exc, tb):
        self.log_traceback(exc)


    def log_module_info(self, module_path):
        self.write_out('\n' + module_path + '\n', Colors.CYAN)

    
    def log_results(self, tests, failed, errors, time):
        self.write_out('\n')
        self.write_separator('-')
        self.write_out(f'Ran {tests} tests in {time}s.\n\n')

        if errors == 0 and failed == 0:
            self.write_out('OK.\n\n', Colors.GREEN)
            return

        self.write_out(f'ERRORS: ', Colors.RED)
        self.write_out(str(errors) + '\n')

        self.write_out(f'FAILED: ', Colors.RED)
        self.write_out(str(failed) + '\n')

        self.write_out('\n')


    def terminate(self):
        pass
