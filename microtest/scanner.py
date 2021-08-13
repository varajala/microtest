"""
Test module discovery implementation.

Author: Valtteri Rajalainen
"""

import os
import re
from typing import Iterable


test_module_regex = r'tests?_\w+\.py|\w+_tests?\.py|tests?\.py'


def find_tests(root_path: str) -> tuple:
    """
    Do a BFS over the directory structure and add all
    filepaths that sadisfy the is_test_module check.
    """
    modules = []
    dirs_to_scan = [root_path]
    
    while dirs_to_scan:
        dir_path = dirs_to_scan.pop(0)
        for entry in scan_directory_safely(dir_path):
            if entry.is_dir():
                dirs_to_scan.append(entry.path)
            
            elif is_test_module(entry.name):
                modules.append(entry.path)
    
    return tuple(modules)


def scan_directory_safely(path: str) -> Iterable:
    """
    Safely scan a directory.
    Returns an empty iterator if any errors
    occur while scanning the directory.
    """
    result = iter(list())
    try:
        result = os.scandir(path)
    except (FileNotFoundError, PermissionError, OSError):
        pass
    return result


def is_test_module(filename: str):
    try:
        exp = re.compile(test_module_regex)    
    except re.error:
        raise ValueError(f'Failed to compile regex "{test_module_regex}"')
    return re.fullmatch(exp, filename) is not None
