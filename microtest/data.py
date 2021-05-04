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