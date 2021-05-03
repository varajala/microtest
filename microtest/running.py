"""
Author: Valtteri Rajalainen
Edited: 3.5.2021
"""

import os
import sys
import runpy
import threading

import microtest.scanner as scanner
import microtest.logger as logger
import microtest.core as core
from microtest.data import *


EXEC_NAME = '__main__'


def run(root_path):
    """
    Run the scanner from the given path
    and execute all found modules.
    """
    path = os.path.abspath(root_path)
    modules = (path,)
    if os.path.isdir(path):
        modules = scanner.find_tests(path)
        if not modules:
            sys.stdout.write(f'No tests executed.\n')
            return

    logger_thread = threading.Thread(target=logger.run, args=(core.logger_queue,))
    logger_thread.start()

    core.start_testing()
    
    for module_path in modules:
        try:
            runpy.run_path(module_path, run_name=EXEC_NAME)
        
        except KeyboardInterrupt:
            break

        except SystemExit:
            break

        except Exception as exc:
            core.register_module_exec_error(module_path, exc)

    core.stop_testing()
    logger_thread.join()


def verbose_output():
    logger.output_mode = Output.VERBOSE

def minimal_output():
    logger.output_mode = Output.MINIMAL


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

    run(path)
