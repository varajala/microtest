## microtest
```python
def set_logger(obj: object):
  pass


def set_module_discovery_regex(regex: str):
  pass


def run_from_commandline(args: list):
  """
  The args is excpeted to be a list of command line arguments in the format:
  
      sys.argv[1:]
  
  The most important argument is the tested file/directory path.
  This is expected to be the last argument. If not provided os.getcwd() is used.
  """

```
