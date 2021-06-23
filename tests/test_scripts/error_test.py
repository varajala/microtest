import microtest


@microtest.test
def test_errors():
    raise Exception('This error should be thrown...')


if __name__ == '__main__':
    microtest.run()