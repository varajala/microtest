"""
Utilities for testing.

Author: Valtteri Rajalainen
Edited: 21.1.2021
"""

import traceback
import timeit


class Singleton:
    """
    Base class for implementing the Singleton-pattern.
    Don't use the __init__ - method in the subclass.
    Use the _setup_instance - method instead. If the
    _setup_instance is not implemented in the subclass,
    NotImplementedError is raised.

    Use:
        #SubClass inherits from Singleton
        instance1 = SubClass()
        instance2 = SubClass()
        #instance1 is instance2 -> True
    """

    instance = None

    def __new__(class_, *args, **kwargs):
        if class_.instance is None:
            class_.instance = super().__new__(class_)
            class_.instance._setup_instance()
        return class_.instance


    def __call__(class_, *args, **kwargs):
        return class_.__new__(*args, **kwargs)


    def _setup_instance(self, *args, **kwargs):
        info = 'No _setup method defined. Use it instead of __init__.'
        raise NotImplementedError(info)


class TestLogger(Singleton):
    """A logger class for storing data during testing."""

    FAIL_STATUS = 'FAIL'
    ERROR_STATUS = 'ERROR'
    OK_STATUS = 'OK'
    MINIMAL = 'minimal'
    VERBOSE = 'verbose'
    DEFAULT = 'default'
    OUTPUT_WIDTH = 75 #chars
    log = print

    def _setup_instance(self, *args, **kwargs):
        self._tested_modules = []
        self._testcases = 0
        self._output = self.DEFAULT
        self.errors = 0
        self.failed = 0
        self.root_path = None
        self.log(self.OUTPUT_WIDTH * '=')
        self.log('Started testing...')
        self.log(self.OUTPUT_WIDTH * '=')


    @property
    def tests_performed(self):
        return self._testcases


    @property
    def tested_modules(self):
        return len(self._tested_modules)


    @property
    def tests_passed(self):
        return self.errors == 0 and self.failed == 0


    @property
    def minimal_output(self):
        return self._output == self.MINIMAL


    @property
    def verbose_output(self):
        return self._output == self.VERBOSE


    def set_verbose(self):
        self._output = self.VERBOSE


    def set_minimal(self):
        self._output = self.MINIMAL


    @property
    def default_output(self):
        result = True
        minimal = self.minimal_output
        verbose = self.verbose_output
        if minimaĺ or verbose:
            result = False
        return result


    @property
    def tested_modules_message(self):
        tested_modules = self.tested_modules
        message = f'Executed {tested_modules} modules.\n'
        if tested_modules == 1:
            message = 'Executed 1 module.\n'
        return message


    @property
    def performed_testcases_message(self):
        tests = self.tests_performed
        message = f'Ran {tests} tests overall.\n'
        if tests == 1:
            message = 'Ran 1 test.\n'
        elif tests == 0:
            message = 'No tests were conducted...\n'
        return message


    def parse_module_name(self, path):
        name = path.name.replace(path.suffix, '')
        if self.root_path is not None:
            name = self.get_extended_path(self.root_path, path)
        return name


    @staticmethod
    def get_extended_path(root, extended_path):
        """
        Return the extended path relative to the root path.
        Paths are pathlib.Path objects.

        For example:
        root = /home/usr/Documents/project/
        extended_path = /home/usr/Documents/project/src/foo.py
        >>> project/src/foo.py
        """
        relative_path = str(extended_path).replace(str(root.parent), '')
        return relative_path[1:]


    def add_test(self, func, status):
        test = TestCase(func, status)
        self._testcases += 1
        if self.current_module is not None:
            self.current_module.add_test(test)


    def add_module(self, module_path):
        module_name = self.parse_module_name(module_path)
        module = TestModule(module_name)
        self._tested_modules.append(module)
        self.current_module = module


    def log_fail(self, exception):
        """
        Called when an AssertionError is raised
        from the tested function.
        """
        self.failed += 1
        if not self.minimal_output:
            tb = exception.__traceback__
            self.log('Assertion failed:\n')
            for line in traceback.format_tb(tb):
                self.log(line)
            self.log(self.OUTPUT_WIDTH * '=')


    def log_error(self, exception):
        self.errors += 1
        if not self.minimal_output:
            tb = exception.__traceback__
            error_type = exception.__class__.__name__
            self.log(f'An error type of: <{error_type}> occured.\n')
            for line in traceback.format_tb(tb):
                self.log(line)
            self.log(self.OUTPUT_WIDTH * '=')


    def log_module_execution_error(self, exception, module_path):
        self.errors += 1
        if not self.minimal_output:
            tb = exception.__traceback__
            error_type = exception.__class__.__name__
            self.current_module.error = error_type
            self.log(f'Unhandled error type of: <{error_type}> occured while executing module:\n')
            self.log(f'{module_path}\n')
            for line in traceback.format_tb(tb):
                self.log(line)
            self.log(self.OUTPUT_WIDTH * '=')


    def show_results(self):
        if self.verbose_output:
            self.log_verbose_output()
        if self.tested_modules > 0:
            self.log(self.tested_modules_message)
        self.log(self.performed_testcases_message)
        if self.tests_passed:
            self.log('OK.')
        else:
            self.log(f'Failed: {self.failed}')
            self.log(f'Errors: {self.errors}')


    def log_verbose_output(self):
        for module in self._tested_modules:
            self.log(str(module))
        if self._tested_modules:
            self.log(self.OUTPUT_WIDTH * '=')


    def __del__(self):
        self.show_results()


class TestCase():
    """
    Object to hold information on one test case.
    Records the tested function object and its
    result status (OK, ERROR, FAIL).
    """

    OUTPUT_WIDTH = TestLogger.OUTPUT_WIDTH

    def __init__(self, func, status):
        self.func = func
        self.status = status


    @property
    def info(self):
        width = self.OUTPUT_WIDTH
        name = self.func.__qualname__
        filling = ' ' + (width-len(name))*'.' + ' '
        return name + filling + self.status


class TestModule():
    """
    Object to hold information on testcases
    executed inside one module.
    """

    def __init__(self, name):
        self.name = name
        self._error = None
        self.testcases = []


    def add_test(self, testcase):
        self.testcases.append(testcase)


    @property
    def error(self):
        return self._error


    @error.setter
    def error(self, error_type):
        self._error = error_type


    def __str__(self):
        output_lines = []
        output_lines.append(f'Module: {self.name}')
        if self.error is not None:
            output_lines.append(f'\nFailed to execute because of {self.error}.')
        else:
            for test in self.testcases:
                output_lines.append(test.info)
        output_lines.append('\n')
        return '\n'.join(output_lines)

