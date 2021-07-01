"""
Stateful component of microtest.

Author: Valtteri Rajalainen
Edited: 23.6.2021
"""

import timeit
import inspect
import runpy

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


class _TestObject:
    def __init__(self, test_func):
        self.func = test_func
    
    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            func = object.__getattribute__(self, 'func')
            return object.__getattribute__(func, attr)
            

class _FixtureObject:
    pass


def while_running(func):
    def wrapper(*args, **kwargs):
        if not running:
            initialize()
        return func(*args, **kwargs)
    return wrapper


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


def filter_tests(namespace):
    tests = [ item for item in namespace.values() if issubclass(type(item), _TestObject) ]
    for item in namespace.values():
        if issubclass(type(item), _FixtureObject):
            item.testcases = tests
            return item
    return tests


def collect_test(module_path, test_obj):
    module = modules.get(module_path, None)
    if module is None:
        module = Module(module_path)
        modules[module_path] = module
        if running:
            logger.log_module_info(module_path)
            module.logged = True
    
    module.tests = filter_tests(test_obj.func.__globals__)
    module.tests.append(test_obj)


@while_running
def register_test_results(module_path, func, exc):
    global failed, errors, tests
    tests += 1
    result = Result.OK
    if exc:
        exc_name = exc.__class__.__name__
        result = Result.FAILED if exc_name == 'AssertionError' else Result.ERROR
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


def run_config(path, exec_name):
    global config_in_process
    config_in_process = True
    try:
        runpy.run_path(path, init_globals=utilities, run_name=exec_name)

    finally:
        config_in_process = False


@while_running
def exec_modules(module_paths, exec_name):
    global abort
    with exec_context:
        for module_path in module_paths:
            if module_path not in modules:
                modules[module_path] = module = Module(module_path)
                logger.log_module_info(module_path)
                module.logged = True
            
            try:
                runpy.run_path(module_path, init_globals=utilities, run_name=exec_name)
                if abort:
                    abort = False
                    continue
                run_module(module_path)

            except KeyboardInterrupt:
                break

            except SystemExit:
                break

            except Exception as exc:
                exc_type = type(exc)
                traceback = exc.__traceback__
                register_module_exec_error(module_path, exc_type, exc, traceback)


@while_running
def run_module(module_path):
    if module_path not in modules:
        return

    module = modules[module_path]
    for test in module.tests:
        error = call_with_resources(test)
        register_test_results(module_path, test, error)


def run_current_module():
    if running or config_in_process:
        return
    
    initialize()
    
    with exec_context:
        modules_list = list(modules.values())
        if len(modules_list) == 0:
            return

        module = modules_list.pop(0)
        for test in module.tests:
            error = call_with_resources(test)
            register_test_results(module.path, test, error)


def generate_signature(obj):
    func_obj = None
    if inspect.isfunction(obj):
        func_obj = obj

    if issubclass(obj.__class__, _TestObject):
        func_obj = obj.func

    if func_obj is None:
        info = 'Cannot generate signature for object that is not '
        info += 'a function or microtest.core._TestObject subclass instance.'
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