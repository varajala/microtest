import microtest


fixture = microtest.Fixture()
cleanup_called = False


@fixture.setup
def setup_func():
    raise RuntimeError


@fixture.cleanup
def cleanup_func():
    global cleanup_called
    cleanup_called = True


@microtest.test
def test():
    assert True
    


if __name__ == '__main__':
    microtest.run()
    assert cleanup_called