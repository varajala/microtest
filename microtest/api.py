"""
Main decorators that define the API for the test tools.

Author: Valtteri Rajalainen
Edited: 3.5.2021
"""
import os
import inspect
import microtest.core as core
import microtest.running as running
from microtest.data import *


__all__ = ['log', 'test', 'Fixture', ]


def log(msg):
    message = msg
    if not isinstance(msg, str):
        message = str(msg)
    task = Task(Task.LOG_INFO, message)
    core.logger_queue.put(task)


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