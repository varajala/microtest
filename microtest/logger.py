"""
Author: Valtteri Rajalainen
Edited: 3.5.2021
"""

import time
import sys
import os
import traceback

from microtest.data import *


"""
Dispathcer is a callable object that takes the task as named argument
and returns a callable depending on the task's type that takes
the task.data object as named argument.
"""
def default_dispatcher(task):
    tasks = {
        Task.START:log_start_info,
        Task.TEST:log_test_info,
        Task.STOP:stop,
        Task.EXEC_ERR:log_exec_error,
    }

    assert isinstance(task, Task)
    return tasks[task.type]


output_mode = Output.DEFAULT
out = sys.stdout
use_colors = False
width = 75
running = False
wait_period = 0.01
dispatcher = default_dispatcher


def run(queue):
    global use_colors, running
    if out.isatty():
        use_colors = True

    #redirect sys.stderr to NULL
    sys.stderr = open(os.devnull, 'w') 

    running = True
    while running:
        if queue.empty():
            time.sleep(wait_period)
            continue

        task = queue.get()
        logger_func = dispatcher(task)
        logger_func(task.data)


def write_out(text, color=None):
    if not use_colors or color is None:
        out.write(text)
        return
    
    out.write(color)
    out.write(text)
    out.write(Colors.RESET)


def write_separator(char, separation=1):
    out.write((width // separation) * char)
    out.write('\n')


def write_traceback(exc):
    exc_type = type(exc)
    tb = exc.__traceback__
    traceback_str = '\n'.join(traceback.format_exception(exc_type, exc, tb))
    write_out(traceback_str)


def log_start_info(data):
    write_separator('=')
    write_out('Started testing...\n')
    write_separator('=')


def log_test_info(data):
    assert isinstance(data, TestCase)
    if not data.success and output_mode != Output.MINIMAL:
        write_out(f'Failed assertion:\n\n', Colors.FAILED_RED)
        write_traceback(data.exception)
        write_separator('-')


def log_exec_error(data):
    assert isinstance(data, ModuleExecError)
    exc = data.exception
    exc_name = exc.__class__.__name__
    
    if output_mode != Output.MINIMAL:
        write_out(f'{exc_name} occured in module: {data.path}\n\n', Colors.FAILED_RED)
        write_traceback(exc)
        write_separator('-')


def log_module_info(module_dict):
    assert isinstance(module_dict, dict)
    for module, tests in module_dict.items():
        write_out(module, Colors.INFO_CYAN)
        write_out(':\n')
        for test in tests:
            write_out(test.func)
            padding = width - len(test.func) - 7
            write_out('' + padding * '.' + ' ')

            msg = 'OK'
            color = Colors.OK_GREEN
            if not test.success:
                msg = 'ERROR'
                color = Colors.FAILED_RED
            write_out(msg, color)
            write_out('\n')
        write_out('\n\n')


def stop(data):
    global running
    running = False
    
    assert isinstance(data, StopInfo)

    if data.modules and output_mode == Output.VERBOSE:
        log_module_info(data.modules)
        write_separator('-')

    if data.modules:
        m = len(data.modules)
        msg = f'Executed {m} modules.\n' if m != 1 else f'Executed 1 module.\n'
        write_out(msg)

    n = data.tests
    t_delta = round(data.t_stop - data.t_start, 3)
    msg = f'Ran {n} tests in ' if n != 1 else 'Ran 1 test in '
    msg += f'{t_delta}s.\n\n'
    write_out(msg)

    errors = data.errors
    if errors:
        write_out(f'ERRORS: {errors}\n\n', Colors.FAILED_RED)
        return

    write_out('OK.\n\n', Colors.OK_GREEN)
    
    #close the devnull stream, redirect stderr back to default
    sys.stderr.close()
    sys.stderr = sys.__stderr__