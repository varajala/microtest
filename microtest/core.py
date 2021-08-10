"""
Stateful component of microtest.

Author: Valtteri Rajalainen
"""

import timeit
import inspect
import runpy
import os
import sys

from typing import Iterable

from microtest.data import *


exec_context = ExecutionContext()
resources = dict()
utilities = dict()

modules = dict()
logger = None
running = False
config_in_process = False

errors: int = 0
failed: int = 0
tests: int = 0

t_start: float = None
t_end: float = None

exclude_modules = set()
included_modules = set()

exclude_groups = set()
included_groups = set()

abort = False


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


class _FixtureObject:
    pass


class _FuncWrapper:
    def __init__(self, func):
        self.func = func

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            func = object.__getattribute__(self, 'func')
            return object.__getattribute__(func, attr)


class _TestObject(_FuncWrapper):
    def __init__(self, func, module_path):
        super().__init__(func)
        self.module_path = module_path
        self.group = None


def generate_signature(obj):
    func_obj = None
    if inspect.isfunction(obj):
        func_obj = obj

    if issubclass(obj.__class__, _FuncWrapper):
        func_obj = obj.func

    if func_obj is None:
        print(obj, obj.__class__)
        info = 'Cannot generate signature for object that is not '
        info += 'a function or microtest.core._FuncWrapper subclass instance.'
        raise TypeError(info)
    
    signature = inspect.signature(func_obj)
    return [ param for param in signature.parameters ]
    

def call_with_resources(func):
    kwargs = dict()
    signature = generate_signature(func)
    for item in signature:
        if item not in resources.keys():
            raise NameError(f'Undefined resource "{item}"')
        kwargs[item] = resources[item]
    return func(**kwargs)


def add_resource(name, obj):
    resources[name] = obj


def add_utility(name, obj):
    utilities[name] = obj


def on_exit(func):
    exec_context.on_exit.insert(0, func)


def while_running(func):
    """
    Wrapper function to ensure proper initialization before execution.
    """
    def wrapper(*args, **kwargs):
        if not running:
            initialize()
        return func(*args, **kwargs)
    return wrapper


def filter_tests(namespace: dict) -> Iterable:
    """
    Find testcases and possible Fixture inside the module namespace.
    Filter the found testcases based on their group.

    If included_groups is not empty only those groups will be executed,
    even if exclude_groups is not empty.
    
    If exclude_groups is not empty these groups will be filtered out.
    """
    tests = [ item for item in namespace.values() if issubclass(type(item), _TestObject) ]
    
    if included_groups:
        tests = list(filter(lambda test: test.group in included_groups, tests))
    elif exclude_groups:
        tests = list(filter(lambda test: test.group not in exclude_groups, tests))

    for item in namespace.values():
        if issubclass(type(item), _FixtureObject):
            item.testcases = tests
            return item
    return tests


def filter_modules(modules: tuple) -> tuple:
    """
    Filter the executed modules based on inlcuded_modules and exclude_modules.

    These sets can contain restrictions as strings representing filepaths or parts of filepaths.
    If the restriction is an absolute filepath the paths are comapred with '=='.
    Otherwise the comaprison will be 'restriction in path' (path is an absolute filepath).

    If included_modules is not empty only those modules will be executed,
    even if exclude_modules is not empty.
    
    If exclude_modules is not empty these modules will be filtered out.
    """
    filtered_modules = list(modules)

    def path_meets_restriction(module_path: str, restriction: str) -> bool:
        if os.path.isabs(restriction):
            return module_path == restriction
        return restriction in module_path

    if included_modules:
        filtered_modules = list()
        for restriction in included_modules:
            for module_path in modules:
                if path_meets_restriction(module_path, restriction):
                    filtered_modules.append(module_path)
    
    elif exclude_modules:
        for restriction in exclude_modules:
            for module_path in modules:
                if not path_meets_restriction(module_path, restriction):
                    filtered_modules.append(module_path)
    
    return tuple(filtered_modules)


def initialize():
    global running, t_start
    if logger is None or not issubclass(type(logger), Logger):
        info = 'Invalid configuration. No logger or invalid logger interface'
        raise ValueError(info)
    
    logger.log_start_info()
    t_start = timeit.default_timer()
    exec_context.on_exit.append(stop_testing)
    running = True


def stop_testing(*args):
    global t_start, t_stop
    if not running:
        return
    
    t_stop = timeit.default_timer()
    delta = round(t_stop - t_start, 3)

    logger.log_results(tests, failed, errors, delta)
    logger.terminate()


def collect_test(module_path, test_obj):
    module = modules.get(module_path, None)
    if module is None:
        module = Module(module_path)
        modules[module_path] = module
        if running:
            logger.log_module_info(module_path)
            module.logged = True
    
    module.tests.append(test_obj)


@while_running
def register_test_results(module_path, func, exc):
    global failed, errors, tests
    result = Result.OK
    tests += 1
    if exc:
        result = Result.FAILED if isinstance(exc, AssertionError) else Result.ERROR
        if result == Result.FAILED:
            failed += 1
        else:
            errors += 1
    
    module = modules.get(module_path, None)
    if module and not module.logged:
        logger.log_module_info(module_path)
        module.logged = True

    logger.log_test_info(func.__qualname__, result, exc)


@while_running
def register_module_exec_error(module_path, exc_type, exc, tb):
    global errors, init, t_start
    errors += 1
    logger.log_module_exec_error(module_path, exc_type, exc, tb)


@while_running
def exec_modules(module_paths, exec_name):
    global abort
    with exec_context:
        for module_path in filter_modules(module_paths):
            if module_path not in modules:
                module = modules[module_path] = Module(module_path)
                logger.log_module_info(module_path)
                module.logged = True
            
            try:
                namespace = runpy.run_path(module_path, init_globals=utilities, run_name=exec_name)
                if abort:
                    abort = False
                    continue
                
                module.tests = filter_tests(namespace)
                for test in module.tests:
                    call_with_resources(test)

            except KeyboardInterrupt:
                break

            except SystemExit:
                break

            except Exception as exc:
                exc_type = type(exc)
                traceback = exc.__traceback__
                register_module_exec_error(module_path, exc_type, exc, traceback)


def run_current_module():
    if running or config_in_process:
        return
    
    initialize()
    
    with exec_context:
        modules_list = list(modules.values())
        if len(modules_list) == 0:
            return

        module = modules_list.pop(0)
        if not module.tests:
            return
        
        namespace = module.tests[0].func.__globals__
        for test in filter_tests(namespace):
            call_with_resources(test)


def run_config(path, exec_name):
    global config_in_process
    config_in_process = True
    try:
        runpy.run_path(path, run_name=exec_name)

    finally:
        config_in_process = False
