"""
Main decorators that define the API for the test tools.

Author: Valtteri Rajalainen
Edited: 26.5.2021
"""
import os
import inspect
import traceback as tb_module

import microtest.core as core


__all__ = [
    'test',
    'raises',
    'patch',
    'resource',
    'utility',
    'add_resource',
    'create_fixture',
    'on_exit',
    'Fixture',
    'PatchObject',
    ]


def generate_signature(func):
    signature = inspect.signature(func)
    return [ param for param in signature.parameters ]


class TestCase(core._TestObject):

    def __init__(self, module_path, func):
        self.func = func
        self.signature = generate_signature(func)
        self.module_path = module_path
        self.catch_errors = True

    def __call__(self, **kwargs):
        error = None
        try:
            self.func(**kwargs)
        
        except Exception as exc:
            if not self.catch_errors:
                raise exc
            error = exc
        
        finally:
            core.register_test_results(self.module_path, self.func, error)


class Fixture(core._FixtureObject):

    def __init__(self, *, reset = None, setup = None, cleanup = None):
        self.setup_done = False
        self.testcases = list()
        self.error = None
        self._setup = setup
        self._cleanup = cleanup
        self._reset = reset


    def append(self, test):
        self.testcases.append(test)


    def setup(self, func):
        self._setup = func
        return func


    def cleanup(self, func):
        self._cleanup = func
        return func


    def reset(self, func):
        self._reset = func
        return func


    def __iter__(self):
        return FixtureIterator(self)


class TestCaseWrapper:
    def __init__(self, fixture, testcase):
        self.fixture = fixture
        self.testcase = testcase
        self.signature = testcase.signature

    def __call__(self, **kwargs):
        fixture = self.fixture
        testcase = self.testcase
        testcase.catch_errors = False
        try:
            if fixture._reset:
                fixture._reset()
            testcase(**kwargs)
        
        except Exception as exc:
            suppress_exc = False
            fixture.error = exc
            if fixture._cleanup:
                suppress_exc = fixture._cleanup()
            
            if not suppress_exc:
                raise exc


class FixtureIterator:

    def __init__(self, fixture):
        self.fixture = fixture

    def __next__(self):
        fixture = self.fixture
        if not fixture.setup_done:
            if fixture._setup:
                fixture._setup()
            fixture.setup_done = True
        
        if fixture.testcases:
            testcase = fixture.testcases.pop(0)
            return TestCaseWrapper(self.fixture, testcase)
        
        if fixture._cleanup and not fixture.error:
            fixture._cleanup()
        raise StopIteration



def test(func):
    """Make a single function part of the test suite."""
    module_path = os.path.abspath(inspect.getsourcefile(func))
    testcase = TestCase(module_path, func)
    core.collect_test(module_path, testcase)
    return testcase


def create_fixture(func):
    globals_ = func.__globals__
    obj = core.call_with_resources(func, generate_signature(func))
    if not isinstance(obj, Fixture):
        ifno = '@create_fixture excpects a callable that retruns a Fixture object'
        raise ValueError(info)
    
    globals_['fixture'] = obj


class Error:
    def __init__(self, exc_type, exc, tb):
        self.exc_type = exc_type
        self.exc = exc
        self.tb = tb

    @property
    def traceback(self):
        exc_info = (self.exc_type, self.exc, self.tb)
        return ''.join(tb_module.format_exception(*exc_info))


def raises(callable, args, exc_type):
    if not inspect.isclass(exc_type):
        raise TypeError('Argument exc_type was not a class.')
    
    try:
        callable(*args)
    
    except exc_type as err:
        return Error(exc_type, err, err.__traceback__)

    except Exception as err:
        info = f'Expected an exception with type: {exc_type.__name__}. '
        info += f'{err.__class__.__name__} was raised instead.'
        raise AssertionError(info)

    else:
        info = 'No errors raised.'
        raise AssertionError(info)


class Patch:
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


class PatchObject:

    def __init__(self, items):
        object.__setattr__(self, '__items__', items)

    def __setattr__(self, attr, value):
        items = object.__getattribute__(self, '__items__')
        items[attr] = value

    def __getattribute__(self, attr):
        items = object.__getattribute__(self, '__items__')
        if attr not in self:
            raise AttributeError(f'No such attribute "{attr}"')
        return items[attr]

    def __contains__(self, item):
        items = object.__getattribute__(self, '__items__')
        return item in items.keys()


def resource(func):
    obj = core.call_with_resources(func, generate_signature(func))
    core.add_resource(func.__name__, obj)


def utility(obj, *, name=None):
    if name is None:
        name = obj.__name__
    core.add_utility(name, obj)


def add_resource(name, obj):
    core.add_resource(name, obj)


def on_exit(func):
    core.on_exit(func)