## microtest.logging
```python
class Colors:
class DefaultLogger:
  def write(self, text: str, *, color = None):
    pass
  
  
  def format_separator(self, char: str, separation = 1):
    pass
  
  
  def format_traceback(self, exc_type, exc, tb):
    pass
  
  
  def log_start_info(self):
    pass
  
  
  def log_test_info(self, name: str, result: str, exc: Exception):
    pass
  
  
  def log_module_exec_error(self, module_path: str, exc_type: Types.Class, exc: Exception, tb: Types.Traceback):
    pass
  
  
  def log_module_info(self, module_path: str):
    pass
  
  
  def log_results(self, tests: int, failed: int, errors: int, time: float):
    pass
  
  
  def terminate(self):
    pass
  
  
```
