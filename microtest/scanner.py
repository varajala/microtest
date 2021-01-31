"""
Script for finding all tests in a directory and its children.

Author: Valtteri Rajalainen
Edited: 31.1.2021
"""

import os
import pathlib

from microtest.logger import TestLogger


ID_FILE = '__test__.py'


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
        for entry in scan_directory_safely(dir_path):
            if entry.is_dir():
                if is_test_dir(entry.path):
                    dirs_to_scan.append(entry.path)
            elif is_python_module(entry.name):
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


def is_test_dir(path):
    """Check if directory contains the ID_FILE."""
    listed_dir = []
    try:
        listed_dir = os.listdir(path)
    except (FileNotFoundError, PermissionError, OSError):
        pass
    return ID_FILE in listed_dir


def is_python_module(filename):
    return filename.endswith('.py')
        
        