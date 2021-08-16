"""
Utility classes and functions for testing.

Author: Valtteri Rajalainen
"""

import stat
import os
import sys
import shutil
import tempfile
import subprocess as subp
import time
import socket

from microtest.objects import Types


class Namespace:
    def __init__(self, items=dict()):
        object.__setattr__(self, 'items', items)

    def __getattribute__(self, attr):
        items = object.__getattribute__(self, 'items')
        if attr not in self:
            raise AttributeError(f'No memeber "{attr}" in namespace')
        return items[attr]

    def __setattr__(self, attr, value):
        object.__getattribute__(self, 'items').__setitem__(attr, value)

    def __contains__(self, item):
        items = object.__getattribute__(self, 'items')
        return item in items.keys()


class TemporaryDirectory(tempfile.TemporaryDirectory):
    @property
    def path(self):
        return os.path.abspath(self.name)

    def populate(self, files=list(), dirs=list()):
        for file in files:
            path = os.path.join(self.path, file)
            open(path, 'x').close()

        for dir_ in dirs:
            path = os.path.join(self.path, file)
            os.mkdir(path)

    def delete_contents(self):
        for entry in os.scandir(self.path):
            if entry.is_dir():
                shutil.rmtree(entry.path)
                continue
            os.remove(entry.path)


class TemporaryFile:
    def __init__(self, **kwargs):
        self.path, self.fd = tempfile.mkstemp(**kwargs)
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close():
        if not self.closed:
            os.unlink(self.path)
            os.close(self)
            self.closed = True


class UnauthorizedFile:
    """
    Context manager that temporarily removes all user permissions
    from the file and read / write permission from the parent
    directory (the file cannot be removed). The permissions are restored
    to the initial values after the context has exited.

    Basically the same as:
    $ chmod u-rw directory
    $ chmod u-rwx file
    """

    NO_PERMISSIONS = 0x0000
    NO_RW_PERMISSION = NO_PERMISSIONS | stat.S_IXUSR

    def __init__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError()
        
        self.file_path = os.path.abspath(path)
        self.file_mode = os.stat(self.file_path).st_mode
        self.dir_path = os.path.dirname(self.file_path)
        self.dir_mode = os.stat(self.dir_path).st_mode

    def __enter__(self):
        os.chmod(self.file_path, self.NO_PERMISSIONS)
        os.chmod(self.dir_path, self.NO_RW_PERMISSION)
        return self

    def __exit__(self, exc_type, exc, tb):
        os.chmod(self.dir_path, self.dir_mode)
        os.chmod(self.file_path,  self.file_mode)


class UnauthorizedDirectory:
    """
    Context manager that temporarily removes all user permissions
    from the directory. The permissions are restored to the initial
    values after the context has exited.

    Basically the same as:
    $ chmod u-rwx directory
    """

    NO_PERMISSIONS = 0x0000

    def __init__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError()
        
        self.dir_path = os.path.dirname(os.path.abspath(path))
        self.dir_mode = os.stat(self.dir_path).st_mode

    def __enter__(self):
        os.chmod(self.dir_path, self.NO_PERMISSIONS)
        return self

    def __exit__(self, exc_type, exc, tb):
        os.chmod(self.dir_path, self.dir_mode)


class Process:
    def __init__(self, stream, process):
        self.last_read = 0
        self.stream = stream
        self.process = process

    @property
    def running(self):
        proc = self.process
        #multiprocessing.Process
        if hasattr(proc, 'is_alive'):
            return proc.is_alive()
        #subprocess.Popen
        if hasattr(proc, 'poll'):
            return proc.poll() is None

    def read_output(self, *, read_all=False):
        i = self.last_read if not read_all else 0
        self.last_read = self.stream.tell()
        self.stream.seek(i)
        return self.stream.read()

    def kill(self):
        self.process.kill()
        self.stream.close()

    def terminate(self):
        self.process.terminate()
        self.stream.close()


def create_temp_dir(*, files=list(), dirs=list()) -> TemporaryDirectory:
    dir_ = TemporaryDirectory()
    dir_.populate(files, dirs)
    return dir_


def create_temp_file(**kwargs) -> TemporaryDirectory:
    return TemporaryFile(**kwargs)


def set_as_unauthorized(path: str) -> Types.Union[UnauthorizedFile, UnauthorizedDirectory]:
    if os.path.isfile(path):
        return UnauthorizedFile(path)
    return UnauthorizedDirectory(path)


def start_smtp_server(*,
    port: int,
    wait = True,
    localhost: str = 'localhost',
    ) -> Process:

    def wait_for_server_init(host: tuple):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
            while True:
                try:
                    soc.connect(host)
                
                except OSError:
                    time.sleep(0.1)
                    continue
                
                else:
                    soc.close()
                    break

    if not sys.executable:
        raise RuntimeError('Can\'t find the Python executable (sys.exectuable is None or "")')
    
    host_str = ':'.join([localhost, str(port)])
    cmd = [sys.executable, '-u', '-m', 'smtpd', '-c', 'DebuggingServer', '-n', host_str]
    
    stream = tempfile.TemporaryFile(mode='w+')
    proc = subp.Popen(cmd, stdout=stream)

    if wait:
        wait_for_server_init((localhost, port))
    return Process(stream, proc)

