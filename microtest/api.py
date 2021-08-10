"""
The user API.

Author: Valtteri Rajalainen
"""

import os
import inspect
import traceback
import microtest.core as core
import functools


__all__ = [
    'test',
    'resource',
    'utility',
    'on_exit',
    'call',
    'group',
    
    'run',
    'abort',
    'raises',
    'patch',
    
    'add_resource',
    
    'only_modules',
    'exclude_modules',

    'only_groups',
    'exclude_groups',
    
    'Fixture',
    ]


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


class SimpleTestCase(core._TestObject):
    
    def __call__(self, *args, **kwargs):
        error = None
        try:
            self.func(*args, **kwargs)
        
        except Exception as exc:
            error = exc
        
        core.register_test_results(self.module_path, self, error)
        return error


class Fixture(core._FixtureObject):

    def __init__(self, *, reset = None, setup = None, cleanup = None):
        self._setup = setup
        self._cleanup = cleanup
        self._reset = reset
        
        self.setup_done = False
        self.testcases = list()
        self.error = None


    def append(self, test):
        self.testcases.append(test)


    def setup(self, func):
        self._setup = capture_exception(func)


    def cleanup(self, func):
        self._cleanup = capture_exception(func)


    def reset(self, func):
        self._reset = capture_exception(func)


    def __iter__(self):
        return self


    def __next__(self):
        if not self.setup_done:
            self.do_setup()
        
        if self.error:
            raise StopIteration

        if self.testcases:
            return self.wrap_test(self.testcases.pop(0))
        
        self.do_cleanup()
        raise StopIteration


    def wrap_test(self, func):
        @functools.wraps(func)
        def wrapper(**kwargs):
            if self._reset:
                error = core.call_with_resources(self._reset)
                if error:
                    self.abort_with_error(error)
            return func(**kwargs)
        return wrapper


    def do_setup(self):
        self.setup_done = True
        if self._setup:
            error = core.call_with_resources(self._setup)
            if error:
                self.abort_with_error(error)


    def do_cleanup(self):
        if self._cleanup:
            error = core.call_with_resources(self._cleanup)
            if error:
                self.abort_with_error(error, do_cleanup=False)

    
    def abort_with_error(self, error, *, do_cleanup=True):
        self.error = error
        if do_cleanup:
            self.do_cleanup()
        raise error


def test(func):
    """
    Make a single function part of the test suite.
    """
    module_path = os.path.abspath(inspect.getsourcefile(func))
    testcase = SimpleTestCase(func, module_path)
    core.collect_test(module_path, testcase)
    return testcase


def raises(callable, params, exc_type):
    """
    Return True if provided callable raises an exception of type exc_type with
    the given arguments. All other exception types will be raised normally.
    
    Params must be a tuple or a dict. If a dict object is given, they are
    passed as keyword arguments.
    """
    if not inspect.isclass(exc_type):
        raise TypeError('Argument exc_type was not a class.')

    try:
        callable(**params) if isinstance(params, dict) else callable(*params)
    
    except exc_type as err:
        return True

    else:
        return False


class Patch:
    """
    Dynamically replace an attribute from the given object with the
    new object. Use as a context manager.
    """
    def __init__(self, obj, attr, new):
        object.__setattr__(self, 'in_context', False)
        self.obj = obj
        self.attr = attr
        self.old = getattr(obj, attr)
        self.new = new

    def __setattr__(self, attr, value):
        in_context = object.__getattribute__(self, 'in_context')
        if not in_context:
            object.__setattr__(self, attr, value)
            return
        
        new = object.__getattribute__(self, 'new')
        obj = object.__getattribute__(self, 'obj')
        if hasattr(new, attr):
            object.__setattr__(new, attr, value)
            return
        object.__setattr__(obj, attr, value)

    def __getattribute__(self, attr):
        in_context = object.__getattribute__(self, 'in_context')
        if not in_context:
            return object.__getattribute__(self, attr)
        
        new = object.__getattribute__(self, 'new')
        obj = object.__getattribute__(self, 'obj')
        if hasattr(new, attr):
            return object.__getattribute__(new, attr)
        return object.__getattribute__(obj, attr)

    def __enter__(self):
        setattr(self.obj, self.attr, self.new)
        self.in_context = True
        return self

    def __exit__(self, exc_type, exc, tb):
        object.__setattr__(self, 'in_context', False)
        setattr(self.obj, self.attr, self.old)


def patch(obj, attr, new):
    return Patch(obj, attr, new)


def resource(func):
    obj = core.call_with_resources(func)
    core.add_resource(func.__name__, obj)


def utility(obj, *, name=None):
    """
    Mark the wrapped object as a utility.
    These are injected into the function namespace
    during test execution.
    """
    if name is None:
        name = obj.__name__
    core.add_utility(name, obj)
    return obj


def add_resource(name, obj):
    core.add_resource(name, obj)


def on_exit(func):
    core.on_exit(func)


def call(func):
    """
    Call the function during module exection if microtest is running
    or doing configuration.
    """
    if core.running or core.config_in_process:
        core.call_with_resources(func)
    return func


def abort():
    """
    Set the abort flag.
    This is checked after the module is executed and before
    any tests are executed.

    Cleared after every module executed.
    """
    core.abort = True


def group(name):
    def wrapper(test_obj):
        test_obj.group = name
        return test_obj
    return wrapper


def exclude_groups(*args):
    for name in args:
        core.exclude_groups.add(name)


def only_groups(*args):
    for name in args:
        core.included_groups.add(name)


def exclude_modules(*args):
    for name in args:
        core.exclude_modules.add(name)


def only_modules(*args):
    for name in args:
        core.included_modules.add(name)


def run():
    core.run_current_module()
