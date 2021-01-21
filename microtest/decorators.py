"""
Main decorators that define the API for the test tools.

Author: Valtteri Rajalainen
Edited: 21.1.2021
"""

from microtest.logger import TestLogger


def test(func):
    """Make a single function part of the test suite."""
    def wrapper(*args, **kwargs):
        logger = TestLogger()
        status = logger.OK_STATUS
        try:
            func(*args,**kwargs)
        
        except AssertionError as err:
            logger.log_fail(err)
            status = logger.FAIL_STATUS
        
        except Exception as err:
            logger.log_error(err)
            status = logger.ERROR_STATUS
        
        finally:
            logger.add_test(func, status)
    return wrapper