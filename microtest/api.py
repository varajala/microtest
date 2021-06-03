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
    'Fixture',
    ]


def test(callable):
    """Make a single function part of the test suite."""
    module_path = os.path.abspath(inspect.getsourcefile(callable))
    
    def wrapper(*args, **kwargs):
        error = None
        try:
            callable(*args, **kwargs)
        
        except Exception as exc:
            error = exc
        
        finally:
            core.register_test(module_path, callable, error)
    return wrapper


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


class Fixture:
    def __init__(self, *, setup=None, reset=None, cleanup=None):
        self.setup = setup
        self.cleanup = cleanup
        self.reset = reset

    def run(self, testcases):
        for testcase in testcases:
            try:
                testcase()
            finally:
                if self.reset:
                    self.reset()        

    def __enter__(self):
        if self.setup:
            self.setup()
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        if self.cleanup:
            return self.cleanup()