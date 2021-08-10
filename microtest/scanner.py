"""
BFS for the test modules from the given root path.

Author: Valtteri Rajalainen
"""

import os
import re

test_module_regex = r'tests?_\w+\.py|\w+_tests?\.py|tests?\.py'


def find_tests(root_path):
    """
    Find all test directories starting from root_path
    and return a tuple of found modules.
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
    
    return modules


def scan_directory_safely(path):
    """
    Safely scan a directory.
    Returns an empty list if any errors
    occur while scanning the directory.
    """
    result = []
    try:
        result = os.scandir(path)
    except (FileNotFoundError, PermissionError, OSError):
        pass
    return result


def is_test_module(filename):
    try:
        exp = re.compile(test_module_regex)    
    except re.error:
        raise ValueError(f'Failed to compile regex "{test_module_regex}"')
    return re.fullmatch(exp, filename) is not None
        
        