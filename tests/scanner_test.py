import unittest
import os
import shutil
import pathlib

import microtest.scanner as scanner


class Tests(unittest.TestCase):

    test_dir = pathlib.Path(__file__).parent.joinpath('scanner_test')
    subdir = test_dir.joinpath('subdir')
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

    def setUp(self):
        os.mkdir(self.test_dir)
        for file in self.test_files:
            filepath = self.test_dir.joinpath(file)
            open(filepath, 'x').close()
        for file in self.other_files:
            filepath = self.test_dir.joinpath(file)
            open(filepath, 'x').close()

        os.mkdir(self.subdir)
        for file in self.test_files:
            filepath = self.subdir.joinpath(file)
            open(filepath, 'x').close()
        for file in self.other_files:
            filepath = self.subdir.joinpath(file)
            open(filepath, 'x').close()


    def test_scanner(self):
        test_modules = scanner.find_tests(str(self.test_dir))
        
        for filename in self.test_files:
            filepath = self.test_dir.joinpath(filename)
            self.assertTrue(str(filepath) in test_modules)
        for filename in self.other_files:
            filepath = self.test_dir.joinpath(filename)
            self.assertTrue(str(filepath) not in test_modules)

        for filename in self.test_files:
            filepath = self.subdir.joinpath(filename)
            self.assertTrue(str(filepath) in test_modules)
        for filename in self.other_files:
            filepath = self.subdir.joinpath(filename)
            self.assertTrue(str(filepath) not in test_modules)


    def tearDown(self):
        shutil.rmtree(self.test_dir)


if __name__ == '__main__':
    unittest.main(argv=['python3'], exit=False)