import timeit
import atexit

from typing import List, Dict
from queue import Queue
from microtest.data import *


modules = dict()
running = False
logger = None

errors: int = 0
failed: int = 0
tests: int = 0

t_start: float = None
t_end: float = None


class Logger:

    required_methods = (
        'log_start_info',
        'log_module_info',
        'log_test_info',
        'log_module_exec_error',
        'log_results',
        'terminate',
    )

    def __init_subclass__(cls):
        object.__init_subclass__()
        cls_members = [ member for member in dir(cls) if not member.startswith('_') ]
        for method_name in Logger.required_methods:
            if method_name not in cls_members:
                raise TypeError(f'Invalid Logger implementation. Missing method "{method_name}"')


def while_running(func):
    def wrapper(*args, **kwargs):
        global running, t_start
        if not running:
            if logger is None or not issubclass(type(logger), Logger):
                info = 'Invalid configuration. No logger or invalid logger interface'
                raise ValueError(info)
            logger.log_start_info()
            t_start = timeit.default_timer()
            atexit.register(stop_testing)
            running = True
        return func(*args, **kwargs)
    return wrapper


def stop_testing():
    global t_start, t_stop
    
    t_stop = timeit.default_timer()
    delta = round(t_stop - t_start, 3)

    logger.log_results(tests, failed, errors, delta)
    logger.terminate()


def list_tests():
    results = []
    for module in modules.values():
        results.extend(list(module.values()))
    return results


@while_running
def collect_test(module_path, test_obj):
    if module_path not in modules:
        register_module(module_path)
    
    test = Namespace()
    test.result = None
    test.executed = False
    test.obj = test_obj
    
    testcases = modules[module_path]
    testcases[test_obj.func.__qualname__] = test


@while_running
def register_test_results(module_path, func, exc):
    global failed, errors, tests
    tests += 1
    result = Result.OK
    if exc:
        exc_name = exc.__class__.__name__
        result = Result.FAILED if exc_name == 'AssertionError' else Result.ERROR
        if exc_name == 'AssertionError':
            failed += 1
        else:
            errors += 1
    
    testcases = modules[module_path]
    test = testcases[func.__qualname__]
    test.executed = True
    test.result = result
    print(func.__name__, result, exc)
    logger.log_test_info(func.__qualname__, result, exc)


@while_running
def register_module(module_path):
    if module_path not in modules:
        logger.log_module_info(module_path)
        modules[module_path] = dict()


@while_running
def register_module_exec_error(module_path, exc_type, exc, tb):
    global errors, init, t_start
    errors += 1
    logger.log_module_exec_error(module_path, exc_type, exc, tb)
