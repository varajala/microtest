"""
Author: Valtteri Rajalainen
"""

import os
import sys
import traceback
import types

import microtest.scanner as scanner
import microtest.core as core

from microtest.data import Namespace
from microtest.logging import DefaultLogger
from microtest.api import *


def set_logger(obj):
    if core.running:
        info = 'Can\'t set logger while executing tests. This must be done during configuration'
        raise RuntimeError(info)
    core.logger = obj


context = Namespace()
exec_name = 'microtest_runner'
set_logger(DefaultLogger())


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

    entrypoint = os.environ.get('MICROTEST_ENTRYPOINT', 'main.py')
    if entrypoint in os.listdir(path):
        core.run_config(os.path.join(path, entrypoint), exec_name)

    core.exec_modules(modules, exec_name)

