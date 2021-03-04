"""
Main decorators that define the API for the test tools.

Author: Valtteri Rajalainen
Edited: 4.3.2021
"""

from microtest.logger import TestLogger

__all__ = ['test',]


def test(func):
    """Make a single function part of the test suite."""
    def wrapper(*args, **kwargs):
        logger = TestLogger()
        error = None
        try:
            func(*args, **kwargs)
        
        except Exception as exc:
            error = exc
        
        finally:
            logger.add_test(func, error)
    return wrapper
    