Back to [docs](index.md)...

<br>

## Fixtures

[Wikipedia](https://en.wikipedia.org/wiki/Test_fixture) defines a test fixture in the following way: 
>"A test fixture is an environment used to consistently test some item, device, or piece of software."

In software testing this means setting up a reproducible environment for a set of tests to be executed in and doing the appropriate cleanup actions after the testing.

Here's an example how microtest allows you to setup certain conditions before executing any tests inside a module:

```python
import sqlite3
import tempfile
import os

import microtest
import tested_module


@microtest.setup
def setup():
    global fd, path
    fd, path = tempfile.mkstemp()
    
    with sqlite3.connect(path) as conn:
        with open('schema.sql') as file:
            conn.executescript(file.read())


@microtest.reset
def reset():
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users')
        conn.commit()


@microtest.cleanup
def cleanup():
    os.unlink(path)
    os.close(fd)
    

@microtest.test
def test_storing_users():
    tested_module.store_user(name='Dave', hobby='fishing')

    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT (name, hobby) FROM users WHERE name = Dave')
        user = cursor.fetchone()
    
    assert user is not None
    name, hobby = tuple(user)
    assert name == 'Dave'
    assert hobby == 'fishing'


if __name__ == '__main__':
    microtest.run()
```

Here the **setup** function will be the very first function to be executed. After the setup is done, microtest will execute all tests in the given module. If the reset function is registered it will be called before every test function. The cleanup will be executed after all tests are executed or if an unhandled exception is raised.

So the order of execution will be:

  - setup
  - reset
  - test_storing_users
  - cleanup

If an exception is raised during setup function, the cleanup function wont be called and the execution of this module is stopped.

All of these functions are optional and you can create any combination of the **setup**, **reset** and **cleanup** functions. For example you may define setup and cleanup functions, but no reset function, or define just a reset function.

These functions define the fixture inside a given module. Microtest also provides ways of defining actions to be done before and after executing the individual test modules. When executing microtest as a module, microtest will first search an entrypoint to perform configuration. You can read the details for setting up this entrypoint in the [config](config.md) section. This entrypoint is a python module, which will be executed before searching and executing the test modules. This is the place to do setup actions before any actual test code is executed.

To do cleanup actions before exiting the program microtest provides the **on_exit** decorator. This is recommended to be defined during the configuration process. The function provided into **on_exit** must take three named arguments: *exception_type*, *exception* and *traceback*. These are similiar to Python's builtin **sys.exc_info**. If microtest exits normally these are all set to None.

Here's an example from the [config](config.md) section that is based on code I have personally used to test Flask applications:

```python
import microtest
import os
import tempfile

from application import create_app
from application.extensions import sqlalchemy


@microtest.call
def setup():
    fd, path = tempfile.mkstemp()
    config = {
        'TESTING': True,
        'SECRET_KEY': 'testing',
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    }
    app = create_app(config)
    microtest.add_resource('app', app)
    
    with app.app_context():
        sqlalchemy.create_all()

    @microtest.on_exit
    def cleanup(exc_type, exc, tb):
        os.unlink(path)
        os.close(fd)

```
This sets up the Flask application instance and makes it available to all test functions in the executed modules. It also creates a temporary file where the sqlite database is created.

The **call** decorator simply calls the setup function when microtest is doing configuration or running. See the [resources](resources.md) section to read more on the **add_resource** function.


<br>

Back to [docs](index.md)...