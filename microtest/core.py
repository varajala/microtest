import timeit
import atexit
import runpy

from microtest.data import *


exec_context = ExecutionContext()
resources = dict()
utilities = dict()

modules = dict()
logger = None
running = False

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


class _TestObject:
    pass

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
    atexit.register(stop_testing)
    running = True


def stop_testing():
    global t_start, t_stop
    
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


@while_running
def collect_test(module_path, test_obj):
    module = get_module(module_path)
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
        if exc_name == 'AssertionError':
            failed += 1
        else:
            errors += 1
    
    logger.log_test_info(func.__qualname__, result, exc)


@while_running
def get_module(module_path):
    if module_path not in modules:
        logger.log_module_info(module_path)
        modules[module_path] = Module(module_path)
    return modules[module_path]


@while_running
def register_module_exec_error(module_path, exc_type, exc, tb):
    global errors, init, t_start
    errors += 1
    logger.log_module_exec_error(module_path, exc_type, exc, tb)


@while_running
def run_modules(modules, exec_name='microtest_runner'):
    with exec_context:
        for module_path in modules:
            try:
                runpy.run_path(module_path, init_globals=utilities, run_name=exec_name)
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
        call_with_resources(test, test.signature)


@while_running
def run():
    modules_list = list(modules.values())
    if len(modules_list) == 0:
        return

    module = modules_list.pop(0)
    for test in module.tests:
        call_with_resources(test, test.signature)
    


def call_with_resources(callable, signature):
    kwargs = dict()
    for item in signature:
        if item not in resources.keys():
            raise NameError(f'Undefined resource "{item}"')
        kwargs[item] = resources[item]
    return callable(**kwargs)


def add_resource(name, obj):
    resources[name] = obj


def add_utility(name, obj):
    utilities[name] = obj


def on_exit(func):
    exec_context.on_exit = func