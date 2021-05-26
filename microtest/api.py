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


class Fixture:
    def __init__(self):
        self.__setup = None
        self.__cleanup = None

    def setup(self, func):
        self.__setup = func

    def cleanup(self, func):
        self.__cleanup = func

    def __enter__(self):
        if self.__setup:
            self.__setup()
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        self.__cleanup()