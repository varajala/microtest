Back to [docs](index.md)...

<br>


## Configuring

As mentioned in the [running](running.md) section, when executing microtest as a module the first things that happen are:

  - microtest will try to find a config script
  - run the config script if found

The config script is simply a Python module containing arbitrary Pyhton code.
It is executed before any tests are discovered or executed so you can perform the following actions:

  - Alter how test modules are discovered
  - Alter the **\_\_name\_\_** - attribute of the executed modules
  - Filter test modules by their filepath
  - Filter tests by groups
  - Change the way output is logged by replacing the default logger
  - Define [utilites](utilities.md) to be shared across all test modules
  - Add [resources](resources.md) to be shared across all test modules
  - Register cleanup actions to be preformed before exiting the program
  - Execute arbitrary Python code before testing (ask user input for options, etc...)

The config script is by default a file called **main.py**
inside the directory provided as command line argument.
This can be modified by setting an environment variable called
**MICROTEST_ENTRYPOINT** to point to a file you want to be executed.
If this path is not absolute, it will be joined with the path provided.

<br>

### Altering module discovery

After the config step is done microtest will search for test modules inside the given directory structure.
The collected test modules are determined by matching the module name against a single regular expression.
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
its compilation fails using re.compile(), a ValueError will be raised.
Comparison is done by using re.fullmatch().
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
When executing the cinfig script it will always be the default value.

It can be useful to set this to something else, for example when running tests built with unittest.
Here's an excerpt from the microtest's own tests:

```python
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

The exclude_modules function will filter those modules out which filepath contains any of the provided strings. For example calling microtest.exclude_modules('validation') with the following set of filepaths:

*tests/test_login.py*
<br>
*tests/test_registering.py*
<br>
*tests/test_form_**validation**.py*
<br>
*tests/**validation**s/test_emails.py*
<br>
*tests/**validation**s/test_usernames.py*

will result to only filepaths *tests/test_login.py* and *tests/test_registering.py*.
The parts that matched the restriction are highlighted.

Calling only_modules will result to execution of only those modules which filepath contains any of the given strings. This is the opposite of exclude_modules.

For example calling microtest.only_modules('validation') with the same set of filepaths
will result to filepaths *tests/test_form_**validation**.py*,
*tests/**validation**s/test_emails.py* and *tests/**validation**s/test_usernames.py*.
The parts that matched the restriction are highlighted. This is true even if exclude_modules was called with restrictions that might filter out some of these modules out.

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