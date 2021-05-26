"""
Commandline entrypoint for testing.

Author: Valtteri Rajalainen
Edited: 26.5.2021
"""

import sys
from microtest import run_from_commandline


if __name__ == '__main__':
   run_from_commandline(sys.argv[1:])

