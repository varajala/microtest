"""
Functions for resolving statement values in AssertionErrors.

Author: Valtteri Rajalainen
Edited: 23.6.2021
"""

import re
import io
import traceback


operators = [
    'is', 'not', 'and', 'or', 'if', 'else',
    '==', '!=', '>', '<', '>=', '<=',
    ]


call = re.compile(r'\w+\(.*\)')
identifier = re.compile(r'\w+')


def split_expressions(assertion):
    str_escapes = dict()
    str_escape_token = ':string:'
    index = 0
    
    string_re = re.compile(r"""("[^"]*")|'[^']*'""")
    matches = re.finditer(string_re, assertion)
    for match in matches:
        str_escapes[index] = match.group()
        index += 1
    
    line, _ = re.subn(string_re, str_escape_token, assertion)

    operator_exp = re.compile('|'.join([ f'(?<!\\w){op}(?=\\s)' for op in operators ]))
    ops = re.findall(operator_exp, line)
    
    expressions = list()
    index = 0
    parts = re.split(operator_exp, line)
    for part in parts:
        escapes = re.finditer(str_escape_token, part)
        for escape in escapes:
            part = part.replace(str_escape_token, str_escapes[index], 1)
            index += 1
        expressions.append(part.strip())
    return ops, expressions


def parse_assertion_line(assertion_line, exc_message):
    exc_context_exp = re.compile(r'(?<=AssertionError: )[^\n]+')
    match = re.search(exc_context_exp, exc_message)
    context = None
    if match:
        context = match.group()
        assertion_line = assertion_line.replace(match.group(), ':context:').strip()
        assertion_line = assertion_line.replace(", ':context:'", '').strip()
        assertion_line = assertion_line.replace(', :context:', '').strip()
    return assertion_line, context


def extract_data_from_bottom_tb(traceback):
    bottom_tb = traceback
    while bottom_tb.tb_next is not None:
        bottom_tb = bottom_tb.tb_next

    globals_ = bottom_tb.tb_frame.f_globals 
    locals_ = bottom_tb.tb_frame.f_locals
    return globals_, locals_, bottom_tb.tb_lineno


def resolve_assertion_error(exc_type, exception, tb):
    tb_lines = traceback.format_exception(exc_type, exception, tb)
    tb_text = ''.join(tb_lines)

    globals_, locals_, lineno = extract_data_from_bottom_tb(tb)

    assert_exp = re.compile(r'(?<=assert )[^\n]+')
    match = re.search(assert_exp, tb_text)
    if match is None:
        return f'\nAssertionError on line {lineno}.\n\n'

    assertion_line = match.group()
    assertion, context = parse_assertion_line(assertion_line, tb_text)
    ops, expressions = split_expressions(assertion)
    
    values = [ eval(expression, globals_, locals_) if expression else ':blank:' for expression in expressions]
    
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