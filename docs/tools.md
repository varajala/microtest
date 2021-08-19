Back to [docs](index.md)...

<br>

## Tools

Microtest provides some useful testing tools for making common testing tasks easier.

  - [Namespace](#namespace)
  - [patch](#patch)
  - [create_temp_dir](#create_temp_dir)
  - [set_as_unauthorized](#set_as_unauthorized)
  - [start_wsgi_server](#start_wsgi_server)
  - [start_smtp_server](#start_smtp_server)

<br>

### Namespace

Namespaces are a thin wrapper around Python's builtin dictionaries.
They provide dictionary access with **\_\_getattr\_\_** and **\_\_setattr\_\_**.
It is located in the microtest.utils module.

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

As you can see the Namespace can wrap an exitinsing dictionary and mutate its values.
You can create an empty Namepace by not providing a dictionary in the 'constructor',
this creates a new dictionary for the namespace.

Failed 'key' lookup on the Namespace will raise an AttributeError.

<br>

### Patch

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

