Back to [docs](index.md)...

<br>


## Configuring

As mentioned in the [running](running.md) section, when executing microtest as a module the first things that happen are:

  - microtest will try to find a config script
  - run the config script if found

The config script is simply a Python module containing arbitrary Python code.
It is executed before any tests are discovered or executed so you can perform the following actions:

  - Alter how test modules are discovered
  - Alter the **\_\_name\_\_** - attribute of the executed modules
  - Filter test modules by their filepath
  - Filter tests by groups
  - Change the way output is displayed by replacing the default logger
  - Define [utilites](utilities.md) to be shared across all test modules
  - Add [resources](resources.md) to be shared across all test modules
  - Register cleanup actions to be preformed before exiting the program
  - Execute arbitrary Python code before testing (ask user input for options, etc...)

<br>

> **NOTE**:You should not include any tests inside the config script.

<br>

The config script is by default a file called **main.py**
inside the directory provided as command line argument.
This can be modified by setting an environment variable called
**MICROTEST_ENTRYPOINT** to point to a file you want to be executed.
If this path is not absolute, it will be joined with the path provided.


If microtest doesn't recieve any command line arguments, the current working directory is used.

<br>

### Altering module discovery

After the config step is done microtest will search for test modules inside the given directory structure.
Which modules are collected is determined by matching the module name against a single regular expression.
Here's the default value of this regex:

```python
r'tests?_\w+\.py|\w+_tests?\.py|tests?\.py'
```

It will match modules which name:

  - starts with **test_** or **tests_**
  - ends with **_test** or **_tests**
  - is equal to **test** or **tests**

This regex can be set directly by using the **microtest.set_module_discovery_regex** function.
It takes a single string as an argument. This string is expected to be a valid regex and if
its compilation fails using re.compile, a ValueError will be raised.
Comparison is done by using re.fullmatch.
Note that the this is done against the modules's name, not the full filepath.

<br>

> **NOTE**: Modules are discovered using breadth-first-search. This means that modules higher in
> the directory hierachy are excecuted before modules that are lower in the directory hierarchy.
> **This can be relied on.**

> **NOTE**: Modules inside the same directory are executed in the order dependent on the
> underlying filesystem, they are not sorted in any way.
> **You should not rely on any particular order of execution of modules inside the same directory**.

<br>

### Setting the \_\_name\_\_ - attribute

The \_\_name\_\_ - attribute of the executed modules can be simply altered by setting the **microtest.exec_name**
to the string you want it to be. This defaults to **'microtest_runner'**.
When executing the config script it will always be the default value.

It can be useful to set this to something else, for example when running tests built with unittest.

Here's an example:
```python
#in main.py
import microtest

microtest.exec_name = '__main__'
```

```python
#in assertion_tests.py
import unittest
import microtest.assertion as assertion


class Tests(unittest.TestCase):

    def test_basic_assertion(self):
        x = 2
        try:
            assert x == 1
        except AssertionError as err:
            result = assertion.resolve_assertion_error(type(err), err, err.__traceback__)
            self.assertTrue('assert 2 == 1' in result)


    def test_func_assertion(self):
        func = lambda s: s.upper()
        try:
            assert func('spam') == 'spam'
        except AssertionError as err:
            result = assertion.resolve_assertion_error(type(err), err, err.__traceback__)
            self.assertTrue("assert 'SPAM' == 'spam'" in result)


if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)
```

Now these tests can be ran normally with microtest when the exec_name is set to **'\_\_main\_\_**.
Here's how the output looks:

```
=======================================================================
Started testing...
=======================================================================

/home/varajala/dev/py/microtest/tests/assertion_tests.py
..
----------------------------------------------------------------------
Ran 2 tests in 0.001s

OK

-----------------------------------------------------------------------
Ran 0 tests in 0.012s.

OK.

```

As you can see, microtest doesn't really support unittest right now,
but the tests can be executed by calling the **unittest.main** function.
This might be added into microtest in future updates.

<br>

### Filtering executed modules

Before we took a look on how to alter the test discovery.
However using the default patterns for discovering tests and filtering them is much easier.

There are two functions to filter modules:
**microtest.exclude_modules** and **microtest.only_modules**.
They both take an arbitrary numer of strings as named arguments.

