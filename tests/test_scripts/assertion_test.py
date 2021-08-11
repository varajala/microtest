import microtest


variable = 1


@microtest.cleanup
def cleanup():
    global variable
    variable = 0


@microtest.test
def test():
    assert variable == 0


if __name__ == '__main__':
    microtest.run()