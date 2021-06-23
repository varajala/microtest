import microtest


calls = []

fixture = microtest.Fixture()


@fixture.setup
def setup_func():
    calls.append('setup')


@fixture.reset
def reset_func():
    calls.append('reset')


@fixture.cleanup
def cleanup_func():
    calls.append('cleanup')
    assert calls == ['setup', 'reset', 'func1', 'reset', 'func2', 'reset', 'func3', 'cleanup']


@microtest.test
def func1():
    calls.append('func1')


@microtest.test
def func2():
    calls.append('func2')


@microtest.test
def func3():
    calls.append('func3')
    raise RuntimeError()


if __name__ == '__main__':
    microtest.run()