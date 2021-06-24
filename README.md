# microtest
Simple but powerful testing utilities for Python.


## Table of contents
- [Installation](#installation)
- [Basic Use](#basic-use)
- [Discovering Tests](#discovering-tests)
- [Different Outputs](#different-outputs)
- [Fixtures](#fixtures)
- [Resources](#resources)
- [Utilites](#utilities)
- [Config](#config)
- [Other Testing Utilities](#other-testing-utilities)

## Installation

To install microtest download and unpack the zip folder with the source code, or fork and clone this project to a local repository. After this navigate to the toplevel directory where the **setup.py**-file is located and install the package with pip.


    pyhton -m pip install .


## Basic use
Here is the most basic test scenario using microtest:

```python
import microtest


@microtest.test
def test_func():
    assert 10 > 0
    

if __name__ == '__main__':
    microtest.run()
```
The **test**-decorator tells microtest to run the function *test_func* as a part of the test suite and check its result.
The **run**-function inside the *__name__ == '__main__'*-condition will execute the tests collected from the module and output their results.


Now executing this module normally will produce the following output:
 ```
===========================================================================
Started testing...
===========================================================================

/home/varajala/dev/python/test.py
test_func ................................................................. OK    

---------------------------------------------------------------------------
Ran 1 tests in 0.001s.

OK.
 ```
 
 ## Discovering Tests

Microtest can be executed from the terminal with the following command:

    python -m microtest .

This command will start microtest at the current working directory. If microtest is ran from the terminal, it will automatically find all test modules iniside the provided directory and its children. If the provided path points to a file, only that file will be executed. In the case of no path provided, microtest defaults to the current working directory.

All Python modules with the following names are included into the test suite:
  
  - Those starting with the name test\_ or tests\_
  - Those ending with the name \_test or \_tests
  - Those with the name test.py or tests.py

Before executing any collected modules, microtest looks for a file called **main.py** in the provided directory and executes it before executing any other modules. This provides a way to configure later tests. More on this in the [config](#config)-section.

When running microtest from the terminal, the **run**-function will have no effect.
All tests decorated with the **test**-decorator will be executed automatically.


## Different Outputs

Microtest will provide a overview of all execcuted modules and tests inside the modules. Here's how the default output looks for succesful test run:

```
===========================================================================
Started testing...
===========================================================================

/home/varajala/dev/project/tests/file_handling_tests.py
test_valid_filenames ..................................................... OK    
test_invalid_filenames ................................................... OK    
test_valid_path_extensions ............................................... OK    
test_invalid_path_extensions ............................................. OK    
test_file_creation ....................................................... OK    
test_dir_creation ........................................................ OK    
test_renaming ............................................................ OK    
test_renaming_errors ..................................................... OK    
test_file_removal ........................................................ OK    
test_dir_removal ......................................................... OK    
test_common_paths ........................................................ OK    
test_child_paths ......................................................... OK    
test_access_query ........................................................ OK    

/home/varajala/dev/project/tests/cmd_parser_tests.py
test_parsing ............................................................. OK    
test_invalid_parser_inputs ............................................... OK    
test_globs ............................................................... OK    
test_cmd_validation ...................................................... OK    
test_arg_validation ...................................................... OK    

---------------------------------------------------------------------------
Ran 18 tests in 0.856s.

OK.

 ```
Here two modules were tested and total of 18 tests were executed succesfully.


When a test fails due to failed assertion microtest will resolve the runtime values in the expression and show the assertion with those values. For example the following test:

```python
import microtest


def func(string):
    return string.title()


@microtest.test
def test_func1():
    assert func('foo') == 'Foo'[::-1], 'Error message for this assertion'


@microtest.test
def test_func2():
    assert func('foo') == 'Foo'


@microtest.test
def test_func3():
    assert func('FOO') == 'Foo'
 ```

Would generate the following output:

```
===========================================================================
Started testing...
===========================================================================

/home/varajala/dev/project/tests.py
test_func1 ........................................................... FAILED    

AssertionError on line 10:
assert 'Foo' == 'ooF'

Error message for this assertion

test_func2 ........................................................... OK    
test_func3 ........................................................... OK

---------------------------------------------------------------------------
Ran 3 tests in 0.223s.

ERRORS: 0
FAILED: 1

```

## Fixtures

A fixture is an utility that helps you perform the following things:
 
  - Setting up the testing environment
  - Performing reset actions after every test
  - Performing cleanup actions after the tests in the fixture are completed

Microtest provides a Fixture class to do this for you. Here is an example:

```python
import sqlite3
import tempfile
import os
import microtest

import tested_module


fixture = microtest.Fixture()

@fixture.setup
def setup():
    global fd, path
    fd, path = tempfile.mkstemp()


@fixture.reset
def reset():
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users')
        conn.commit()


@fixture.cleanup
def cleanup():
    os.unlink(path)
    os.close(fd)


@microtest.test
def test_user_creation():
    tested_module.create_user(first_name='Foo', last_name='Bar')

    with sqlite3.connect(path) as conn:
        conn.row_factory = tested_module.user_factory
        cursor = conn.cursor()
        sql = 'SELECT * FROM users WHERE first_name = ? AND last_name = ?'
        cursor.execute(sql, ('Foo', 'Bar'))
        user = cursor.fetchone()

    assert user is not None
    assert user.first_name == 'Foo'
    assert user.last_name == 'Bar'
        
```
The example code above is an imaginary test scenario using sqlite3 database with a temporary file. Because the fixture is in the module namespace, microtest will perform the *setup*-function before any testcases. This creates a temporary file, which can be used to create temporary database. The *reset*-function will be called before each testcase. This will delete all rows from the table *users*, so the tests don't have an effect on each other. The *cleanup*-function will be called after all tests are executed, or if any exceptions occur. Here the temporary file is removed.

In microtest Fixtures are scoped to the module. You should not try to use same Fixture object for multiple modules. One module should have only one Fixture.


## Resources

Microtest provides a way to share pyhton objects across tests without any external assistance (like importing other modules). Resources are very similiar to fixtures in [pytest](https://github.com/pytest-dev/pytest). You simply create a function that returns some data and use the function's name as an argument in the test function that requires that resource. Microtest will automatically pass that resource to the test function. Here is an example:

```python
import random
import microtest


@microtest.resource
def random_integers():
    return [ random.randint(0, 100) for _ in range(10) ]


@microtest.test
def test_sorting(random_integers):
    assert my_sorting_algorithm(random_integers) == sorted(random_integers)

        
```
This resource is now available globally across all tested modules. The resource factory is always called again for every test that requires its output. Resources can also use other resources and tests can require many resources. You can define resources without a factory function by using the **add_resource**-function.

```python
import random
import microtest


microtest.add_resource('users', ['Foo', 'Bar'])

@microtest.resource
def posts(users):
    return [ {'sender': random.choice(users), 'content': 'hello'} for _ in range(10) ]


@microtest.test
def test_something(users, posts):
    pass
```

> **NOTE**: Resources should be used as data only. They should not be used to perform setup/cleanup operations with yield statements or other mechanisms.


## Utilities

Microtest provides an another way of sharing python objects between tested modules, **utilites**. Where resources are meant for easy and globally accessible data generation, utilites provide a way to share objects between module namespaces without importing. This means that large test suites don't need to be in a pyhton package and installed to share utility classes and functions. Here is an example:

In *test_utils.py*:
```python
import microtest


@microtest.utility
class VeryHandyTestClass:

    def do_something(self):
        print('Hello!')

```
    
In *example_tests.py*:
```python
import microtest


@microtest.test
def test_that_uses_utils():
    handy_thing = VeryHandyTestClass()
    handy_thing.do_something()
```
The code in *example_tests.py* would normally raise a **NameError**, there isn't a thing called *VeryHandyTestClass*. Because the class was decorated as utility, it was injected into the *example_tests.py*-module's global namespace. This is basically what import does in Pyhton.

Note that the *example_tests.py* will fail if it is executed before *test_utils.py*.
It is recommended that utilities are defined during the configuration process.


## Config

As mentioned previously, microtest looks for a file called **main.py** in the root directory when executed as a module. If the file is present in the directory, microtest will execute it separetly from other test modules. This allows you to perform config actions before any actual tests are executed. 

For example you can do some of the following things:

  - Set the \_\_name\_\_ - attribute of the executed modules. 
  - Define resources and utilites used globally between tested modules.
  - Define cleanup actions after all tests are executed, or an exception is raised.

>**NOTE:** Because the config process is separate from the actual testing, you should not insert any tests to the **main.py** - file

Microtest provides two more decorators to make the config process easy:

  - **call** -> Simply call the wrapped function if microtest is running.
  - **on_exit** -> Provide a function to be called before the program is terminated.

For example if you wanted to make a similiar temporary database as in the Fixture [example](#fixture), but available globally to all test modules, here's how it would look:

In *main.py:*
```python
import tempfile
import os
import sqlite3
import microtest


@microtest.call
def setup():
    global fd, path
    fd, path = tempfile.mkstemp()
    microtest.exec_name = '__main__'


@microtest.resource
def database():
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


@microtest.on_exit
def cleanup(exc_type, exc, tb):
    os.unlink(path)
    os.close(fd)
```
Now the temporary file is created before any tests are executed and made available as a resource in all tested modules. Functions decorated by the **call** - decorator can also request resources smiliarly to those decorated with the **test** - decorator.

The cleanup - function is called when microtest is about to exit. It takes three named arguments: exception type, exception instance and the exception traceback. These are None if microtest is exiting normally. This takes care of closing the file properly.

In this example, the \_\_name\_\_ - attribute for executed modules is set to '\_\_main\_\_'. It defaults to **'microtest_runner'**. This is simply done by modifying the microtest.exec_name - variable.


## Other Testing Utilities

Microtest also provides some useful utlities for writing less testing code. First, let's take a look at the **raises** - function.

```python
import microtest


def add(a, b):
    return a + b


@microtest.test
def test_failing():
    assert microtest.raises(add, (1, '1'), TypeError)
```

The **raises** - function takes three arguments:

  - The function to be called.
  - The arguments to be passed into the function.
  - The error type to be expected.

It returns True if the function raises the excpected error, False otherwise. All other error types will not be handled in any way. The defenition is roughly the following:

```python
def raises(func, args, error):
    try:
        func(*args)
    except error:
        return True
    else:
        return False
```

Mirotest also provides tools for [mocking](https://stackoverflow.com/questions/2665812/what-is-mocking) other objects. For this there is a **patch** - function that returns a context manager. Here's an example:

```python
import microtest

import flask_app.commands as commands


@microtest.test
def test_database_init_command(app):
    runner = app.test_cli_runner()
    items = {'init_called': False}

    def dummy_init(*args, **kwargs):
        nonlocal items
        items['init_called'] = True
    
    items['init'] = dummy_init

    with microtest.patch(commands, 'database', microtest.PatchObject(items)):
        result = runner.invoke(args=['init-db'])
        assert items['init_called']
        assert 'Database initialized' in result.output
```

This test is pretty much a microtest translation from the [Flask tutorial](https://flask.palletsprojects.com/en/2.0.x/tutorial/tests/) application tests. This test checks the command line function that initializes the database. Because we want the actual database to not be effected by the test, the database module in our tested module's namespace is temporarily replaced by our mock database module.

The **patch** - function takes three arguments:

  - The object to be temporarily replaced by the mock object.
  - The attribute name of the mock object we are replacing.
  - The mock object.

Here the mock object is an object provided byt microtest called **PatchObject**. It is simply a thin wrapper around a dictionary, so that you can access it by **getattr** and **setattr**. This allows easy introspection on the modifications made to the mock object.

Within the context manager microtest will route the calls to getattr to the mocked object, if the requested attribute is found. If the getattr fails on the mock object, the getattr is routed back to the original object.

See the python unittest documentation on [patching](https://docs.python.org/3/library/unittest.mock.html#where-to-patch) for more info.