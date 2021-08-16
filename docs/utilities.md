## Utilities

It is very common for Python projects to have the following structure:

```
project
├── project
├── docs
├── tests
├── README
├── LICENSE
└── setup.py

```

Here the actual code is inside the project/project directory and the tests are in separate project/tests directory.
For smaller projects tests usually fit inside a single directory, but when the project grows larger
usually the tests are split into more than one directory. This means that if you want to share code
between test modules, you have to install the tests as a separate Python package for import to work (or hack sys.path...).

Microtest aims to prevent this by providing a separate configuration step before the actual testing.
Here you can execute arbitrary Python code for defining utilites, setting up shared resources, etc.
These objects can then be shared between all tested modules with two microtest's tools:
[resources](resources.md) and utilities.

Utilities are meant to replace Pythons **import** statement. When you add an object as a utility, microtest will insert it into a dictionary and this dictionary will be used as the global namespace
that the test modules are executed.

To add an object as utility, use the **microtest.utility** function. This can be used as a decorator
for functions and classes, or explicitly give an existing object a name as keyword argument. 

Here's an example:

```python
import sqlite3
import tempfile
import os
import microtest


@microtest.utility
def reset_database(conn):
    cursor = conn.cursor()
    table_query = [
        "SELECT name FROM sqlite_master",
        "WHERE type = 'table'",
        "AND name NOT LIKE 'sqlite%';"
    ]
    cursor.execute(' '.join(table_query))
    for name in cursor.fetchall():
        cursor.execute(f'DELETE FROM {name}')
    conn.commit()


@microtest.call
def global_setup():
    fd, path = tempfile.mkstemp()
    microtest.add_resource('conn', sqlite3.connect(path))

    @microtest.on_exit
    def global_cleanup(exc_type, exc, tb):
        os.unlink(path)
        os.close(fd)
```

This would be an example of a global config script where **global_setup** function defines a resource: a sqlite database connection object. Because we don't want any of our tests to have side effects on our other tests, we want the database to be cleared after every test that makes modifications to the database. Our **reset_dataabse** function does exactly that. Because we used the **microtest.utility** decorator to inject this function into every test module's global namespace.

We could have added the **reset_database** function as a utility also by removing the **microtest.utility** decorator and by adding the following line into the **global_setup** function:

```python
microtest.utility(reset_database, name='foo')
```

Now the **reset_database** function object would be accessible under the identifier 'foo'.
