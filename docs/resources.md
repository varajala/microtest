## Resources

Many tests require some external entities that should be reused for efficient and fast testing.
Some examples of this are database connections, WSGI application instances, or functions that generate
fake test data. Microtest provides **resources** to do this.

Resource is basically just an object that can be easily shared across tested modules. Test functions
can 'request' these objects by providing the resource name as named argument in the function declaration. A resource can be a single object, or a function that produces a new object every time the resource is requested.
This functions very similiar to fixtures in [pytest](https://docs.pytest.org/).

<br>

### Adding static resources

To add an object as a resource use the **microtest.add_resource** function. It takes the name of the resource and
the actual object as arguments.

Here's a simple example:

```python
import microtest
import sqlite3


@microtest.setup
def setup():
    conn = sqlite.connect('database.db')
    conn.row_factory = sqlite.Row
    microtest.add_resource('conn', conn)


@microtest.cleanup
def cleanup(conn):
    conn.close()


@microtest.test
def test_something_database_related(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE name = Dave')
    assert cursor.fetchone() is not None


@microtest.test
def test_some_other_thing_database_related(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE name = Bob')
    assert cursor.fetchone() is not None


@microtest.test
def test_more_things_database_related(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE name = Alice')
    assert cursor.fetchone() is not None

    
if __name__ == '__main__':
    microtest.run()
```

Here the sqlite database connection object is created in the **setup** function and added as a resource.
The test functions can then request this resource by adding its name in the function declaration.

Here the connection is closed in the **cleanup** function. You can read more about fixtures and how
they easily provide setup, reset and cleanup actions [here](fixtures.md).

<br>

> **NOTE**: Resources are not exclusive to test functions only.
Also other resources, setup, reset and cleanup functions can request resources.

<br>

### Adding dynamic resources

You can also provide microtest a callable object that is used to dynamically create the requested object every time a resource is requested. This is done by using the **microtest.resource** decorator.

Here's an example:

```python
import microtest
import random


def mergesort(list_: list) -> None:
    """Mergesort for lists of integers..."""
    def merge(list_a, list_b, main_list):
        i = 0
        while list_a and list_b:
            a = list_a.pop(0)
            b = list_b.pop(0)
            if a > b:
                main_list[i] = b
                list_a.insert(0, a)
            else:
                main_list[i] = a
                list_b.insert(0, b)
            i += 1
        while list_a:
            main_list[i] = list_a.pop(0)
            i += 1
        while list_b:
            main_list[i] = list_b.pop(0)
            i += 1
        
    def split(l):
        i = len(l) // 2
        return l[:i], l[i:]
    
    if len(list_) > 1:
        a, b = split(list_)
        mergesort(a)
        mergesort(b)
        merge(a, b, list_)


@microtest.resource
def test_data():
    list_ = [ random.randint(0, 100) for _ in range(100) ]
    return list_, sorted(list_)


@microtest.test
def test_mergesort(test_data):
    list_, result = test_data
    assert mergesort(list_) == result


    
if __name__ == '__main__':
    microtest.run()
```

Now the **test_data** function is called every time some other component requests it, and the
result is passed to the component requesting it.
