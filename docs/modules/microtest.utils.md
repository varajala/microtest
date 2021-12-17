## microtest.utils

```python
"""
Utility classes and functions for testing.

Author: Valtteri Rajalainen
"""

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
  def __getattribute__(self, attr):
    """
    Return getattr(self, name).
    """

  def __setattr__(self, attr, value):
    """
    Implement setattr(self, name, value).
    """

  def __contains__(self, item):
    pass

class TemporaryDirectory:
  """
  A subclass of tempfile.TemporaryDirectory.
  Adds easy population with files and directories
  and clearing all contents without removing the
  directory.
  """
  path: object

  def populate(self, files=list(), dirs=list()):
    pass

  def delete_contents(self):
    pass

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
  NO_PERMISSIONS: 0
  NO_RW_PERMISSION: 64

  def __enter__(self):
    pass

  def __exit__(self, exc_type, exc, tb):
    pass

class UnauthorizedDirectory:
  """
  Context manager that temporarily removes all user permissions
  from the directory. The permissions are restored to the initial
  values after the context has exited.
  
  Basically the same as:
  $ chmod u-rwx directory
  """
  NO_PERMISSIONS: 0

  def __enter__(self):
    pass

  def __exit__(self, exc_type, exc, tb):
    pass

class Process:
  """
  A wrapper object that holds refrences to a process object and
  a text stream where the process's output is directed.
  
  The wrapper process object can be an instance of subprocess.Popen 
  or multiprocessing.Process.
  """
  running: object

  def read_output(self, *, read_all=False):
    """
    Read the output that the wrapped process has produced since
    last read. If read_all is set to True, all output that the
    process has ever produced will be read.
    """

  def kill(self):
    pass

  def terminate(self):
    pass

def create_temp_dir(*, files=list(), dirs=list()) -> TemporaryDirectory:
  """
  Create a TemporaryDirectory instance and populate it with
  the provided files and directories.
  """

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

def start_smtp_server(*, port: int, wait = True, host: str = '127.0.0.1') -> Process:
  """
  Start a debug SMTP server on host:port.
  If wait is True, this call blocks until a connection can be established with the server.
  
  Uses the builtin smtd.DebuggingServer.
  """

def start_wsgi_server(wsgi_app: object, *, port: int, host: str = '127.0.0.1', wait = True) -> Process:
  """
  Start a debug web server that serves the WSGI application wsgi_app.
  The provided wsgi_app object must be a valid WSGI application specified by PEP 3333.
  If wait is True, this call blocks until a connection can be established with the server.
  
  Uses the builtin wsgiref.simple_server.
  """

```

