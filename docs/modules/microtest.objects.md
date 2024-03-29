## microtest.objects

```python
"""
Common objects used across different modules.

Author: Valtteri Rajalainen
"""

class Types:
  Function: object
  Class: object
  Traceback: object
  Callable: object
  Union: object
  Iterable: object
  Any: object
  Tuple: object
  List: object

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

