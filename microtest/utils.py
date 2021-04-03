"""
Classes:
> TestCase
> TestModule
> OutputProvider
> Colors

Author: Valtteri Rajalainen
Edited: 3.4.2021
"""

class Colors:

    OK_GREEN = '\033[92m'
    FAILED_RED = '\033[91m'
    INFO_CYAN = '\033[96m'
    RESET = '\033[0m'

    @classmethod
    def color_ok(cls, text):
        return cls.OK_GREEN + text + cls.RESET


    @classmethod
    def color_error(cls, text):
        return cls.FAILED_RED + text + cls.RESET

    
    @classmethod
    def color_info(cls, text):
        return cls.INFO_CYAN + text + cls.RESET


class OutputProvider:
    
    OUTPUT_WIDTH = 75 #chars


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


class TestCase(OutputProvider):
    """
    Object to hold information on one test case.
    Records the tested function object and its
    result status (OK, ERROR, FAIL).
    """
    
    OK_STATUS = Colors.color_ok('OK')
    ERROR_STATUS = Colors.color_error('ERROR')
    FAIL_STATUS = Colors.color_error('FAILED')

    def __init__(self, func, error_type):
        self.func = func
        self.status = self.check_status(error_type)
        

    def check_status(self, error_type):
        if error_type == 'AssertionError':
            return self.FAIL_STATUS
        if error_type is not None:
            return self.ERROR_STATUS
        return self.OK_STATUS
        
        
    @property
    def name(self):
        return self.func.__qualname__
        
    
    @property
    def failed(self):
        return self.status != self.OK_STATUS
    
    
    @property
    def output(self):
        width = self.OUTPUT_WIDTH
        filling = ' ' + (width-len(self.name))*'.' + ' '
        return self.name + filling + self.status


class TestModule(OutputProvider):
    """
    Object to hold information on testcases
    executed inside one module.
    """

    def __init__(self, path):
        self.path = path
        self._error = None
        self._testcases = []


    def add_test(self, testcase):
        self._testcases.append(testcase)


    @property
    def error(self):
        return self._error


    @error.setter
    def error(self, exception):
        self._error = exception.__class__.__name__


    @property
    def output(self):
        output_lines = []
        output_lines.append(f'Module: {Colors.color_info(str(self.path))}')
        for test in self._testcases:
            output_lines.append(test.output)
        if not self._testcases:
            output_lines.append('No test cases executed...')
        if self.error:
            output_lines.append(f'ERROR type of: <{self.error}> occured')
        output_lines.append('\n')
        return '\n'.join(output_lines)
