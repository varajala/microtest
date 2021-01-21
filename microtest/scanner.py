"""
Script for finding all tests in a directory and its children.

Author: Valtteri Rajalainen
Edited: 21.1.2021
"""

import os
import runpy
import pathlib

from microtest.logger import TestLogger


def find_tests(root_path):
    """
    Find all test directories starting from root_path
    and return a tuple of found modules. The path given
    has to be pathlib.Path object.

    TODO: handle permission errors
    """
    modules = []
    dirs_to_scan = [root_path]
    while dirs_to_scan:
        dir_path = dirs_to_scan.pop(0)
        for entry in os.scandir(dir_path):
            if entry.is_dir():
                if is_test_dir(entry.path):
                    dirs_to_scan.append(entry.path)
            elif is_python_module(entry.name):
                modules.append(pathlib.Path(entry.path))
    return tuple(modules)


def is_test_dir(path):
    return '__test__.py' in os.listdir(path)


def is_python_module(filename):
    return filename.endswith('.py')


def execute_module(path, exec_name='__main__'):
    logger = TestLogger()
    logger.add_module(path)
    try:
        runpy.run_path(path, run_name=exec_name)
    except Exception as exc:
        logger.log_module_execution_error(exc, path)