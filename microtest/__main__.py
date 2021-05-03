"""
Commandline entrypoint for testing.

Author: Valtteri Rajalainen
Edited: 3.5.2021
"""

import sys
import microtest.running as runner

if __name__ == '__main__':
   runner.run_from_commandline(sys.argv[1:])

