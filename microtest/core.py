"""
Stateful component of microtest.

Author: Valtteri Rajalainen
"""

import timeit
import inspect
import runpy
import os
import sys
import functools

from typing import Iterable

from microtest.data import *


exec_context = ExecutionContext()
resources = dict()
utilities = dict()

logger = None
current_module = None

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


logger_interface = (
    ('log_start_info', list()),
    ('log_module_info', ['module_path']),
    ('log_test_info', ['name', 'result', 'exc']),
    ('log_module_exec_error', ['module_path', 'exc_type', 'exc', 'tb']),
    ('log_results', ['tests', 'failed', 'errors', 'time']),
    ('terminate', list())
    )


def capture_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        error = None
        try:
            func(*args, **kwargs)
        except Exception as exc:
            error = exc
        return error
    return wrapper


class _TestObject:
    def __init__(self, func):
        self.func = func
        self.group = None

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError as err:
            try:
                func = object.__getattribute__(self, 'func')
                return object.__getattribute__(func, attr)
            except AttributeError:
                raise err

    def __call__(self, *args, **kwargs):
        error = None
        try:
            self.func(*args, **kwargs)
        
        except Exception as exc:
            error = exc
        
        register_test_results(self, error)
        return error


class Fixture:

    def __init__(self):
        self._setup = None
        self._cleanup = None
        self._reset = None
        
        self.setup_done = False
        self.tests = list()
        self.error = None


    def append(self, test):
        self.tests.append(test)


    def register_setup(self, func):
        if self._setup:
            info = 'Setup function is already set for this module'
            raise RuntimeError()
        self._setup = capture_exception(func)


    def register_cleanup(self, func):
        if self._cleanup:
            info = 'Cleanup function is already set for this module'
            raise RuntimeError()
        self._cleanup = capture_exception(func)


    def register_reset(self, func):
        if self._reset:
            info = 'Reset function is already set for this module'
            raise RuntimeError()
        self._reset = capture_exception(func)


    def __iter__(self):
        return self


    def __next__(self):
        if not self.setup_done:
            self.do_setup()
        
        if self.error:
            raise StopIteration

        if self.tests:
            return self.wrap_test(self.tests.pop(0))
        
        self.do_cleanup()
        raise StopIteration


    def wrap_test(self, func):
        @functools.wraps(func)
        def wrapper(**kwargs):
            if self._reset:
                error = call_with_resources(self._reset)
                if error:
                    self.abort_with_error(error)
            return func(**kwargs)
        return wrapper


    def do_setup(self):
        self.setup_done = True
        if self._setup:
            error = call_with_resources(self._setup)
            if error:
                self.abort_with_error(error, do_cleanup=False)


    def do_cleanup(self):
        if self._cleanup:
            error = call_with_resources(self._cleanup)
            if error:
                self.abort_with_error(error, do_cleanup=False)

    
    def abort_with_error(self, error, *, do_cleanup=True):
        self.error = error
        if do_cleanup:
            self.do_cleanup()
        raise error


def generate_signature(obj):
    func_obj = None
    if inspect.isfunction(obj) or inspect.ismethod(obj):
        func_obj = obj

    if isinstance(obj, _TestObject):
        func_obj = obj.func

    if func_obj is None:
        info = 'Cannot generate signature for object that is not '
        info += 'a function, method or microtest.core._TestObject instance.'
        raise TypeError(info)
    
    signature = inspect.signature(func_obj)
    return [ param for param in signature.parameters ]


def check_logger_object(obj: object):
    for requirement in logger_interface:
        method_name, signature = requirement
        if not hasattr(obj, method_name):
            info = f'Invalid Logger implementation: Expected Logger to have attribute "{method_name}"'
            raise TypeError(info)
        
        method_obj = getattr(obj, method_name)
        if not hasattr(method_obj, '__call__'):
            info = f'Invalid Logger implementation: Attribute "{method_name}" is not callable'
            raise TypeError(info)
        
        method_obj_signature = generate_signature(method_obj)
        if method_obj_signature != signature:
            info = ''.join([
                'Invalid Logger implementation: ',
                f'Signature of "{method_name}" doesn\'t match the interface requirement.\n\n',
                f'{method_obj_signature} != {signature}'
                ])
            raise TypeError(info)
    
    return True
    

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
    exec_context.add_cleanup_operation(func)


def require_init(func):
    """
    Wrapper function to ensure proper initialization before execution.
    """
    def wrapper(*args, **kwargs):
        if not running:
            initialize()
        return func(*args, **kwargs)
    return wrapper


def filter_tests(module: Module) -> Iterable:
    tests = module.tests.copy()
    if included_groups:
        tests = list(filter(lambda test: test.group in included_groups, module.tests))
    
    elif exclude_groups:
        tests = list(filter(lambda test: test.group not in exclude_groups, module.tests))

    if module.fixture:
        module.fixture.tests = tests
        return module.fixture
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
        return tuple(filtered_modules)
    
    filtered_modules = list(modules)
    
    for restriction in exclude_modules:
        removed = 0
        for index, module_path in enumerate(modules):
            if path_meets_restriction(module_path, restriction):
                filtered_modules.pop(index - removed)
                removed += 1
    
    return tuple(filtered_modules)


def initialize():
    global running, t_start
    check_logger_object(logger)
    
    running = True
    logger.log_start_info()
    t_start = timeit.default_timer()
    exec_context.add_cleanup_operation(stop_testing, final=True)


def stop_testing(*args):
    global t_start, t_stop
    if not running:
        return
    
    t_stop = timeit.default_timer()
    delta = round(t_stop - t_start, 3)

    logger.log_results(tests, failed, errors, delta)
    logger.terminate()


def collect_test(test_obj):
    global current_module
    if current_module is None:
        current_module = Module('__main__')
    current_module.tests.append(test_obj)


def get_fixture():
    global current_module
    if current_module is None:
        current_module = Module('__main__')
    
    if not current_module.fixture:
        current_module.fixture = Fixture()
    
    return current_module.fixture


@require_init
def register_test_results(func, exc):
    global failed, errors, tests
    result = Result.OK
    tests += 1
    if exc:
        result = Result.FAILED if isinstance(exc, AssertionError) else Result.ERROR
        if result == Result.FAILED:
            failed += 1
        else:
            errors += 1
    
    logger.log_test_info(func.__qualname__, result, exc)


@require_init
def register_module_exec_error(module_path, exc_type, exc, tb):
    global errors, init, t_start
    errors += 1
    logger.log_module_exec_error(module_path, exc_type, exc, tb)


@require_init
def exec_modules(module_paths, exec_name):
    global abort, current_module
    with exec_context:
        for module_path in filter_modules(module_paths):
            current_module = Module(module_path)
            logger.log_module_info(module_path)
            
            try:
                runpy.run_path(module_path, init_globals=utilities, run_name=exec_name)
                if abort:
                    abort = False
                    continue

                for test in filter_tests(current_module):
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
    if running or config_in_process or current_module is None:
        return
    
    initialize()
    
    with exec_context:
        try:
            for test in filter_tests(current_module):
                call_with_resources(test)
        
        except KeyboardInterrupt:
            return

        except SystemExit:
            return

        except Exception as exc:
            exc_type = type(exc)
            traceback = exc.__traceback__
            register_module_exec_error(current_module.path, exc_type, exc, traceback)
            return


def run_config(path, exec_name):
    global config_in_process
    config_in_process = True
    try:
        runpy.run_path(path, run_name=exec_name)

    finally:
        config_in_process = False
