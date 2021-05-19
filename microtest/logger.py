"""
Author: Valtteri Rajalainen
Edited: 4.5.2021
"""

import sys
import os
import traceback
import re

from microtest.data import *

class Logger:
    
    def __init__(self, output_mode=Output.DEFAULT, out=sys.stdout):
        self.mode = output_mode
        self.out = out
        self.width = 75
        if out.isatty():
            self.use_colors = True


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
        self.write_out(''.join(tb_lines), Colors.FAILED_RED)
        self.write_out('\n')


    def log_start_info(self):
        self.write_separator('=')
        self.write_out('Started testing...\n')
        self.write_separator('=')


    def log_test_info(self, func_name, result, exc):
        self.write_out(func_name)
        padding = self.width - len(func_name) - len(result)
        self.write_out(' ' + padding * '.' + ' ')
        color = Colors.OK_GREEN if result == Result.OK else Colors.FAILED_RED
        self.write_out(result + '    \n', color)

        if result == Result.FAILED:
            tb = exc.__traceback__
            exc_type = type(exc)
            tb_lines = traceback.format_exception(exc_type, exc, tb)
            msg = assertion_introspect(tb_lines[-2])
            self.write_out('-> ' + msg, Colors.FAILED_RED)
            self.write_out('-> ' + tb_lines[-1], Colors.FAILED_RED)
            return

        if result == Result.ERROR:
            self.log_traceback(exc)


    def log_module_exec_error(self, module_path, exc_type, exc, tb):
        self.log_traceback(exc)


    def log_module_info(self, module_path):
        self.write_out('\n' + module_path + '\n', Colors.INFO_CYAN)

    
    def log_results(self, tests, failed, errors, time):
        self.write_out('\n')
        self.write_separator('-')
        self.write_out(f'Ran {tests} tests in {time}s.\n\n')

        if errors == 0 and failed == 0:
            self.write_out('OK.\n', Colors.OK_GREEN)
            return

        self.write_out(f'ERRORS: ', Colors.FAILED_RED)
        self.write_out(str(errors) + '\n')

        self.write_out(f'FAILED: ', Colors.FAILED_RED)
        self.write_out(str(failed) + '\n')

        self.write_out('\n')


    def terminate(self):
        pass



def assertion_introspect(tb_line):
    ln_exp = re.compile(r'(?<=line )\d+')
    ln = re.search(ln_exp, tb_line)[0]

    assertion = ''
    assert_exp = re.compile(r'(?<=assert )[^\n]+')
    match = re.search(assert_exp, tb_line)
    if match:
        assertion = match[0]

    return f'On line {ln}: {assertion}\n'