import microtest


def run_tests():
    test_func1()
    f()
    test_func2()


def f():
    g()

def g():
    h()

def h():
    j()

def j():
    #info = 'Here is info on the exception...'
    rai#se RuntimeError(info)

@microtest.test
def test_func1():
    pass


@microtest.test
def test_func2():
    pass


if __name__ == '__main__':
    run_tests()