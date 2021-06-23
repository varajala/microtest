import microtest


@microtest.resource
def some_resource():
    return 'resource'


microtest.add_resource('Foo', 'Bar')


@microtest.test
def test_resources(some_resource, Foo):
    assert some_resource == 'resource'
    assert Foo == 'Bar'


@microtest.test
def test_global_resources(data, more_data):
    assert data + more_data == [2, 4, 6, 8, 2, 4, 6, 8, 8, 6, 4, 2]


if __name__ == '__main__':
    microtest.run()