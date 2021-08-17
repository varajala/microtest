## microtest.utils

```python


class Namespace:
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
  Create and return a temporary directory.  This has the same
  behavior as mkdtemp but can be used as a context manager.  For
  example:
  
      with TemporaryDirectory() as tmpdir:
          ...
  
  Upon exiting the context, the directory and everything contained
  in it are removed.
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
  running: object
  def read_output(self, *, read_all=False):
    pass

  def kill(self):
    pass

  def terminate(self):
    pass

def create_temp_dir(*, files=list(), dirs=list()) -> TemporaryDirectory:
  pass

def set_as_unauthorized(path: str) -> Types.Union[UnauthorizedFile, UnauthorizedDirectory]:
  pass

def start_smtp_server(*, port: int, wait = True, localhost: str = 'localhost') -> Process:
  pass

```

