import microtest


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


microtest.utility('foo', name='foo')