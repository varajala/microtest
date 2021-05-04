import timeit

from typing import List, Dict
from queue import Queue
from microtest.data import *
from microtest.logger import Logger

modules = dict()
errors: int = 0
tests: int = 0
t_start: float = None
t_end: float = None
running = False
logger = Logger()


def start_testing():
    global t_start, running

    t_start = timeit.default_timer()
    running = True


def stop_testing():
    global t_start, t_stop
    t_stop = timeit.default_timer()
    running = False
    

def register_test(module_path, func, exc):
    global errors, tests
    tests += 1

    if exc:
        errors += 1

    if module_path not in modules:
        logger.log_module_info(module_path)
        modules[module_path] = list()

    func_name = func.__qualname__
    result = Result.OK
    if exc is not None:
        exc_name = exc.__class__.__name__
        result = Result.FAILED if exc_name == 'AssertionError' else Result.ERROR
    modules[module_path].append((func_name, result, exc))
    logger.log_test_info(func_name, result, exc)


def register_module_exec_error(module_path, exc):
    global errors
    errors += 1
    logger.log_module_exec_error(module_path, exc)