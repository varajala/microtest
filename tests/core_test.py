import unittest
import time
from queue import Queue

import microtest.core as core
from microtest.data import *


def testfunc():
    pass


class Tests(unittest.TestCase):

    def setUp(self):
        core.errors = 0
        core.tests = 0
        core.t_start = None
        core.t_end = None
        core.logger_queue = Queue()


    def test_register(self):
        self.assertTrue(core.tests == 0)
        self.assertTrue(core.errors == 0)
        
        path = '/home/varajala/dev/module.py'
        exception = None
        core.register_test(path, testfunc, exception)
        
        self.assertTrue(core.tests == 1)
        self.assertTrue(core.errors == 0)
        self.assertEqual(len(core.modules.keys()), 1)

        path = '/home/varajala/dev/other_module.py'
        exception = RuntimeError()
        core.register_test(path, testfunc, exception)
        self.assertTrue(core.tests == 2)
        self.assertTrue(core.errors == 1)
        self.assertEqual(len(core.modules.keys()), 2)


    def test_timing(self):
        wait = 0.05
        core.start_testing()
        time.sleep(wait)
        core.stop_testing()

        delta = round(core.t_stop - core.t_start, 2)
        self.assertEqual(delta, wait)


    def test_logging_tasks(self):
        queue = core.logger_queue
        self.assertTrue(queue.empty())

        core.start_testing()
        self.assertFalse(queue.empty())
        task = queue.get()
        self.assertEqual(task.type, Task.START)

        path = '/home/varajala/dev/module.py'
        exception = None
        core.register_test(path, testfunc, exception)

        self.assertFalse(queue.empty())
        task = queue.get()
        self.assertEqual(task.type, Task.TEST)

        test_obj = task.data
        self.assertEqual(test_obj.func, 'testfunc')
        self.assertEqual(test_obj.success, True)
        self.assertEqual(test_obj.exception, None)

        core.stop_testing()
        self.assertFalse(queue.empty())
        task = queue.get()
        self.assertEqual(task.type, Task.STOP)
        data = task.data
        self.assertTrue('errors' in data)
        self.assertTrue('tests' in data)
        self.assertTrue('t_start' in data)
        self.assertTrue('t_stop' in data)




if __name__ == '__main__':
    unittest.main()