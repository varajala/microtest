from dataclasses import dataclass
from typing import Any, Dict


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
class ModuleExecError:
    path: str
    exception: Exception


@dataclass
class StopInfo:
    errors: int
    tests: int
    t_start: float
    t_stop: float
    modules: Dict[str, TestCase] = None


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
        Data is an instance of StopInfo.
        Providing modules is optional.

TEST -> A new testcase was executed.
        Data is an instance of TestCase.

EXEC_ERR -> An exception during the execution of a module.
            Data is an instance of ModuleExecError.

LOG_INFO -> Print message to stdout. Data is a string.
"""

class Task:
    
    START = 'start'
    STOP = 'stop'
    TEST = 'test'
    EXEC_ERR = 'exec_err'
    LOG_INFO = 'log'

    def __init__(self, type_, data=None):
        self.type_ = type_
        self.data = data

    @property
    def type(self):
        return self.type_