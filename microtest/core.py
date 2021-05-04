import timeit
import atexit

from typing import List, Dict
from queue import Queue
from microtest.data import *
from microtest.logger import Logger

modules = dict()
errors: int = 0
failed: int = 0
tests: int = 0
t_start: float = None
t_end: float = None
init = False
#main = False
logger = Logger()


def stop_testing():
    global t_start, t_stop
    
    t_stop = timeit.default_timer()
    delta = round(t_stop - t_start, 3)

    logger.log_results(tests, failed, errors, delta)
    logger.terminate()
    

def register_test(module_path, func, exc):
    global failed, errors, tests, t_start, init
    if not init:
        t_start = timeit.default_timer()
        init = True
        atexit.register(stop_testing)
    
    tests += 1
    result = Result.OK
    if exc:
        exc_name = exc.__class__.__name__
        result = Result.FAILED if exc_name == 'AssertionError' else Result.ERROR
        if exc_name == 'AssertionError':
            failed += 1
        else:
            errors += 1

    if module_path not in modules:
        logger.log_module_info(module_path)
        modules[module_path] = list()

    func_name = func.__qualname__
    
    modules[module_path].append((func_name, result, exc))
    logger.log_test_info(func_name, result, exc)


def register_module(module_path):
    if module_path not in modules:
        logger.log_module_info(module_path)
        modules[module_path] = list()


def register_module_exec_error(module_path, exc_type, exc, tb):
    global errors
    errors += 1
    logger.log_module_exec_error(module_path, exc_type, exc, tb)