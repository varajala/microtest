import microtest


def run_tests():
    test_func1()
    test_func2()
    test_func3()


@microtest.test
def test_func1():
    assert 10 > 0


@microtest.test
def test_func2():
    x = 1
    assert 10 < x, (10, x)


@microtest.test
def test_func3():
    raise TypeError