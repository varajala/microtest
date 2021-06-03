import microtest


calls = []

def run_tests():
    fixture = microtest.Fixture()
    fixture.setup = setup_func
    fixture.reset = reset_func
    fixture.cleanup = cleanup_func

    tests = [func1, func2, func3]
    with fixture:
        fixture.run(tests)


def setup_func():
    calls.append('setup')


def reset_func():
    calls.append('reset')


def cleanup_func():
    calls.append('cleanup')
    assert calls == ['setup', 'func1', 'reset', 'func2', 'reset', 'func3', 'reset', 'cleanup']
    return True


def func1():
    calls.append('func1')


def func2():
    calls.append('func2')


def func3():
    calls.append('func3')
    raise RuntimeError()


if __name__ == '__main__':
    run_tests()