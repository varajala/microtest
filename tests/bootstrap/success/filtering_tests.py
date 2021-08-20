import sys
import subprocess
import microtest
import os
import tempfile


def run_microtest(directory: str) -> str:
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
    for name in args:
        path = os.path.join(path, name)
    return path
    


@microtest.test
def test_exclude_modules():
    output = run_microtest(join_asset_path('module_filtering', 'exclude_modules'))
    assert 'config executed' in output
    assert 'run_this_test' in output


@microtest.test
def test_only_modules():
    output = run_microtest(join_asset_path('module_filtering', 'only_modules'))
    assert 'config executed' in output
    assert 'run_this_test' in output
    assert 'exec_this_test' in output
