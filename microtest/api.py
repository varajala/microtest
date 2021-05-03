"""
Main decorators that define the API for the test tools.

Author: Valtteri Rajalainen
Edited: 3.5.2021
"""
import os
import inspect
import microtest.core as core
import microtest.running as running


__all__ = ['test',]


def test(callable):
    """Make a single function part of the test suite."""
    module_path = os.path.abspath(inspect.getsourcefile(callable))
    if not core.is_running():
        running.run(module_path)
    
    def wrapper(*args, **kwargs):
        error = None
        try:
            callable(*args, **kwargs)
        
        except Exception as exc:
            error = exc
        
        finally:
            core.register_test(module_path, callable, error)
    return wrapper
    