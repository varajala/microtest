"""
Author: Valtteri Rajalainen
Edited: 4.3.2021
"""

import sys
import os
import pathlib
import runpy

from microtest.scanner import find_tests
from microtest.logger import TestLogger


EXEC_NAME = '__main__'


def run(root_path):
    """
    Run the scanner from the given path
    and execute all found modules.
    """
    modules_to_test = find_tests(root_path)
    for module_path in modules_to_test:
        execute_module(module_path)


def execute_module(path, exec_name=EXEC_NAME):
    logger = TestLogger()
    logger.add_module(path)
    try:
        runpy.run_path(path, run_name=exec_name)
    except Exception as exc:
        logger.module_execution_error(exc)


def run_from_commandline():
    """
    Run the scanner and execute all found modules
    with the commandline arguments.
    """
    ARGUMENTS = {
    '-m':TestLogger().minimal_output,
    '--minimal':TestLogger().minimal_output,
    '-v':TestLogger().verbose_output,
    '--verbose':TestLogger().verbose_output,
    }
    arguments = sys.argv[1:]
    if len(arguments) > 0:
        cwd_path = pathlib.Path(os.getcwd())
        path = cwd_path.joinpath(arguments.pop(-1)).resolve()
        while arguments:
            arg = arguments.pop(0)
            if arg not in ARGUMENTS:
                continue
            ARGUMENTS[arg]()
        if path.exists():
            run(path)
            