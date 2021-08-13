"""
Stateful component of microtest.

Author: Valtteri Rajalainen
"""

import functools
import timeit
import runpy
import os
import sys

from microtest.objects import Module, Result, Types, ExecutionContext
from microtest.core.utils import (
    filter_tests,
    filter_modules,
    capture_exception,
    generate_signature,
    check_logger_object
)


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

excluded_modules = set()
included_modules = set()

excluded_groups = set()
included_groups = set()


class _TestObject:
    def __init__(self, func: Types.Function):
        self.func = func
        self.group = None

    def __getattribute__(self, attr: str):
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


class _Fixture:

    def __init__(self):
        self._setup = None
        self._cleanup = None
        self._reset = None
        
        self.setup_done = False
        self.tests = list()
        self.error = None


    def append(self, test: _TestObject):
        self.tests.append(test)


    def register_setup(self, func: Types.Function):
        if self._setup:
            info = 'Setup function is already set for this module'
            raise RuntimeError()
        self._setup = capture_exception(func)


    def register_cleanup(self, func: Types.Function):
        if self._cleanup:
            info = 'Cleanup function is already set for this module'
            raise RuntimeError()
        self._cleanup = capture_exception(func)


    def register_reset(self, func: Types.Function):
        if self._reset:
            info = 'Reset function is already set for this module'
            raise RuntimeError()
        self._reset = capture_exception(func)


    def __iter__(self):
        return self


    def __next__(self) -> _TestObject:
        if not self.setup_done:
            self.do_setup()
        
        if self.error:
            raise StopIteration

        if self.tests:
            return self.wrap_test(self.tests.pop(0))
        
        self.do_cleanup()
        raise StopIteration


    def wrap_test(self, func: Types.Function) -> Types.Function:
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

    
    def abort_with_error(self, error: Exception, *, do_cleanup=True):
        self.error = error
        if do_cleanup:
            self.do_cleanup()
        raise error


def require_init(func: Types.Function) -> Types.Function:
    """
    Wrapper function to ensure proper initialization before execution.
    """
    def wrapper(*args, **kwargs):
        if not running:
            initialize()
        return func(*args, **kwargs)
    return wrapper


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


def collect_test(test_obj: _TestObject):
    global current_module
    if current_module is None:
        current_module = Module('__main__')
    current_module.tests.append(test_obj)


def get_fixture() -> _Fixture:
    global current_module
    if current_module is None:
        current_module = Module('__main__')
    
    if not current_module.fixture:
        current_module.fixture = _Fixture()
    
    return current_module.fixture


def call_with_resources(func: Types.Function) -> Types.Any:
    kwargs = dict()
    signature = generate_signature(func)
    for item in signature:
        if item not in resources.keys():
            raise NameError(f'Undefined resource "{item}"')
        kwargs[item] = resources[item]
    return func(**kwargs)


def add_resource(name: str, obj: object):
    resources[name] = obj


def add_utility(name: str, obj: object):
    utilities[name] = obj


def on_exit(func: Types.Function):
    exec_context.add_cleanup_operation(func)


@require_init
def register_test_results(func: Types.Function, exc: Exception):
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
def register_module_exec_error(module_path: str, exc_type: Types.Class, exc: Exception, tb: Types.Traceback):
    global errors, init, t_start
    errors += 1
    logger.log_module_exec_error(module_path, exc_type, exc, tb)


@require_init
def exec_modules(module_paths: tuple, exec_name: str):
    global current_module
    with exec_context:
        for module_path in filter_modules(module_paths, included_modules, excluded_modules):
            current_module = Module(module_path)
            logger.log_module_info(module_path)
            
            try:
                runpy.run_path(module_path, init_globals=utilities, run_name=exec_name)

                for test in filter_tests(current_module, included_groups, excluded_groups):
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
            for test in filter_tests(current_module, included_groups, excluded_groups):
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


def run_config(path: str, exec_name: str):
    global config_in_process
    config_in_process = True
    try:
        runpy.run_path(path, run_name=exec_name)

    finally:
        config_in_process = False
