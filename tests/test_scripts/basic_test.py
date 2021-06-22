import microtest


@microtest.test
def function():
    assert True


if __name__ == '__main__':
    microtest.run()