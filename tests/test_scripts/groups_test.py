import microtest


#microtest.exclude_groups('slow')
microtest.only_groups('fast')


@microtest.group('slow')
@microtest.test
def test1():
    print('SLOW test')


@microtest.group('fast')
@microtest.test
def test2():
    print('FAST test')


@microtest.test
def test3():
    print('test')



if __name__ == '__main__':
    microtest.run()