"""
Author: Valtteri Rajalainen
Edited: 26.5.2021
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


__all__ = ['context', 'run'] + microtest.api.__all__

context = Namespace()
core.logger = DefaultLogger()

ENTRYPOINT = 'main.py'


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
        core.run_modules((path,))
        return

    modules = scanner.find_tests(path)
    if not modules:
        sys.stdout.write(f'No modules found.\n')
        return

    if ENTRYPOINT in os.listdir(path):
        modules.insert(0, os.path.join(path, ENTRYPOINT))

    core.run_modules(modules)


def run():
    core.run()