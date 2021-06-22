import microtest


calls = []

fixture = microtest.Fixture()


@fixture.setup
def setup_func():
    calls.append('setup')
    print(calls)


@fixture.reset
def reset_func():
    calls.append('reset')
    print(calls)


@fixture.cleanup
def cleanup_func():
    calls.append('cleanup')
    print(calls)
    assert calls == ['setup', 'reset', 'func1', 'reset', 'func2', 'reset', 'func3', 'cleanup']
    return True


@microtest.test
def func1():
    calls.append('func1')
    print(calls)


@microtest.test
def func2():
    calls.append('func2')
    print(calls)


@microtest.test
def func3():
    calls.append('func3')
    print(calls)
    raise RuntimeError()


if __name__ == '__main__':
    microtest.run()