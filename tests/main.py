import microtest


microtest.exec_name = '__main__'

#microtest.only_modules('assertion')
microtest.exclude_modules('fixture_error_test')


@microtest.on_exit
def teardown(exc_type, exc, tb):
    print('exit...')


@microtest.resource
def data():
    return list(range(2, 10, 2))


@microtest.resource
def more_data(data):
    return data + list(reversed(data))


@microtest.utility
class TestUtility:
    pass


@microtest.call
def init_func(data, more_data):
    assert data is not None
    assert more_data is not None
    microtest.utility('foo', name='foo')
    assert microtest.core.running == False