## microtest.docs

```python
INDENT: '  '


def find_modules(pkg_root_path: str) -> tuple:
  """
  Recursively find all sub packages and modules.
  Raises ValueError if the provided directory path
  doesn't include a file called "__init__.py".
  
  Discards files called "__main__.py".
  """

def generate_module_docs(module: object, *, markdown=True, path=None):
  pass

def generate_member_docs(name: str, value: object, stream, *, indent = 0):
  pass

def generate_func_docs(func, stream, *, indent = 0):
  pass

def generate_class_docs(class_, stream):
  pass

def generate_docs(pkg_root_path: str, docs_directory: str, *, markdown=True):
  """
  Generate documentation files from modules inside the given package.
  Doc files will be named after the found modules and '.md' suffix
  will be added if the markdown flag is set.
  
  Both filepaths should be absolute.
  """

```

