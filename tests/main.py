import microtest


# class TestLogger:
    
#     def log_start_info(self):
#         pass

#     def log_test_info(self, name, result, exc):
#         pass

#     def log_module_exec_error(self, module_path, exc_type, exc, tb):
#         pass

#     def log_module_info(self, module_path):
#         pass
    
#     def log_results(self, tests, failed, errors, time):
#         pass

#     def terminate(self):
#         pass

# microtest.set_logger(TestLogger())


microtest.exec_name = '__main__'

microtest.exclude_modules('fixture_error_test')


@microtest.on_exit
def teardown(exc_type, exc, tb):
    print('\n  [ EXIT ]')


@microtest.resource
def data():
    return list(range(2, 10, 2))


@microtest.resource
def more_data(data):
    return data + list(reversed(data))


@microtest.utility
class TestUtility:
    pass


@microtest.call
def init_func(data, more_data):
    assert data is not None
    assert more_data is not None
    microtest.utility('foo', name='foo')
    assert microtest.core.running == False

    print('\n  [ START ]  \n')