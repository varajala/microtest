import microtest


@microtest.test
def test_utilities():
    assert TestUtility() is not None
    assert foo == 'foo'