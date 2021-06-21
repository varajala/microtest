import runpy


execute = lambda module: list() 


def run(modules, on_error, notify_module=None, exec_name='microtest_runner'):
    for module_path in modules:
        if notify_module:
            notify_module(module_path)
        
        try:
            module = runpy.run_path(module_path, run_name=exec_name)
            for test in execute(module):
                test()
            
        
        except KeyboardInterrupt:
            break

        except SystemExit:
            break

        except Exception as exc:
            exc_type = type(exc)
            traceback = exc.__traceback__
            on_error(module_path, exc_type, exc, traceback)