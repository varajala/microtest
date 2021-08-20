import microtest
import functools


calls = list()

def add_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        calls.append(func.__name__)
        return func(*args, **kwargs)
    return wrapper


@microtest.setup
@add_call
def setup():
    pass

@microtest.reset
@add_call
def reset():
    pass

@microtest.cleanup
@add_call
def cleanup():
    assert calls == ['setup', 'reset', 'test_1', 'reset', 'test_2', 'reset', 'test_3', 'cleanup']

@microtest.test
@add_call
def test_1():
    pass

@microtest.test
@add_call
def test_2():
    pass

@microtest.test
@add_call
def test_3():
    pass


if __name__ == '__main__':
    microtest.run()
