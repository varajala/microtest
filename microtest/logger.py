"""
Utilities for testing.

Author: Valtteri Rajalainen
Edited: 4.3.2021
"""

import traceback
import sys
import timeit

from microtest.utils import TestCase, TestModule, Singleton, OutputProvider, Colors


class TestLogger(Singleton, OutputProvider):
    """A logger class for storing data during testing."""

    MINIMAL = 'minimal'
    VERBOSE = 'verbose'
    DEFAULT = 'default'

    def _setup_instance(self):
        self._output = self.DEFAULT
        self._modules = []
        self._errors = []
        self._failed = []
        self._testcases = 0
        self._start_time = timeit.default_timer()
        self.log(self.OUTPUT_WIDTH * '=')
        self.log('Started testing...')
        self.log(self.OUTPUT_WIDTH * '=')
        
        
    def log(self, string):
        print(string)


    @property
    def tests_performed(self):
        return self._testcases



    @property
    def modules_tested(self):
        return len(self._modules)


    @property
    def all_passed(self):
        return self.total_errors == 0 and self.total_fails == 0
        
        
    @property
    def total_errors(self):
        return len(self._errors)
    
    
    @property
    def total_fails(self):
        return len(self._failed)


    @property
    def output(self):
        return self._output


    def verbose_output(self):
        self._output = self.VERBOSE


    def minimal_output(self):
        self._output = self.MINIMAL
        
        
    @property
    def current_module(self):
        module = None
        if self._modules:
            module = self._modules[-1]
        return module


    def add_test(self, func, exception):
        error_type = None
        if exception:
            error_type = exception.__class__.__name__
            self._failed.append(exception)
        test = TestCase(func, error_type)
        if self.current_module is not None:
            self.current_module.add_test(test)
        self._testcases += 1


    def add_module(self, module_path):
        module = TestModule(module_path)
        self._modules.append(module)
        
        
    def module_execution_error(self, exception):
        self._errors.append(exception)
        if self.current_module is not None:
            self.current_module.error = exception
            
            
    def log_results(self):
        if self.output != self.MINIMAL:
            for exception in self._errors:
                self.log_error(exception)
            for exception in self._failed:
                self.log_fail(exception)
        if self.output == self.VERBOSE:
            for module in self._modules:
                self.log(module.output)
            self.log(self.OUTPUT_WIDTH * '=')
        if self.modules_tested > 0:
            time = round(timeit.default_timer()-self._start_time, 3)
            self.log(f'Executed {self.modules_tested} modules in {time}s.')
        self.log(f'Ran {self.tests_performed} tests.\n')
        if self.all_passed:
            self.log(Colors.color_ok('OK.\n'))
        else:
            self.log(str(self.total_fails) + ' ' + Colors.color_error('FAILED')) 
            self.log(str(self.total_errors) + ' ' + Colors.color_error('ERRORS\n'))
        
        
    def log_error(self, exception):
        tb = exception.__traceback__
        error_type = exception.__class__.__name__
        self.log(Colors.color_error(f"ERROR type of <{error_type}> occured while executing a module.\n"))
        for line in traceback.format_exception(error_type, exception, tb):
            self.log(line)
        self.log(self.OUTPUT_WIDTH * '=')
        
    
    def log_fail(self, exception):
        tb = exception.__traceback__
        error_type = exception.__class__.__name__
        self.log(Colors.color_error(f"FAILED because of <{error_type}>\n"))
        for line in traceback.format_exception(error_type, exception, tb):
            self.log(line)
        self.log(self.OUTPUT_WIDTH * '=')        


    def __del__(self):
        self.log_results()
