import microtest


def run_tests():
    test_func1()
    raise TypeError()
    test_func2()


@microtest.test
def test_func1():
    pass


@microtest.test
def test_func2():
    pass


if __name__ == '__main__':
    run_tests()