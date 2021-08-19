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
import multiprocessing as mp
import wsgiref.simple_server
import time
import socket

from microtest.objects import Types


class Namespace:
    """
    A thin wrapper around Python dictionaries.
    Provides access to the dict with __getattr__ and __setatttr__.

    ns = Namespace({'foo': 'bar'})
    print(ns.foo)
    >>> 'bar'

    ns.foo = 'not bar...'
    print(ns.foo)
    >>> 'not bar...'

    ns.spam = 1
    print(ns.spam)
    >>> 1
    """
    
    def __init__(self, items=dict()):
        object.__setattr__(self, 'items', items)

    def __getattribute__(self, attr):
        if attr not in self:
            raise AttributeError(f'No memeber "{attr}" in namespace')
        items = object.__getattribute__(self, 'items')
        return items[attr]

    def __setattr__(self, attr, value):
        object.__getattribute__(self, 'items').__setitem__(attr, value)

    def __contains__(self, item):
        items = object.__getattribute__(self, 'items')
        return item in items.keys()


class TemporaryDirectory(tempfile.TemporaryDirectory):
    """
    A subclass of tempfile.TemporaryDirectory.
    Adds easy population with files and directories
    and clearing all contents without removing the
    directory.
    """
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
    """
    A wrapper object that holds refrences to a process object and
    a text stream where the process's output is directed.

    The wrapper process object can be an instance of subprocess.Popen 
    or multiprocessing.Process.
    """
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
        """
        Read the output that the wrapped process has produced since
        last read. If read_all is set to True, all output that the
        process has ever produced will be read.
        """
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
    """
    Create a TemporaryDirectory instance and populate it with
    the provided files and directories.
    """
    dir_ = TemporaryDirectory()
    dir_.populate(files, dirs)
    return dir_


def set_as_unauthorized(path: str) -> Types.Union[UnauthorizedFile, UnauthorizedDirectory]:
    """
    Return a context manager for temporarily restricting access to the path.
    Rights are restored after the context has exited.

    For files the restriction is basically the same as:
    $ chmod u-rw directory
    $ chmod u-rwx file

    For directories the restriction is basically the same as:
    $ chmod u-rwx directory
    """
    if os.path.isfile(path):
        return UnauthorizedFile(path)
    return UnauthorizedDirectory(path)


def _wait_for_server_init(host: tuple):
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


def start_smtp_server(*, port: int, wait = True, host: str = 'localhost') -> Process:
    """
    Start a debug SMTP server on host:port.
    If wait is True, this call blocks until a connection can be established with the server.

    Uses the builtin smtd.DebuggingServer.
    """
    if not sys.executable:
        raise RuntimeError('Can\'t find the Python executable (sys.exectuable is None or "")')
    
    host_str = ':'.join([host, str(port)])
    cmd = [sys.executable, '-u', '-m', 'smtpd', '-c', 'DebuggingServer', '-n', host_str]
    
    stream = tempfile.TemporaryFile(mode='w+')
    proc = subp.Popen(cmd, stdout=stream, stderr=stream)

    if wait:
        _wait_for_server_init((host, port))
    return Process(stream, proc)


def start_wsgi_server(wsgi_app: object, *, port: int, host = 'localhost', wait = True) -> Process:
    """
    Start a debug web server that serves the WSGI application wsgi_app.
    The provided wsgi_app object must be a valid WSGI application specified by PEP 3333.
    If wait is True, this call blocks until a connection can be established with the server.

    Uses the builtin wsgiref.simple_server.
    """
    def run_server(host, port, wsgi_app, stream):
        sys.stdout = sys.stderr = stream
        with wsgiref.simple_server.make_server(host, port, wsgi_app) as server:
            server.serve_forever()


    stream = tempfile.TemporaryFile(mode='w+')
    proc = mp.Process(target=run_server, args=(host, port, wsgi_app, stream))
    proc.start()

    if wait:
        _wait_for_server_init((host, port))
    return Process(stream, proc)

