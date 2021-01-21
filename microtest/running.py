"""
Author: Valtteri Rajalainen
Edited: 21.1.2021
"""

import sys
import os
import pathlib

from microtest.scanner import execute_module, find_tests
from microtest.logger import TestLogger


def run_from_commandline():
    """
    Run the scanner and execute all found modules
    with the commandline arguments.
    """
    arguments = sys.argv[1:]
    settings = {
        '-v':TestLogger().set_verbose,
        '--verbose':TestLogger().set_verbose,
        '-m':TestLogger().set_minimal,
        '--minimal':TestLogger().set_minimal,
    }
    if len(arguments) > 0:
        cwd_path = pathlib.Path(os.getcwd())
        path = cwd_path.joinpath(arguments.pop(-1)).resolve()
        #process extra args here
        for setting in settings.keys():
            if setting in arguments:
                settings[setting]()
        if path.exists():
            run(path)


def run(path):
    """
    Run the scanner from the given path
    and execute all found modules.
    """
    TestLogger().root_path = path
    modules_to_test = find_tests(path)
    for module_path in modules_to_test:
        execute_module(module_path)

