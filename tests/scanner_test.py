import unittest
import os

import microtest.scanner as scanner
from microtest.utils import create_temp_dir


test_files = [
    'test_module.py',
    'tests_module.py',
    'tests.py',
    'module_test.py',
    'module_tests.py',
]

other_files = [
    'module.py',
    'setup.py',
    'foo',
    'bar',
    'spam.py'
]

all_files = test_files + other_files

directories = [
    'dir',
    'dir/subdir',
]

class Tests(unittest.TestCase):

    
    @classmethod
    def setUpClass(cls):
        temp_dir = cls.temp_dir = create_temp_dir(files=all_files, dirs=directories)
        
        for dir_ in directories:
            path = os.path.join(temp_dir.path, dir_)
            for name in all_files:
                open(os.path.join(path, name), 'x').close()


    def test_scanner(self):
        temp_dir = Tests.temp_dir
        modules = set(scanner.find_tests(temp_dir.path))

        directories.insert(0, '')
        for dir_ in directories:
            dir_path = os.path.join(temp_dir.path, dir_)
            
            for name in test_files:
                path = os.path.join(dir_path, name)
                self.assertTrue(path in modules)

            for name in other_files:
                path = os.path.join(dir_path, name)
                self.assertTrue(path not in modules)


    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()


if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)