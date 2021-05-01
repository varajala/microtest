import timeit

from typing import List, Dict
from queue import Queue
from microtest.data import *

modules: Dict[str, List[TestCase]] = dict()
errors: int = 0 
tests: int = 0
t_start: float = None
t_end: float = None

logger_queue = Queue()


def start_testing():
    global t_start
    task = Task(Task.START)
    logger_queue.put(task)
    t_start = timeit.default_timer()


def stop_testing():
    global t_start, t_stop
    t_stop = timeit.default_timer()
    data = {
        'errors':errors,
        'tests':tests,
        't_start':t_start,
        't_stop':t_stop
    }
    task = Task(Task.STOP, data)
    logger_queue.put(task)


def register_test(module_path, func, exc):
    global errors, tests
    tests += 1

    if exc:
        errors += 1

    if module_path not in modules:
        modules[module_path] = list()

    test_obj = TestCase(func.__qualname__, exc is None, exc)
    modules[module_path].append(test_obj)
    
    task = Task(Task.TEST, test_obj)
    logger_queue.put(task)


def register_module_exec_error(module_path, exc):
    global errors
    errors += 1
    #log exec error