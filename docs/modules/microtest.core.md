## microtest.core
```python
def require_init(func: Types.Function) -> Types.Function:
  """
  Wrapper function to ensure proper initialization before execution.
  """

def initialize():
  pass


def stop_testing(*args):
  pass


def collect_test(test_obj: _TestObject):
  pass


def get_fixture() -> _Fixture:
  pass


def call_with_resources(func: Types.Function) -> Types.Any:
  """
  Call the given function with the resources named in
  function arguments.
  
  Note that functools.wraps should be used when wrapping microtest.core._TestObjects,
  otherwise the wrapper function's signature must match with the original
  test function's signature.
  """

def add_resource(name: str, obj: object):
  pass


def add_utility(name: str, obj: object):
  pass


def on_exit(func: Types.Function):
  pass


def wrapper(*args, **kwargs):
  pass


def wrapper(*args, **kwargs):
  pass


def wrapper(*args, **kwargs):
  pass


def run_current_module():
  pass


def run_config(path: str, exec_name: str):
  pass


```
