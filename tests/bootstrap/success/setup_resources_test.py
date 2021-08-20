import microtest


@microtest.resource
def int_list():
    return [i for i in range(1, 11)]


@microtest.resource
def int_list_squared(int_list):
    return [i * i for i in int_list]


@microtest.call
def add_foo():
    microtest.add_resource('foo', 'bar')
