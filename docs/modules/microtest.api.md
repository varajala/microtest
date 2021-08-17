## microtest.api

```python


class Patch:
  """
  Dynamically replace an attributes from the given object.
  Use as a context manager.
  """
  def __enter__(self):
    pass

  def __exit__(self, exc_type: Types.Class, exc: Exception, tb: Types.Traceback):
    pass

def test(func: Types.Function) -> core.TestObject:
  pass

def setup(func: Types.Function) -> Types.Function:
  pass

def reset(func: Types.Function) -> Types.Function:
  pass

def cleanup(func: Types.Function) -> Types.Function:
  pass

def raises(callable: Types.Callable, params: Types.Union[tuple, dict], exc_type: Types.Class) -> bool:
  """
  Return True if provided callable raises an exception of type exc_type with
  the given arguments. All other exception types will be raised normally.
  
  Params must be a tuple or a dict. If a dict object is given, they are
  passed as keyword arguments.
  """

def patch(obj: object, **kwargs) -> Patch:
  pass

def resource(func: Types.Function):
  pass

def utility(obj: object, *, name: str = None):
  """
  Mark the wrapped object as a utility.
  These are injected into the module namespace
  during test execution.
  """

def add_resource(name: str, obj: object):
  pass

def on_exit(func: Types.Function):
  pass

def call(func: Types.Function) -> Types.Function:
  """
  Call the function during module exection if microtest is running
  or doing configuration.
  """

def group(name: str) -> Types.Function:
  pass

def exclude_groups(*args):
  pass

def only_groups(*args):
  pass

def exclude_modules(*args):
  pass

def only_modules(*args):
  pass

def run():
  pass

```

