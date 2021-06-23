import microtest


raise RuntimeError

@microtest.test
def test_func1():
    pass


@microtest.test
def test_func2():
    pass


if __name__ == '__main__':
    microtest.run()