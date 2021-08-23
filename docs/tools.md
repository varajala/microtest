Back to [docs](index.md)...

<br>

## Tools

Microtest provides some useful testing tools for making common testing tasks easier.

  - [Namespaces](#namespaces)
  - [Patching](#patching)
  - [Expecting Erros](#expecting-errors)
  - [Temporary Directory](#temporary-directory)
  - [Restricting File Access](#restricting-file-access)
  - [WSGI server](#wsgi-server)
  - [SMTP server](#smtp-server)

<br>

### Namespaces

Namespaces are a thin wrapper around Python's builtin dictionaries.
They provide access to the given dictionary with **\_\_getattr\_\_** and **\_\_setattr\_\_**.

It is located in the **microtest.utils** module.

Here's an example:

```python
from microtest.utils import Namespace


data = {'name': 'Dave', 'age': 32}
user = Namespace(data)

print(user.name)
# >>> 'Dave'

print(user.age)
# >>> 32

user.age = 33
print(user.age)
# >>> 33

print('hobby' in user)
# >>> False

user.hobby = 'fishing'
print('hobby' in user)
# >>> True

print(data)
# >>> {'name': 'Dave', 'age': 33, 'hobby': 'fishing'}
```

As you can see the Namespace can wrap an existing dictionary and mutate its values.
You can create an empty Namespace by not providing a dictionary in the 'constructor',
this creates a new dictionary for the namespace.

Failed 'key' lookup on the Namespace will raise an AttributeError.

<br>

### Patching

Patching means dynamically modifying some object's state for testing purposes.
Microtest provides a **patch** function to do this.

<br>

```python
def patch(obj: object, **kwargs) -> Patch:
```

The patch function returns a context manager that sets the given attributes to the given values
for the specified object. Here's a simple example what this means:

```python
import microtest
from microtest.utils import Namepace


ns = Namespace()
ns.integer = 42
ns.string = 'foo'

with microtest.patch(ns, integer=0, string='bar'):
    print(ns.integer, ns.string)
    # >>> 0 'bar'

print(ns.integer, ns.string)
# >>> 42 'foo'

```

This is very useful for things like limiting the side effects of tests and temporarily replacing constant values during testing.

Here's a more real-world scenario where I have used patching:

```python
import microtest
from microtest.utils import Namepace

import application.orm.manage as manage


@microtest.test
def test_init_db_cmd(app):

    def dummy_init(*args, **kwargs):
        nonlocal items
        items['init_called'] = True
    
    items = {'init_called': False, 'init': dummy_init}
    runner = app.test_cli_runner()

    with microtest.patch(manage, models = Namespace(items)):
        result = runner.invoke(args=['init-db'])
        assert items['init_called']
```

Here I'm testing the database initialization command from a Flask application.
Because I don't want the actual init command to be called, I'm going to replace it
with the dummy_init command that just sets the init_called flag to True.

The application.orm.manage module calls internally another module called 'models'
where the actual init_db function is defined.

<br>

> **NOTE**: Patching won't work if you import specific items from a module rather than the whole module.
> See https://docs.python.org/3/library/unittest.mock.html#where-to-patch for more info.

<br>

### Expecting Errors

In many cases you may want to test if certain functions with specific arguments
raise some exception or not. Microtest helps you doing so with the **raises** function.

```python
def raises(callable: Callable, params: Union[tuple, dict], exc_type: Class) -> bool:
```

The **raises** function takes a callable object and calls it with the provided
arguments. If the callable raises an exception of type exc_type it returns True.
If any other exception is raised, it is raised normally and if no exceptions are raised, it returns
False.

The params must be a tuple or a dictionary object. If params is a tuple, its contents are passed to the callable as named arguments.
If params is a dict, its contents are passed to the callable as keyword arguments.

Here's an example:

```python
import microtest


class TypedDict:
    def __init__(self, *, keys, values):
        self.t_keys = keys
        self.t_values = values
        self.items = dict()

    def __getitem__(self, key):
        return self.items[key]

    def __setitem__(self, key, value):
        if not isinstance(key, self.t_keys):
            raise TypeError(f'Key is not type of "{self.t_keys}"')
        if not isinstance(value, self.t_values):
            raise TypeError(f'Value is not type of "{self.t_values}"')
        self.items[key] = value

    def __contains__(self, item):
        return item in self.items


@microtest.test
def test_adding_values():
    td = TypedDict(keys=str, values=int)
    td['foo'] = 1
    td['bar'] = 2
    assert td['foo'] == 1
    assert td['bar'] == 2


@microtest.test
def test_adding_invalid_key_type():
    td = TypedDict(keys=str, values=int)
    assert microtest.raises(td.__setitem__, (1, 1), TypeError)


@microtest.test
def test_adding_invalid_value_type():
    td = TypedDict(keys=str, values=int)
    assert microtest.raises(td.__setitem__, ('foo', 'bar'), TypeError)


if __name__ == '__main__':
    microtest.run()

```

<br>

### Temporary Directory

Microtest provides a slightly extended version of **tempfile.TemporaryDirectory**.
It allows to populate the directory easily and remove all of its contents
without removing the actual directory.

See [https://docs.python.org/3/library/tempfile.html#tempfile.TemporaryDirectory](https://docs.python.org/3/library/tempfile.html#tempfile.TemporaryDirectory) for more info on the **tempfile.TemporaryDirectory** and its usage.

The microtest TemporaryDirectory offers the same methods and properties as
the **tempfile.TemporaryDirectory** but adds the following methods and properties:


```python
class TemporaryDirectory:
    """
    A subclass of tempfile.TemporaryDirectory.
    Adds easy population with files and directories
    and clearing all contents without removing the
    directory.
    """
  
  @property
  def path(self):
    """Return the absolute path of this directory as a string."""

  def populate(self, files=list(), dirs=list()):
    """
    For every name in files and dirs, create new file/directory
    inside this temporary directory.
    """

  def delete_contents(self):
    """Delete all files and directories inside this temporary directory."""
```

There is also a function called **create_temp_dir** that creates a new TemporaryDirectory instance
and populates it with the provided items.

```python
def create_temp_dir(files = list(), dirs = list()) -> TemporaryDirectory:
```

The **TemporaryDirectory** class and the **create_temp_dir** function
are located in the **microtest.utils** module.

<br>

### Restricting File Access

Microtest provides a useful context manager for temporarily reducing file or directory
permissions. This context manager is returned by the **set_as_unauthorized** function:

```python
def set_as_unauthorized(path: str) -> ContextManager:
```

For files the the change in permissions is equal to:
    
    chmod u-rw directory
    chmod u-rwx directory/file

For directories the change in permissions is equal to:
    
    chmod u-rwx directory

The original permissions are restored after the context has exited.

<br>

> **NOTE**: The change in permissions is implemented by using os.chmod.
> This is not fully supported on Windows.
> See [https://docs.python.org/3/library/os.html#os.chmod](https://docs.python.org/3/library/os.html#os.chmod) for more info.

<br>

Here's an example:

```python
import tempfile
import os
import microtest
from microtest.utils import set_as_unauthorized


@microtest.setup
def setup():
    path, fd = tempfile.mkstemp()
    microtest.add_resource('path', path)
    microtest.add_resource('fd', fd)


@microtest.cleanup
def cleanup(path, fd):
    os.unlink(path)
    os.close(fd)


def read_file(filepath: str) -> str:
    with open(filepath) as file:
        return file.read()


@microtest.test
def test_unauthorized_files(path):
    with set_as_unauthorized(path):
        assert microtest.raises(read_file, (path,), PermissionError)

```
<br>

The **set_as_unauthorized** function is located in the **microtest.utils** module.

<br>

### WSGI Server

Microtest provides a simple function to start a WSGI server for testing using Python's builtin
wsgiref.simple_server module.

```python
def start_wsgi_server(wsgi_app: object, *, port: int, host: str = 'localhost', wait = True) -> Process:
```

The **start_wsgi_server** function runs a web server in the address host:port.
The provided wsgi_app must be a valid WSGI application specified by PEP 3333.
If wait is True this call blocks until a connection can be established with the server.
The server is executed in another process. The returned Process instance has the following methods and properties:

```python
class Process:
    """
    A wrapper object that holds refrences to a process object and
    a text stream where the process's output is directed.
    
    The wrapper process object can be an instance of subprocess.Popen 
    or multiprocessing.Process.
    """

  @property
  def running(self) -> bool:
    pass

  def read_output(self, *, read_all=False):
    """
    Read the output that the wrapped process has produced since
    last read. If read_all is set to True, all output that the
    process has ever produced will be read.
    """

  def kill(self):
    """Kill the running process and close the output stream."""

  def terminate(self):
    """Terminate the running process and close the output stream."""
```
The **start_wsgi_server** function is located in the **microtest.utils** module.

<br>

### SMTP Server

Microtest provides a simple function to start a SMTP server for testing using Python's builtin smtpd module.

```python
def start_smtp_server(*, port: int, host: str = 'localhost', wait = True) -> Process:
```

The **start_smtp_server** function runs a smtp server in the address host:port.
If wait is True this call blocks until a connection can be established with the server.
The server is executed in another process.
The returned Process instance is similiar to one returned by **start_wsgi_server**.

The **start_smtp_server** function is located in the **microtest.utils** module.

<br>

Back to [docs](index.md)...
