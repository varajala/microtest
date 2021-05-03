import microtest


def run_tests():
    test_func1()
    test_func2()


@microtest.test
def test_func1():
    assert 10 > 0


@microtest.test
def test_func2():
    assert 10 < 0


if __name__ == '__main__':
    run_tests()