import microtest


raise RuntimeError


@microtest.test
def test_exec_err():
    assert False, 'Execution of this module should have been stopped...'


if __name__ == '__main__':
    microtest.run()