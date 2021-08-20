import microtest


class Logger:
    
    def log_start_info(self):
        pass

    def log_test_info(self, name, result, exc):
        print(name)

    def log_module_exec_error(self, module_path, exc_type, exc, tb):
        pass

    def log_module_info(self, module_path):
        print(module_path)
    
    def log_results(self, tests, failed, errors, time):
        pass

    def terminate(self):
        pass


microtest.set_logger(Logger())
microtest.only_groups('slow', 'super_slow')

print('config executed')