"""
Script for finding all tests in a directory and its children.

Author: Valtteri Rajalainen
Edited: 31.1.2021
"""

import os
import pathlib
import re

from microtest.logger import TestLogger


def find_tests(root_path):
    """
    Find all test directories starting from root_path
    and return a tuple of found modules. The path given
    has to be pathlib.Path object.
    """
    modules = []
    dirs_to_scan = [root_path]
    while dirs_to_scan:
        dir_path = dirs_to_scan.pop(0)
        for entry in scan_directory_safely(dir_path):
            if entry.is_dir():
                dirs_to_scan.append(entry.path)
            elif is_test_module(entry.name):
                modules.append(pathlib.Path(entry.path))
    return tuple(modules)


def scan_directory_safely(path):
    """
    Safely scan a directory.
    Returns an emty list if any errors
    occur while scanning the directory.
    """
    result = []
    try:
        result = os.scandir(path)
    except (FileNotFoundError, PermissionError, OSError):
        pass
    return result


def is_test_module(filename):
    TEST_MODULE_EXP = re.compile(r'tests?_\w+\.py|\w+_tests?\.py|tests?\.py')
    match = re.fullmatch(TEST_MODULE_EXP, filename)
    return match is not None
        
        