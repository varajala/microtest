## microtest.core

```python
exec_context: object
resources: dict
utilities: dict
logger: object
current_module: None
running: False
config_in_process: False
errors: 0
failed: 0
tests: 0
t_start: None
t_end: None
excluded_modules: set
included_modules: set
excluded_groups: set
included_groups: set


class TestObject:
  def __getattribute__(self, attr: str):
    """
    Return getattr(self, name).
    """

  def __call__(self, *args, **kwargs):
    """
    Call self as a function.
    """

class Fixture:
  """
  Iterable container that ensures the right
  execution order for setup/reset/cleanup/test functions.
  """
  def append(self, test: TestObject):
    pass

  def register_setup(self, func: Types.Function):
    pass

  def register_cleanup(self, func: Types.Function):
    pass

  def register_reset(self, func: Types.Function):
    pass

  def __iter__(self):
    pass

  def __next__(self) -> TestObject:
    pass

  def wrap_test(self, func: Types.Function) -> Types.Function:
    pass

  def do_setup(self):
    pass

  def do_cleanup(self):
    pass

  def abort_with_error(self, error: Exception, *, do_cleanup=True):
    pass

def require_init(func: Types.Function) -> Types.Function:
  """
  Wrapper function to ensure proper initialization before execution.
  """

def initialize():
  pass

def stop_testing(*args):
  pass

def collect_test(test_obj: TestObject):
  pass

def get_fixture() -> Fixture:
  pass

def call_with_resources(func: Types.Function) -> Types.Any:
  """
  Call the given function with the resources named in
  function arguments.
  
  Note that functools.wraps should be used when wrapping microtest.core.TestObjects,
  otherwise the wrapper function's signature must match with the original
  test function's signature.
  """

def add_resource(name: str, obj: object):
  pass

def add_utility(name: str, obj: object):
  pass

def on_exit(func: Types.Function):
  pass

def run_current_module():
  pass

def run_config(path: str, exec_name: str):
  pass

```

