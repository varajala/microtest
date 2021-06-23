import microtest


@microtest.test
def test_func1():
    assert 'This is a string' != 'This is a string', 'Error message for this assertion'


@microtest.test
def test_func2():
    x = 1
    assert x > 10 if type(10) == type(func()) else func() == 2, ('This is an error message', 'string')


def func():
    return 1

@microtest.test
def test_func3():
    assert 10 < func()


@microtest.test
def test_func4():
    raise AssertionError


if __name__ == '__main__':
    microtest.run()