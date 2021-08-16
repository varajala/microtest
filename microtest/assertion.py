"""
Functions for resolving variable values in AssertionError tracebacks.

Author: Valtteri Rajalainen
"""

import re
import io
import traceback

from typing import List, Tuple, Union, NewType


OPERATORS = [
    'is', 'not', 'and', 'or', 'if', 'else',
    '==', '!=', '>', '<', '>=', '<=',
    ]


Class = NewType('Class', object)
Traceback = NewType('Traceback', object)


def extract_data_from_bottom_tb(traceback: Traceback):
    """
    Find the 'root' stack frame of the traceback and return its
    globals, locals and the original linenumber where exception was raised. 
    """
    bottom_tb = traceback
    while bottom_tb.tb_next is not None:
        bottom_tb = bottom_tb.tb_next

    globals_ = bottom_tb.tb_frame.f_globals 
    locals_ = bottom_tb.tb_frame.f_locals
    return globals_, locals_, bottom_tb.tb_lineno


def parse_assertion_line(assertion_line: str, exc_message: str) -> Tuple[str, Union[str, None]]:
    """
    For the given assertion line and exception message, exctract
    the assertion 'context'. Returns the raw assertion expression and the context in a tuple.

    Example:

        'assert x == 10, ("X is not 10!", x)' -> ('assert x == 10', '("X is not 10", x)')
        'assert x == 10 -> ('assert x == 10', None)

    """
    exc_context_exp = re.compile(r'(?<=AssertionError: )[^\n]+')
    match = re.search(exc_context_exp, exc_message)
    context = None
    if match:
        context = match.group()
        assertion_line = assertion_line.replace(match.group(), ':context:').strip()
        assertion_line = assertion_line.replace(", ':context:'", '').strip()
        assertion_line = assertion_line.replace(', :context:', '').strip()
    return assertion_line, context


def escape_strings(assertion: str):
    escapes = dict()
    escape_token = ':string:'
    index = 0
    
    string_re = re.compile(r"""("[^"]*")|'[^']*'""")
    matches = re.finditer(string_re, assertion)
    for match in matches:
        escapes[index] = match.group()
        index += 1
    line, _ = re.subn(string_re, escape_token, assertion)

    def reverse(parts: list) -> list:
        results = list()
        index = 0
        
        for part in parts:
            for match in re.finditer(escape_token, part):
                part = part.replace(escape_token, escapes[index], 1)
                index += 1
            results.append(part.strip())
        return results
    
    return line, reverse


def escape_comprehensions(assertion: str):
    escapes = dict()
    create_escape = lambda i: f':comp{i}:'
    index = 0
    comp_re = re.compile(r'\([^()]+\)|\[[^[\]]+\]|\{[^{}]+\}')
    
    line = assertion
    match = re.search(comp_re, line)
    while match:
        escapes[index] = match.group()
        line = line.replace(match.group(), create_escape(index), 1)
        index += 1
        match = re.search(comp_re, line)

    def reverse(parts: list) -> str:
        results = list()
        comp_escape_re = re.compile(r':comp[0-9]+:')
        create_index = lambda string: int(re.search(r'[0-9]+', string).group())
        
        for part in parts:
            escape = re.search(comp_escape_re, part)
            while escape:
                escape_str = escape.group()
                index = create_index(escape_str)
                part = part.replace(escape_str, escapes[index], 1)
                escape = re.search(comp_escape_re, part)
            results.append(part.strip())
        return results

    return line, reverse


def split_expressions(assertion: str) -> Tuple[List[str], List[str]]:
    """
    Split the expressions from the assertion line.
    Returns a tuple of two lists: (OPERATORS, expressions).
    Experssion can be an empty string.


    Examples:

        'assert x == 10' -> (['=='], ['x', '10'])
        
        'assert x == 10 and y < 2' -> (['==', '<'], ['x', '10', 'y', '2'])
        
        'assert x is not None' -> (['is', 'not'], ['x', '', 'None'])
    
    """
    line, reverse_string_escape = escape_strings(assertion)
    line, reverse_comp_escape = escape_comprehensions(line)
    
    operator_exp = re.compile('|'.join([ f'(?<!\\w){op}(?=\\s)' for op in OPERATORS ]))
    ops = re.findall(operator_exp, line)
    parts = re.split(operator_exp, line)

    expressions = reverse_comp_escape(parts)
    expressions = reverse_string_escape(expressions)
    return ops, expressions


def resolve_assertion_error(exc_type: Class, exception: Exception, tb: Traceback) -> str:
    """
    Resolve the identifier values for a given AssertionError in the error message.
    """
    tb_lines = traceback.format_exception(exc_type, exception, tb)
    tb_text = ''.join(tb_lines)

    globals_, locals_, lineno = extract_data_from_bottom_tb(tb)

    #find the actual assertion line, return a generic message if not found
    assert_exp = re.compile(r'(?<=assert )[^\n]+')
    match = re.search(assert_exp, tb_text)
    if match is None:
        return f'\nAssertionError on line {lineno}.\n\n'

    #exctract the optional user provided 'context' for this assertion
    #separate the actual variable names from OPERATORS
    assertion_line = match.group()
    assertion, context = parse_assertion_line(assertion_line, tb_text)

    #print(assertion_line, ' -> ', assertion, context)
    ops, expressions = split_expressions(assertion)
    
    #evaluate the variables to their runtime values
    values = [ eval(expression, globals_, locals_) if expression else ':blank:' for expression in expressions]
    
    #write error msg with resolve values
    buffer = io.StringIO()
    buffer.write(f'\nAssertionError on line {lineno}:\n')
    buffer.write('assert ')
    while values:
        val = values.pop(0)
        if val != ':blank:':
            buffer.write(repr(val))
            buffer.write(' ')
        if ops:
            buffer.write(ops.pop(0))
            buffer.write(' ')

    if context:
        buffer.write('\n\n')
        buffer.write(context)

    buffer.write('\n\n')
    buffer.seek(0)
    resolved_assertion = buffer.read()
    buffer.close()
    return resolved_assertion
