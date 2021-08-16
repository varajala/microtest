## microtest.scanner
```python
def find_tests(root_path: str) -> tuple:
  """
  Do a BFS over the directory structure and add all
  filepaths that sadisfy the is_test_module check.
  """

def scan_directory_safely(path: str) -> Iterable:
  """
  Safely scan a directory.
  Returns an empty iterator if any errors
  occur while scanning the directory.
  """

def is_test_module(filename: str):
  pass


```
