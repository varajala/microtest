## Basic Use

Here's the simplest testing program you can create with microtest:

```python
import microtest


@microtest.test
def function():
    x = 10
    assert x < 0
    

if __name__ == '__main__':
    microtest.run()
```

To add a function as a part of the test suite, just decorate it with the **microtest.test** function. This will register the function as a part of the test suite. Inside the test functions you can use the Python's builtin **assert** statement to perform all assertions.

All tests that raise AssertionError will be registered as FAILED and all tests that raise any other exceptions will be registered as ERRORS. 

The **microtest.run** function is needed when you want to automatically run the tests when executing this file as a regular python script. It has no effect when running microtest as a module (see [running](#./running.md) for more details).
