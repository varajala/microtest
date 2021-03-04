# microtest
Simple but powerful testing utilities for Python.


## Table of contents
- [Intallation](installation)
- [Use](use)

## Installation

To use this library, please install **Python 3.7+**. 
Any Python version before 3.7 won't work because the pathlib is used in this project.

You can check the version of your Python interpreter by typing the following command to the terminal:

On Windows:

    python --version
  
On Linux and Mac:

    python3 --version
    
You can install Microtest directly from PyPI:

Winodws:

    pip install microtest
    
Mac and Linux:

    pip3 install microtest

## Use

### Basic use
To create test cases, import test from microtest.
After this you can apply this decorator to any function or method to make it part of the test suite.
This needs to be called somewhere in the module to do any testing. Here's a simple example:

```python
from microtest import test

@test
def test_function():
    assert 10 > 0
    
if __name__ == '__main__':
    test_function()
```
Now executing this module normally will produce the following output:
 ```shell
  ===========================================================================
  Started testing...
  ===========================================================================
  Ran 1 tests.

  OK.
 ```
 If the test function is not called, it will not be included in the test suite.
 
 Running microtest from the command line is preferrable to executing single modules directly.
 Any function decorated with the test-decorator will catch any errors, but when running a single module
 directly, any error thown outside the test cases won't be handeled and can effect the test output.
 Running microtest via the command line will handle all possible errors, even when thrown outside any test cases.
 
 To execute all modules inside a directory, type the following command to the terminal:
 
 On Windows:
 
    python -m microtest <path-to-the-directory>
    
 Linux and Mac:
 
    python3 -m microtest <path-to-the-directory>
    
  This will result microtest to search all Python modules with a specific name inside the directory and its subdirectories and execute them.
  The following Python modules are executed:
  
  - Those starting with the name test\_ or tests\_
  - Those ending with the name \_test or \_tests
  - Those with the name test.py or tests.py
  
  **All modules will be executed with the \_\_name\_\_ - attribute set to '\_\_main\_\_'.**
  
  Let's run the previous example via the command line.
  
  Inside the directory, where the example module is: (running on Linux)
  
    python3 -m microtest .
  
  This will give the resulting output:
  ```shell
===========================================================================
Started testing...
===========================================================================
Executed 1 modules in 0.002s.
Ran 1 tests.

OK.
  ```
  
Now let's add more modules to test. Let's run microtest with the following filestructure:


### Output

By default microtest will display a traceback of all failed tests and errors in addition to the start and finish notifications.
Currently there are two more modes for output verbosity. If you want minimal output, use the flag **-m**, or **--minimal**.
This will prevent the traceback logging from errors. For more verbose output use the **-v**, or **--verbose** flag.
THe verbose mode adds a breakdown of all the executed modules and the testcases in them.

Here's how the verbose output looks like:

Notice that the **filepath always has to be the last argument provided.**

### Fixtures and more advanced tests

Here's a suggestion for testing:

 ```python
import pathlib

from microtest import test
from yourapp.database import DatabaseAPI

TEST_DATABASE = pathlib.Path(__file__).parent.joinpath('test_db.db')


def setup():
    DatabaseAPI.connect(TEST_DATABASE)
    
def cleanup():
    DatabaseAPI.disconnect()


def run():
    setup()
    #insert test cases here
    test_case1()
    test_case2()
    cleanup()


@test
def test_case1():
    pass


@test
def test_case2():
    pass


if __name__ == '__main__':
    run()
  ```
 It's easy to setup more complex fixtures and setup/cleanup actions, since there are no limitations by the testing library.
 Python offers great metaprogramming tools, so use them to implement features like skipping, fixtures and so on.
 Microtest mainly provides a tool to search tests inside a directory structure and execute them.
 You can also use microtest only as a scanner to find tests and use other testing tools, such as Python's builtin unittest module.
