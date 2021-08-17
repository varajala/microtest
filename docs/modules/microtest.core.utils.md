## microtest.core.utils

```python


def capture_exception(func: Types.Function) -> Types.Function:
  pass

def generate_signature(obj: object) -> list:
  pass

def check_logger_object(obj: object):
  pass

def filter_tests(module: Module, included_groups: set, excluded_groups: set) -> Types.Iterable:
  """
  Filter tests inside a given module based on their groups.
  
  If included_groups is not empty, only tests with those groups are returned,
  even if their group is in exclude_groups.
  
  If included_group is empty, the excluded_group is checked for filters.
  
  If the module has a fixture, the tests are passed to the fixture and
  the fixture instance is returned.
  """

def filter_modules(modules: tuple, included_modules: set, excluded_modules: set) -> tuple:
  """
  Filter the executed modules based on inlcuded_modules and exclude_modules.
  
  These sets can contain restrictions as strings representing filepaths or parts of filepaths.
  If the restriction is an absolute filepath the paths are comapred with '=='.
  Otherwise the comaprison will be 'restriction in path' (path is an absolute filepath).
  
  If included_modules is not empty only those modules will be executed,
  even if exclude_modules is not empty.
  
  If exclude_modules is not empty these modules will be filtered out.
  """

```
