"""
Author: Valtteri Rajalainen
Edited: 26.5.2021
"""

import os
import traceback
import microtest.runner as runner
import microtest.scanner as scanner
import microtest.core as core
from microtest.api import *


def run_from_commandline(args):
    #handle flags etc...
    cwd = os.getcwd()
    path = cwd
    if args:
        path = args.pop(-1)
        if not os.path.exists(path):
            sys.stderr.write(f'Invalid path: {path}.\n')
            return
        
        if not os.path.isabs(path):
            path = os.path.join(cwd, path)
    
    if os.path.isfile(path):
        core.logger.log_start_info()
        runner.run((path,), lambda path, e, et, tb: traceback.print_exception(e, et, tb))
        return

    find_and_exec(path)


def find_and_exec(path):
    modules = scanner.find_tests(path)
    if not modules:
        sys.stdout.write(f'No modules found.\n')
        return
    
    core.logger.log_start_info()
    runner.run(modules, core.register_module_exec_error, core.register_module)