import sys
import os
import traceback

from microtest.runner import run
import microtest.scanner as scanner


def main(args):
    cwd = os.getcwd()
    path = cwd
    if args:
        path = args.pop(-1)
        if not os.path.exists(path):
            sys.stderr.write(f'Invalid path: {path}.\n')
            return
        
        if not os.path.isabs(path):
            path = os.path.join(cwd, path)
    
    if os.path.isfile(path):
        run((path,), print_exc)
        return

    modules = scanner.find_tests(path)
    if not modules:
        sys.stdout.write(f'No modules found.\n')
        return
    
    run(modules, print_exc)


def print_exc(module_path, exc_type, exc, tb):
    traceback.print_exception(exc_type, exc, tb)


if __name__ == '__main__':
    main(sys.argv[1:])