## microtest.assertion

```python
"""
Functions for resolving runtime variable values in AssertionError tracebacks.

Author: Valtteri Rajalainen
"""

OPERATORS: ['is', 'not', 'and', 'or', 'if', 'else', '==', '!=', '>', '<', '>=', '<=']


def extract_data_from_bottom_tb(traceback: Types.Traceback):
  """
  Find the 'root' stack frame of the traceback and return its
  globals, locals and the original linenumber where exception was raised. 
  """

def separate_assertion_context(assertion_line: str, exc_message: str) -> Types.Tuple[str, Types.Union[str, None]]:
  """
  For the given assertion line and exception message, exctract
  the assertion 'context'. Returns the raw assertion expression and the context in a tuple.
  
  Example:
  
      "assert x == 10, ("X is not 10!", x)" -> ('assert x == 10', '("X is not 10", x)')
      "assert x == 10" -> ('assert x == 10', None)
  """

def escape_strings(assertion: str) -> Types.Tuple[str, Types.Function]:
  """
  Escape all possible strings for correct operator splitting.
  
  Returns the line with escaped values and a function for reversing this process.
  Note that the reverse function takes the list of splitted expressions as input.
  """

def escape_comprehensions(assertion: str) -> Types.Tuple[str, Types.Function]:
  """
  Escape all possible list/dict/generator comprehension expressions
  for correct operator splitting.
  
  Returns the line with escaped values and a function for reversing this process.
  Note that the reverse function takes the list of splitted expressions as input.
  """

def separate_operators_and_expressions(assertion: str) -> Types.Tuple[Types.List[str], Types.List[str]]:
  """
  Split the expressions from the assertion line.
  Returns a tuple of two lists: (OPERATORS, expressions).
  Experssion can be an empty string.
  
  
  Examples:
  
      'assert x == 10' -> (['=='], ['x', '10'])
      
      'assert x == 10 and y < 2' -> (['==', '<'], ['x', '10', 'y', '2'])
      
      'assert x is not None' -> (['is', 'not'], ['x', '', 'None'])
  """

def resolve_assertion_error(exc_type: Types.Class, exception: Exception, tb: Types.Traceback) -> str:
  """
  Resolve the identifier values for a given AssertionError in the error message.
  """

```

