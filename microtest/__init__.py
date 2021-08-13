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


CONFIG_SCRIPT_ENV_VARIABLE = 'MICROTEST_ENTRYPOINT'
DEFAULT_CONFIG_SCRIPT = 'main.py'


def set_logger(obj):
    if core.running:
        info = 'Can\'t set logger while executing tests. This must be done during configuration'
        raise RuntimeError(info)
    core.logger = obj


def set_module_discovery_regex(regex):
    scanner.test_module_regex = regex


context = Namespace()
exec_name = 'microtest_runner'
set_logger(DefaultLogger())


def run_from_commandline(args):
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

    config_file = os.environ.get(CONFIG_SCRIPT_ENV_VARIABLE, DEFAULT_CONFIG_SCRIPT)
    if not os.path.isabs(config_file):
        config_file = os.path.join(path, config_file)
    
    if os.path.exists(config_file):
        core.run_config(config_file, exec_name)

    core.exec_modules(scanner.find_tests(path), exec_name)

