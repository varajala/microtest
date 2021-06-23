"""
Common objects used across different modules.

Author: Valtteri Rajalainen
Edited: 23.6.2021
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Output:
    MINIMAL = 'minimal'
    VERBOSE = 'verbose'
    DEFAULT = 'default'


@dataclass
class Colors:
    OK_GREEN = '\033[92m'
    FAILED_RED = '\033[91m'
    INFO_CYAN = '\033[96m'
    RESET = '\033[0m'


@dataclass
class Result:
    OK = 'OK'
    FAILED = 'FAILED'
    ERROR = 'ERROR'


@dataclass
class Module:
    path: str
    logged: bool = False
    tests = dict()



class Namespace:
    def __init__(self):
        object.__setattr__(self, 'data', dict())

    def __getattribute__(self, attr):
        data = object.__getattribute__(self, 'data')
        if attr not in self:
            raise AttributeError(f'No memeber "{attr}" in namespace')
        return data[attr]

    def __setattr__(self, attr, value):
        object.__getattribute__(self, 'data').__setitem__(attr, value)

    def __contains__(self, item):
        data = object.__getattribute__(self, 'data')
        return item in data.keys()


class ExecutionContext:
    def __init__(self):
        self.on_exit = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.on_exit:
            return self.on_exit(exc_type, exc, tb)