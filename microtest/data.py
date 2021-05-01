from dataclasses import dataclass
from typing import Any


@dataclass
class Output:
    MINIMAL = 'minimal'
    VERBOSE = 'verbose'
    DEFAULT = 'default'


@dataclass
class TestCase:
    func: str
    success: bool
    exception: Exception = None


@dataclass
class Colors:
    OK_GREEN = '\033[92m'
    FAILED_RED = '\033[91m'
    INFO_CYAN = '\033[96m'
    RESET = '\033[0m'


"""
Task types:

START -> Testing started, logger will show start info based on output mode.
         Data is None.

STOP -> Testing halted.
        Data is an dictionary with the following entries:
            > 'errors':int
            > 'tests':int
            > 't_start':float
            > 't_stop':float

TEST -> A new testcase was executed.
        Data is an instance of TestCase.
"""

class Task:
    
    START = 'start'
    STOP = 'stop'
    TEST = 'test'

    def __init__(self, type_, data=None):
        self.type_ = type_
        self.data = data

    @property
    def type(self):
        return self.type_