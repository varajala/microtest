import microtest


@microtest.utility
def utility_function():
    pass


@microtest.utility
class UtilityClass:
    pass


@microtest.call
def add_spam():
    microtest.utility('spam', name='spam')
