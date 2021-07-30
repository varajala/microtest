"""
Common objects used across different modules.

Author: Valtteri Rajalainen
"""

from dataclasses import dataclass
from typing import Any, Dict
import sys


@dataclass
class Output:
    MINIMAL = 'minimal'
    VERBOSE = 'verbose'
    DEFAULT = 'default'


@dataclass
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

    if sys.platform.startswith('win'):
        try:
            import colorama
            colorama.init()
        
        except (ModuleNotFoundError, ImportError):
            info = '\n[ WARNING ]\n'
            info += 'You are running on a Windows platform where ANSI colors are not natively supported.\n'
            info += 'To enable coloring please install the colorama package: \n\n > python -m pip install colorama\n\n'
            sys.stderr.write(info)

            input('Press ENTER to continue... ')
            GREEN = RED = CYAN = RESET = ''


@dataclass
class Result:
    OK = 'OK'
    FAILED = 'FAILED'
    ERROR = 'ERROR'


@dataclass
class Module:
    path: str
    logged: bool = False
    tests = list()


class Namespace:
    def __init__(self, items=dict()):
        object.__setattr__(self, 'items', items)

    def __getattribute__(self, attr):
        items = object.__getattribute__(self, 'items')
        if attr not in self:
            raise AttributeError(f'No memeber "{attr}" in namespace')
        return items[attr]

    def __setattr__(self, attr, value):
        object.__getattribute__(self, 'items').__setitem__(attr, value)

    def __contains__(self, item):
        items = object.__getattribute__(self, 'items')
        return item in items.keys()


class ExecutionContext:
    def __init__(self):
        self.on_exit = list()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.on_exit:
            for func in self.on_exit:
                func(exc_type, exc, tb)
