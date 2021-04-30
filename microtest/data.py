from dataclasses import dataclass
from typein import Any


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


class Task:
    
    START = 'start'
    STOP = 'stop'
    TEST = 'test'

    def __init__(self, type_, data):
        self.type_ = type_
        self.data = data

    @property
    def type(self):
        return self.type_