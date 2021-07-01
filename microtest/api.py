"""
The user API.

Author: Valtteri Rajalainen
Edited: 23.6.2021
"""

import os
import inspect
import traceback
import microtest.core as core


__all__ = [
    'test',
    'resource',
    'utility',
    'on_exit',
    'call',
    'create_fixture',
    
    'raises',
    'patch',
    'add_resource',
    
    'Fixture',
    'PatchObject',
    ]


class CaptureErrors(core._TestObject):
    def __call__(self, *args, **kwargs):
        error = None
        try:
            self.func(*args, **kwargs)
        except Exception as exc:
            error = exc
        return error


class CombinedError(Exception):
    def __init__(self, *, info, last_raised, during=None):
        super().__init__(self)
        self.__traceback__ = last_raised.__traceback__
        self.info = info
        self.last_raised = last_raised
        self.during = during

    def __str__(self):
        parts = [
            f'\n\n{self.info}:\n',
        ]
        if self.during:
            tb = ''.join(traceback.format_exception(type(self.during), self.during, self.during.__traceback__))
            parts.append(tb)
            parts.append('While handling the exception above another error occured:\n')

        tb = ''.join(traceback.format_exception(type(self.last_raised), self.last_raised, self.__traceback__))
        parts.append(tb)
        return '\n'.join(parts).rstrip()


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
        self._setup = CaptureErrors(func)


    def cleanup(self, func):
        self._cleanup = CaptureErrors(func)


    def reset(self, func):
        self._reset = CaptureErrors(func)


    def __iter__(self):
        return FixtureIterator(self)


    def abort_with_error(self, error, info):
        if self._cleanup:
            cleanup_error = core.call_with_resources(self._cleanup)
            if cleanup_error:
                raise CombinedError(info = info, last_raised = cleanup_error, during = error)
        raise CombinedError(info = info, last_raised = error)


class TestCaseWrapper(core._TestObject):
    def __init__(self, fixture, test_obj):
        self.fixture = fixture
        self.test_obj = test_obj
        core._TestObject.__init__(self, test_obj.func)

    def __call__(self, **kwargs):
        fixture = self.fixture

        if fixture._reset:
            error = core.call_with_resources(fixture._reset)
            if error:
                info = 'An error occured while performing reset actions'
                self.fixture.abort_with_error(error, info)
                return
        
        exc = self.test_obj(**kwargs)
        if exc:
            fixture.error = exc
            if fixture._cleanup:
                error = core.call_with_resources(fixture._cleanup)
                if error:
                    info = f'An error occurred while executing function "{self.func.__qualname__}"'
                    return CombinedError(info = info, last_raised = error, during = exc)
        return exc
            

class FixtureIterator:

    def __init__(self, fixture):
        self.fixture = fixture

    def __next__(self):
        fixture = self.fixture
        if not fixture.setup_done:
            if fixture._setup:
                error = core.call_with_resources(fixture._setup)
                if error:
                    info = 'Fixture setup failed'
                    self.fixture.abort_with_error(error, info)
                    return
            fixture.setup_done = True
        
        if fixture.testcases:
            test_obj = fixture.testcases.pop(0)
            return TestCaseWrapper(self.fixture, test_obj)
        
        if fixture._cleanup and not fixture.error:
            core.call_with_resources(fixture._cleanup)
        raise StopIteration



def test(func):
    """Make a single function part of the test suite."""
    module_path = os.path.abspath(inspect.getsourcefile(func))
    testcase = CaptureErrors(func)
    core.collect_test(module_path, testcase)
    return testcase


def create_fixture(func):
    globals_ = func.__globals__
    obj = core.call_with_resources(func)
    if not isinstance(obj, Fixture):
        ifno = '@create_fixture excpects a callable that retruns a Fixture object'
        raise ValueError(info)
    
    globals_['fixture'] = obj


def raises(callable, args, exc_type):
    if not inspect.isclass(exc_type):
        raise TypeError('Argument exc_type was not a class.')
    
    try:
        callable(*args)
    
    except exc_type as err:
        return True

    else:
        return False


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
    obj = core.call_with_resources(func)
    core.add_resource(func.__name__, obj)


def utility(obj, *, name=None):
    if name is None:
        name = obj.__name__
    core.add_utility(name, obj)


def add_resource(name, obj):
    core.add_resource(name, obj)


def on_exit(func):
    core.on_exit(func)


def call(func):
    if core.running or core.config_in_process:
        core.call_with_resources(func)
    return func