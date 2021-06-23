import microtest


@microtest.test
def test_utilities():
    assert TestUtility() is not None
    assert foo == 'foo'


if __name__ == '__main__':
    microtest.run()