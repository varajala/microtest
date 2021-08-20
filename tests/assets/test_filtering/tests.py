import microtest


@microtest.group('slow')
@microtest.test
def slow_test_1():
    raise RuntimeError()


@microtest.group('slow')
@microtest.test
def slow_test_2():
    raise RuntimeError()


@microtest.group('super_slow')
@microtest.test
def super_slow_test():
    raise RuntimeError()


@microtest.test
def normal_test_1():
    pass

@microtest.test
def normal_test_2():
    pass

@microtest.test
def normal_test_3():
    pass
