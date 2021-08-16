"""
Common objects used across different modules.

Author: Valtteri Rajalainen
"""

import typing
from types import TracebackType, FunctionType


class Types:
    Function = typing.NewType('function', FunctionType)
    Class = typing.NewType('Class', type)
    Traceback = typing.NewType('Traceback', TracebackType)
    
    Callable = typing.Callable
    Union = typing.Union
    Iterable = typing.Iterable
    Any = typing.Any

    Tuple = typing.Tuple
    List = typing.List


class Output:
    MINIMAL = 'minimal'
    VERBOSE = 'verbose'
    DEFAULT = 'default'


class Result:
    OK = 'OK'
    FAILED = 'FAILED'
    ERROR = 'ERROR'


class Module:
    def __init__(self, path: str):
        self.path = path
        self.tests = list()
        self.fixture = None


class ExecutionContext:
    def __init__(self):
        self.on_exit = list()

    def add_cleanup_operation(self, func, *, final=False):
        if not final:
            self.on_exit.insert(0, func)
        else:
            self.on_exit.append(func)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.on_exit:
            for func in self.on_exit:
                func(exc_type, exc, tb)
