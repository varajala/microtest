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

Download the source code in a .zip-folder or fork and clone this project to your local repository.
Next navigate to the toplevel folder *microtest*.

Here you should see the following items in this drectory: ***microtest***, *README.md*, *LICENSE.txt*,  *setup.py*.

Next type the following command to your terminal:

On Windows:

    pip install .
  
On Linux and Mac:

    pip3 install .
    
    
## Use

### Basic use
To create test cases, import test from microtest.decorators.
After this you can apply this decorator to any function or method to make it part of the test suite.
This needs to be called somewhere in the module to do any testing. Here's a simple example:

```python
from microtest.decorators import test

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
  Ran 1 test.
  
  OK.
 ```
 If the test function is not called, it will not be included in the test suite.
 
 ### Testing multiple modules
 
 This library provides a handy scanning tool to locate Python modules.
 Running microtest from the command line is preferrable to executing single modules directly.
 Any function decorated with the test-decorator will catch any errors, but when running a single module
 directly, any error thown outside the test cases won't be handeled and can effect the test output.
 Running microtest via the command line will handle all possible errors, even when thrown outside any test cases.
 
 To execute all modules inside a directory, type the following command to the terminal:
 
 On Windows:
 
    python -m microtest <path-to-the-directory>
    
 Linux and Mac:
 
    python3 -m microtest <path-to-the-directory>
    
  This will result microtest to search all Python modules inside the directory and execute them.
  **All modules will be executed with the \_\_name\_\_ - attribute set to '\_\_main\_\_'.**
  
  Let's run the previous example via the command line.
  
  Inside the directory, where the example module is: (running on Linux)
  
    python3 -m microtest .
  
  This will give the resulting output:
  ```shell
  ===========================================================================
  Started testing...
  ===========================================================================
  Executed 1 module.
  
  Ran 1 test.
  
  OK.
  ```
