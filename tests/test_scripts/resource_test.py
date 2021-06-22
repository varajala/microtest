import microtest


@microtest.test
def test_resurces(data):
    assert data == [2, 4, 6, 8]


@microtest.test
def test_resurces(data, more_data):
    assert more_data == [2, 4, 6, 8, 8, 6, 4, 2]


if __name__ == '__main__':
    microtest.run()