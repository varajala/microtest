"""
Author: Valtteri Rajalainen
Edited: 30.4.2021
"""

import time
import sys

from microtest.data import *

output_mode = Output.DEFAULT
out = sys.stdout
use_colors = False
width = 75
running = True
wait_period = 0.1

def run(queue):
    global use_colors
    if out.isatty():
        use_colors = True

    tasks = {
        Task.START:log_start_info,
        Task.TEST:log_test_info,
        Task.STOP:stop,
    }

    while running:
        if queue.empty():
            time.sleep(wait_period)
            continue

        task = queue.get()
        logger_func = tasks[task.type]
        logger_func(task.data)


def write_out(text, color=None):
    if not use_colors:
        out.write(text)
        return
    out.write(color)
    out.write(text)
    out.write(Colors.RESET)


def write_separator(char, separation=1):
    out.write((width // separation) * char)
    out.write('\n')


def log_start_info(data):
    if output_mode == Output.MINIMAL:
        return
    
    write_separator('=')
    write_out('Started testing...\n')
    write_separator('=')


def log_test_info(data):
    assert isinstance(data, TestCase)


def log_modules(data):
    pass


def stop(data):
    global running
    running = False
    
    assert isinstance(data, StopInfo)

    write_separator('-', 2)

    t_delta = round(data.t_stop - data.t_start, 3)
    write_out(f'Finished in {t_delta}s.\n\n')

    if data.modules:
        m = len(data.modules)
        msg = f'Executed {m} modules.\n' if m != 1 else f'Executed 1 module.\n'
        write_out(msg)

    n = data.tests
    msg = f'Ran {n} tests.\n\n' if n != 1 else 'Ran 1 test.\n\n'
    write_out(msg)

    errors = data.errors
    if errors:
        write_out(f'ERRORS: {errors}\n', Colors.FAILED_RED)
        return

    write_out(f'OK.\n', Colors.OK_GREEN)