import timeit

from typing import List, Dict

modules: Dict[str, List[TestCase]] = []
errors: int = 0 
tests: int = 0
t_start: float = None
t_end: float = None


def start_testing():
    global t_start
    t_start = timeit.default_timer()


def stop_testing():
    global t_start, t_stop
    t_stop = timeit.default_timer()
    delta = t_stop - t_start


def register_test(module_path, func, exc):
    global errors
    tests += 1

    if module_path not in modules:
        modules[module_path] = list()

    test_obj = TestCase(func.__qualname__, exc is None, exc)
    modules[module_path].append(test_obj)
    #log executed function, module, etc...

    if exc:
        error_type = exception.__class__.__name__
        errors += 1
        #log exception traceback
        #depending on mode etc...


def register_module_exec_error(module_path, exc):
    global errors
    errors += 1

    #log exec error