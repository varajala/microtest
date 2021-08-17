## microtest.objects

```python


class Types:
  Callable: object
  Union: object
  Iterable: object
  Any: object
  Tuple: object
  List: object
  def new_type(x):
    pass

  def new_type(x):
    pass

  def new_type(x):
    pass

class Output:
  MINIMAL: 'minimal'
  VERBOSE: 'verbose'
  DEFAULT: 'default'
class Result:
  OK: 'OK'
  FAILED: 'FAILED'
  ERROR: 'ERROR'
class Module:
  pass

class ExecutionContext:
  def add_cleanup_operation(self, func, *, final=False):
    pass

  def __enter__(self):
    pass

  def __exit__(self, exc_type, exc, tb):
    pass

```

