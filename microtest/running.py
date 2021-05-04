"""
Author: Valtteri Rajalainen
Edited: 3.5.2021
"""

import os
import sys
import runpy

import microtest.scanner as scanner
import microtest.logger as logger
import microtest.core as core
from microtest.data import *


def run(modules, on_error, exec_name='__main__'):
    for module_path in modules:
        try:
            runpy.run_path(module_path, run_name=exec_name)
        
        except KeyboardInterrupt:
            break

        except SystemExit:
            break

        except Exception as exc:
            exc_type = type(exc)
            traceback = exc.__traceback__
            on_error(exc_type, exc, traceback)


'''
def run_from_commandline(args):
    flags = {
        '-m':minimal_output,
        '--minimal':minimal_output,
        '-v':verbose_output,
        '--verbose':verbose_output,
    }

    cwd = os.getcwd()
    path = cwd
    if args:
        path = args.pop(-1)
        if not os.path.exists(path):
            sys.stderr.write(f'Invalid path: {path}.\n')
            return
        
        if not os.path.isabs(path):
            path = os.path.join(cwd, path)

    for arg in args:
        if arg in flags:
            func = flags[arg]
            func()

    path = os.path.abspath(root_path)
    modules = (path,)
    if os.path.isdir(path):
        modules = scanner.find_tests(path)
        if not modules:
            sys.stdout.write(f'No tests executed.\n')
            return
'''