The exclude_modules function will filter those modules out which filepath contains any of the provided strings. For example calling **microtest.exclude_modules('validation')** with the following set of filepaths:

*tests/test_login.py*
<br>
*tests/test_registering.py*
<br>
*tests/test_form_**validation**.py*
<br>
*tests/**validation**s/test_emails.py*
<br>
*tests/**validation**s/test_usernames.py*

will result only *tests/test_login.py* and *tests/test_registering.py* to be executed.
The parts that matched the restriction are highlighted.

Calling only_modules will result to execution of only those modules which filepath contains any of the given strings. This is the opposite of exclude_modules.

For example calling **microtest.only_modules('validation')** with the same set of filepaths
will result to  *tests/test_form_**validation**.py*,
*tests/**validation**s/test_emails.py* and *tests/**validation**s/test_usernames.py* be executed.
The parts that matched the restriction are highlighted.

<br>

> **NOTE**: using **only_modules** will result to ignoring any restrictions set by **exclude_modules**.

<br>

### Filtering tests by groups

Tests can be added into a group by using the **microtest.group** decorator.
Here's an example where the function *foo* is added to the group named *bar*:

```python
import microtest


@microtest.group('bar')
@microtest.test
def foo():
    assert 1 + 1 == 2
```

<br>

> **NOTE**: When using **microtest.group** decorator, remember to add the group
> decorator **ontop** of the microtest.test decoratror.

<br>

To select what groups to execute, we have two functions
**microtest.exclude_groups** and **microtest.only_groups** similiar to filtering modules.

These work exactly the same way: they take an arbitrary number of strings as arguments and
they select the filtered tests based on these.

**exclude_groups** will remove tests with the groups provided from being executed.
**only_groups** will execute only tests with the provided groups.

<br>

> **NOTE**: Like in module filtering using **only_groups** will result to ignoring
> any restrictions set by **exclude_groups**.

<br>

### Creating a custom logger

You can format the output to your liking by replacing the default microtest logger.
Logger is the component reponsible of displaying the test results to the user.

The default logger can be changed with any object that implements the logger interface.
This is checked when testing is started and TypeError is raised if the provided object
doesn't match this interface.

Here's how the interface looks:

```python
class Logger:

    def log_start_info(self):
        pass

    def log_test_info(self, name, result, exc):
        pass

    def log_module_exec_error(self, module_path, exc_type, exc, tb):
        pass

    def log_module_info(self, module_path):
        pass
    
    def log_results(self, tests, failed, errors, time):
        pass

    def terminate(self):
        pass


microtest.set_logger(Logger())
```

Note that the actual implementation doesn't have to be a class that you instantiate.
You could also do the following:

```python
#in custom_logger.py

def log_start_info():
    pass

def log_test_info(name, result, exc):
    pass

def log_module_exec_error(module_path, exc_type, exc, tb):
    pass

def log_module_info(module_path):
    pass

def log_results(tests, failed, errors, time):
    pass

def terminate():
    pass
```
```python
#in tests/main.py

import microtest
import custom_logger

microtest.set_logger(custom_logger)
```

The logger implementation **must** provide all the functions above with the **same exact signature**.
Yes, even the variable names must match. This ensures that there is the correct number of named arguments. Let's walk trough the functions one by one.

<br>

```python
log_start_info()
```
Function called when testing is started.
The default implementation logs the 'Started testing...' message.

<br>

```python
log_test_info(name: str, result: str, exc: Exception | None)
```
Function called for every test executed.
<br>
*name* is a string which is the name of the test function.
<br>
*result* is a string representing the result.<br>
Its value is one of the following:<br>
  - microtest.objects.Result.OK = 'OK'
  - microtest.objects.Result.ERROR = 'ERROR'
  - microtest.objects.Result.FAILED = 'FAILED'

Result.FAILED means that an assertion failed,
Result.ERROR means that some other exception was raised.
<br>
*exc* is the Exception instance that was raised during the test or None if result == Result.OK.

<br>

```python
log_module_exec_error(module_path: str, exc_type: Class, exc: Exception, tb: Traceback)
```
Function called when an unhandled exception is raised during module execution (outside of test functions)
<br>
*module_path* is the absolute filepath of this module as a string.
<br>
*exc_type* is the class of the raised exception.
<br>
*exc* is the Exception instance raised during module execution.
<br>
*tb* is a traceback object for the raised exception.

<br>

```python
log_module_info(module_path: str)
```
Function called before the module is executed.
*module_path* is the absolute filepath of this module as a string.

<br>

```python
log_results(tests: int, failed: int, errors: int, time: float)
```
Function to be called after all tests are executed.
This should not be used to do any cleanup actions.
<br>
*tests* is an integer of how many tests were executed.
<br>
*failed* is an integer of how many tests failed (AssertionError was raised).
<br>
*errors* is an integer of how many tests failed due to an exception (not AssertionError).
<br>
*time* is a float that represents the execution time in seconds.

<br>

```python
terminate()
```
Function guarateed to be called before the program exits.
Do cleanup operations here.

<br>

> **NOTE**: Microtest uses coloured output by default on mac and linux, since they support ANSI coloring.
>When on Windows microtest will remind you to install
> [colorama](https://github.com/tartley/colorama)
>every time you run it without it being installed.
>It converts the ANSI escape sequences to win32 API calls.

<br>

### Setting up the test suite

During the configuration you can also do setup actions that have effect on entire test suite.
It is recommended that all [resources](resources.md) and [utilites](utilites.md) are defined here.
This way you avoid tests using resources or utilites that aren't yet created.

All possible resources or utilites taht require cleaning up can be done with the **microtest.on_exit** decorator.
This registers a function to be called right before the program is about to exit even, wheter the
exiting is done normally or due to an exception.

Here's an example of a config I've used in some of my Flask projects:

```python
import microtest
import os
import re
import tempfile

from application import create_app
from application.extensions import sqlalchemy


@microtest.utility
class TestClient:
    """
    A simple wrapper on flask test client that
    can do login, logout and registering easily.

    Supports csrf_tokens.
    """

    login_url = '/auth/login'
    logout_url = '/auth/logout'
    register_url = '/auth/register'
    csrf_token_name = 'csrf_token'

    def __init__(self, app):
        self.client = app.test_client()

    
    def login_as(self, username: str, password: str, *, find_csrf_token=True):
        response = self.client.get(self.login_url)
        form_data = {'username':username, 'password':password}
        
        if find_csrf_token:
            csrf_token = self.find_csrf_token(response.data)
            if csrf_token:
                form_data[self.csrf_token_name] = csrf_token
        
        response = self.client.post(self.login_url, data=form_data)
        return response


    def register_as(self, username: str, email: str, password: str, *, confirm_password=True):
        form_data = {
            'username':username,
            'email':email,
            'password1':password,
            'password2':password if confirm_password else ''
        }
        return self.client.post(self.register_url, data=form_data)

    
    def logout(self, *, find_csrf_token=True):
        form_data = dict()
        response = self.client.get(self.logout_url)
        
        if find_csrf_token:
            csrf_token = self.find_csrf_token(response.data)
            if csrf_token:
                form_data[self.csrf_token_name] = csrf_token
        
        return self.client.post(self.logout_url, data=form_data)


    def find_csrf_token(self, data: bytes) -> str:
        token_name = self.csrf_token_name
        input_tag_exp = re.compile(b'<input.*>')
        matches = re.finditer(input_tag_exp, data)
        if not matches:
            return None

        for match in matches:
            match_str = match.group()
            if match_str.find(f'name="{token_name}"'.encode()) != -1:
                token_exp = re.compile(b'(?<=value=").*(?=")')
                token = re.search(token_exp, match_str)
                if token is not None:
                    return token.group().decode()
        return None


    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            client = object.__getattribute__(self, 'client')
            return object.__getattribute__(client, attr)


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

Here the TestClient is defined as utility, which means that it is injected into every test
module's namespace when executed. This simply replaces imports.

The setup function decorated with the **microtest.call** decorator is called only if microtest
is doing configuration or running.
This acts similiarly as the *if \_\_name\_\_ == '\_\_main\_\_'* guard.
It prevents the setup function to be called if this module would be imported,
but calls it when microtest is in the configuration step.

Inside the setup function a temporary file is created for the sqlite database and the actual Flask
application instance is initialized. This application instance is shared between all test modules, so it is added as a resource.

The temporary file is deleted in the cleanup function.

<br>

Back to [docs](index.md)...