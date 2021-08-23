import os
import sys
import subprocess


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
UNITTESTS_PATH = os.path.join(ROOT_PATH, 'unittests')
BOOTSTRAP_PATH = os.path.join(ROOT_PATH, 'bootstrap')


UNITTEST_FILES = [
    'assertion_tests.py',
    'scanner_tests.py',
]


def run_command(cmd: list, path: str) -> str:
    proc = subprocess.Popen(cmd, stdout = sys.stdout, stderr = sys.stderr, cwd = path)
    proc.wait()


def run_unittests():
    for filename in UNITTEST_FILES:
        path = os.path.join(UNITTESTS_PATH, filename)
        cmd = [sys.executable, '-m', 'unittest', path]
        
        print('Executing: ', ' '.join(cmd))
        run_command(cmd, UNITTESTS_PATH)


def run_bootstrap_success():
    path = os.path.join(BOOTSTRAP_PATH, 'success')
    cmd = [sys.executable, '-m', 'microtest', path]
    print('Executing: ', ' '.join(cmd))
    run_command(cmd, path)


def run_bootstrap_fail():
    path = os.path.join(BOOTSTRAP_PATH, 'fails')
    cmd = [sys.executable, '-m', 'microtest', path]
    print('Executing: ', ' '.join(cmd))
    run_command(cmd, path)


def run_tests():
    print('== STARTED TESTING ==\n')
    print('>>> Executing unittests...\n')
    run_unittests()

    print('>>> Executing bootstrapped tests...\n')
    run_bootstrap_success()

    print('>>> The following tests should all produce FAIL or ERROR...\n')
    run_bootstrap_fail()

    print('== DONE ==\n')


if __name__ == '__main__':
    run_tests()
