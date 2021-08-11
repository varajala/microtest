import microtest


cleanup_called = False


@microtest.setup
def setup_func():
    raise RuntimeError


@microtest.cleanup
def cleanup_func():
    global cleanup_called
    cleanup_called = True


@microtest.test
def test():
    assert True
    


if __name__ == '__main__':
    microtest.run()
    assert cleanup_called