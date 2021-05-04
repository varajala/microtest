import microtest


fixture = microtest.Fixture()
calls = []


@fixture.setup
def setup_func():
    calls.append('setup')


@fixture.cleanup
def cleanup_func():
    calls.append('cleanup')


def func1():
    calls.append('func1')


def func2():
    calls.append('func2')


def func3():
    raise RuntimeError()
    calls.append('func3')


@microtest.test
def assertion():
    print(calls)
    assert calls == ['setup', 'func1', 'func2', 'cleanup']


def main():
    try:
        with fixture:
            func1()
            func2()
            func3()
    except:
        assertion()


if __name__ == '__main__':
    main()