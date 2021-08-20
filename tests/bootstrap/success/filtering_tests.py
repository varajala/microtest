import sys
import subprocess
import microtest
import os
import tempfile


def run_microtest_as_module(directory: str) -> str:
    cmd = [sys.executable, '-m', 'microtest', directory]
    stream = tempfile.TemporaryFile(mode='w+')
    
    proc = subprocess.Popen(cmd, stdout = stream, cwd = directory)
    proc.wait()
    
    stream.seek(0)
    data =  stream.read()
    stream.close()
    return data


def join_asset_path(*args):
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.dirname(path)
    path = os.path.dirname(path)
    path = os.path.join(path, 'assets')
    for name in args:
        path = os.path.join(path, name)
    return path
    


@microtest.test
def test_exclude_modules():
    output = run_microtest_as_module(join_asset_path('module_filtering', 'exclude_modules'))
    assert 'config executed' in output
    assert 'run_this_test' in output


@microtest.test
def test_only_modules():
    output = run_microtest_as_module(join_asset_path('module_filtering', 'only_modules'))
    assert 'config executed' in output
    assert 'run_this_test' in output
    assert 'exec_this_test' in output


@microtest.test
def test_exclude_groups():
    os.environ['MICROTEST_ENTRYPOINT'] = 'exclude_slow.py'
    output = run_microtest_as_module(join_asset_path('test_filtering'))
    assert 'config executed' in output
    assert 'slow_test' not in output
    assert 'normal_test' in output


@microtest.test
def test_only_groups():
    os.environ['MICROTEST_ENTRYPOINT'] = 'only_slow.py'
    output = run_microtest_as_module(join_asset_path('test_filtering'))
    assert 'config executed' in output
    assert 'slow_test' in output
    assert 'normal_test' not in output
