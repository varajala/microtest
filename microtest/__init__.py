"""
Author: Valtteri Rajalainen
"""

import os
import sys
import traceback

import microtest.scanner as scanner
import microtest.core as core

from microtest.data import Namespace
from microtest.logger import DefaultLogger
from microtest.api import *
import microtest.api


ENTRYPOINT = 'main.py'

__all__ = microtest.api.__all__

context = Namespace()
exec_name = 'microtest_runner'
core.logger = DefaultLogger()


def run_from_commandline(args):
    #handle flags etc...
    path = cwd = os.getcwd()
    if args:
        path = args.pop(-1)
        if not os.path.exists(path):
            sys.stderr.write(f'Invalid path: {path}.\n')
            return
        
        if not os.path.isabs(path):
            path = os.path.join(cwd, path)

    path = os.path.abspath(path)
    if os.path.isfile(path):
        core.exec_modules((path,), exec_name)
        return

    modules = scanner.find_tests(path)
    if not modules:
        sys.stdout.write(f'No modules found.\n')
        return

    if ENTRYPOINT in os.listdir(path):
        core.run_config(os.path.join(path, ENTRYPOINT), exec_name)

    core.exec_modules(modules, exec_name)
