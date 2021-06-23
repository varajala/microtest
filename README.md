# microtest
Simple but powerful testing utilities for Python.


## Table of contents
- [Installation](#installation)
- [Basic Use](#basic-use)
- [Discovering tests](#discovering-tests)
- [Fixtures](#fixtures)
- [Config](#config)

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
 ```shell
===========================================================================
Started testing...
===========================================================================

/home/varajala/dev/python/test.py
test_func ................................................................. OK    

---------------------------------------------------------------------------
Ran 1 tests in 0.001s.

OK.
 ```
 
 ## Discovering tests

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

## Config