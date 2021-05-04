"""
Author: Valtteri Rajalainen
Edited: 4.5.2021
"""

import sys
import os
import traceback

from microtest.data import *

class Logger:
    
    def __init__(self, output_mode=Output.DEFAULT, out=sys.stdout):
        self.mode = output_mode
        self.out = out
        self.width = 75
        if out.isatty():
            self.use_colors = True
        #redirect sys.stderr to NULL
        #sys.stderr = open(os.devnull, 'w') 


    def write_out(self, text, color=None):
        if not self.use_colors or color is None:
            self.out.write(text)
            return
        
        self.out.write(color)
        self.out.write(text)
        self.out.write(Colors.RESET)
        self.out.flush()


    def write_separator(self, char, separation=1):
        out.write((self.width // separation) * char)
        out.write('\n')


    def write_traceback(self, exc):
        exc_type = type(exc)
        tb = exc.__traceback__
        traceback_lines = traceback.format_exception(exc_type, exc, tb)
        for line in traceback_lines[5:]:
            print(line)


    def log_test_info(self, func_name, result, exc):
        self.write_out(func_name)
        padding = self.width - len(func_name) - len(result)
        self.write_out(' ' + padding * '.' + ' ')
        color = Colors.OK_GREEN if result == Result.OK else Colors.FAILED_RED
        self.write_out(result + '    \n', color)


    def log_module_exec_error(self, module_path, exc):
        self.write_out(f'Execution failed: {exc.__class__.__name__}\n', Colors.FAILED_RED)
        self.write_traceback(exc)


    def log_module_info(self, module_path):
        self.write_out(module_path + '\n', Colors.INFO_CYAN)


    def terminate(self):
        sys.stderr.close()
        sys.stderr = sys.__stderr__


    def __del__(self):
        self.terminate()