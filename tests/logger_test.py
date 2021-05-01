import unittest
import time
import sys
from queue import Queue
from tempfile import TemporaryFile
from threading import Thread

import microtest.func_logger as logger
from microtest.data import *


class Tests(unittest.TestCase):

    def setUp(self):
        logger.output_mode = Output.DEFAULT
        logger.out = sys.stdout
        logger.use_colors = False
        logger.width = 75
        logger.running = True
        logger.wait_period = 0.1


    def test_running(self):
        with TemporaryFile(mode='w+') as file:
            logger.out = file
            queue = Queue()
            t = Thread(target=logger.run, args=(queue,))
            t.start()

            task = Task(Task.START)
            queue.put(task)

            data = {
                'errors':0,
                'tests':0,
                't_start':0.0,
                't_stop':0.0
            }
            task = Task(Task.STOP, data)
            queue.put(task)
            t.join()

            file.seek(0)
            output = file.read()
            self.assertTrue(output != '')


if __name__ == '__main__':
    unittest.main()




