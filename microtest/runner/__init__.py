"""
Runner submodule.
"""
import runpy


def run(modules, on_error, notify_module=None, exec_name='__main__'):
    for module_path in modules:
        if notify_module:
            notify_module(module_path)
        
        try:
            runpy.run_path(module_path, run_name=exec_name)
        
        except KeyboardInterrupt:
            break

        except SystemExit:
            break

        except Exception as exc:
            exc_type = type(exc)
            traceback = exc.__traceback__
            on_error(module_path, exc_type, exc, traceback)