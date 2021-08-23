import microtest


@microtest.test
def test_assertion_error_with_no_body():
    raise AssertionError


@microtest.test
def test_assertion_error_with_info():
    raise AssertionError('This is the exception info')


@microtest.test
def test_plain_assertion_error():
    assert 1 == 2


@microtest.test
def test_assertion_error_with_simple_variable_resolving():
    x = 10
    assert x < 2


@microtest.test
def test_assertion_error_with_func_resolving():
    f = lambda x: x ** 2
    assert f(2) < 2


@microtest.test
def test_assertion_error_with_list_comp_resolving():
    list_ = [i * i for i in range(1, 6)]
    assert list_ == [i * i for i in range(1, 6) if i % 2 == 0]


@microtest.test
def test_assertion_with_context():
    assert False, 'This is the exception context'


@microtest.test
def test_assertion_with_context_tuple():
    x = '10'
    assert x == 10, ('This is the exception context', x)


@microtest.test
def test_assertion_error_with_list_comp_context():
    list_ = [i * i for i in range(1, 6)]
    assert list_ == [i * i for i in range(1, 6) if i % 2 == 0], list_
