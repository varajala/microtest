"""
Author: Valtteri Rajalainen
Edited: 3.5.2021
"""

import os
import runpy
import threading

import microtest.scanner as scanner
import microtest.logger as logger
import microtest.core as core


EXEC_NAME = '__main__'


def run(root_path):
    """
    Run the scanner from the given path
    and execute all found modules.
    """
    path = os.path.abspath(root_path)
    modules_to_test = (path,)
    if os.path.isdir(path):
        modules_to_test = scanner.find_tests(path)
    _exec_modules(modules_to_test)


def _exec_modules(modules):
    logger_thread = threading.Thread(target=logger.run, args=(core.logger_queue,))
    logger_thread.start()

    core.start_testing()
    
    for module_path in modules:
        try:
            runpy.run_path(module_path, run_name=EXEC_NAME)
        
        except KeyboardInterrupt:
            break

        except SystemExit:
            break

        except Exception as exc:
            core.register_module_exec_error(module_path, exc)

    core.stop_testing()
    logger_thread.join()

"""
def run_from_commandline():
    ARGUMENTS = {
    '-m':TestLogger().minimal_output,
    '--minimal':TestLogger().minimal_output,
    '-v':TestLogger().verbose_output,
    '--verbose':TestLogger().verbose_output,
    }
    arguments = sys.argv[1:]
    if len(arguments) > 0:
        cwd_path = pathlib.Path(os.getcwd())
        path = cwd_path.joinpath(arguments.pop(-1)).resolve()
        while arguments:
            arg = arguments.pop(0)
            if arg not in ARGUMENTS:
                continue
            ARGUMENTS[arg]()
        if path.exists():
            run(path)
"""