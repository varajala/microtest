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
    
    'setup',
    'reset',
    'cleanup',

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
    ]


def test(func):
    """
    Make a single function part of the test suite.
    """
    test_obj = core._TestObject(func)
    core.collect_test(test_obj)
    return test_obj


def setup(func):
    fixture = core.get_fixture()
    fixture.register_setup(func)
    return func


def reset(func):
    fixture = core.get_fixture()
    fixture.register_reset(func)
    return func


def cleanup(func):
    fixture = core.get_fixture()
    fixture.register_cleanup(func)
    return func


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
    def __init__(self, obj, **kwargs):
        self.obj = obj
        self.patched_attrs = kwargs
        self.original_attrs = dict()

    def __enter__(self):
        for attr, value in self.patched_attrs.items():
            self.original_attrs[attr] = getattr(self.obj, attr)
            setattr(self.obj, attr, value)
        return self

    def __exit__(self, exc_type, exc, tb):
        for attr, value in self.original_attrs.items():
            setattr(self.obj, attr, value)


def patch(obj, **kwargs):
    return Patch(obj, **kwargs)


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
