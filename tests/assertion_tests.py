import unittest
import traceback
import functools

import microtest.assertion as assertion


class Tests(unittest.TestCase):

    def test_basic_assertion(self):
        x = 2
        try:
            assert x == 1
        except AssertionError as err:
            result = assertion.resolve_assertion_error(type(err), err, err.__traceback__)
            self.assertTrue('assert 2 == 1' in result)


    def test_basic_assertion_multiple_operators(self):
        x = None
        try:
            assert x is not None
        except AssertionError as err:
            result = assertion.resolve_assertion_error(type(err), err, err.__traceback__)
            self.assertTrue('assert None is not None' in result)


    def test_string_assertion(self):
        x = 'Foo and Bar'
        try:
            assert x != 'Foo and Bar'
        except AssertionError as err:
            result = assertion.resolve_assertion_error(type(err), err, err.__traceback__)
            self.assertTrue("assert 'Foo and Bar' != 'Foo and Bar'" in result)


    def test_func_assertion(self):
        func = lambda s: s.upper()
        try:
            assert func('spam') == 'spam'
        except AssertionError as err:
            result = assertion.resolve_assertion_error(type(err), err, err.__traceback__)
            self.assertTrue("assert 'SPAM' == 'spam'" in result)


    def test_complex_assertion(self):
        foo = False
        func = lambda a, b: a ** b
        value = 42
        limit = 100
        bar = True
        
        try:
            assert foo if func(6, 2) - value > limit else bar
        except AssertionError as err:
            result = assertion.resolve_assertion_error(type(err), err, err.__traceback__)
            print(result)
            self.assertTrue('assert False if 36 - 42 > 100 else True' in result)


    def test_assertion_context_simple(self):
        try:
            assert 1 == 2, '1 was not equal to 2'
        except AssertionError as err:
            result = assertion.resolve_assertion_error(type(err), err, err.__traceback__)
            self.assertTrue("assert 1 == 2" in result)
            self.assertTrue("1 was not equal to 2" in result)


    def test_assertion_context_complex(self):
        try:
            assert 1 == 2, ('1 was not equal to 2', 'some other string')
        except AssertionError as err:
            result = assertion.resolve_assertion_error(type(err), err, err.__traceback__)
            self.assertTrue("assert 1 == 2" in result)
            self.assertTrue("('1 was not equal to 2', 'some other string')" in result)
        

if __name__ == '__main__':
    unittest.main(argv=['python3'], exit=False)