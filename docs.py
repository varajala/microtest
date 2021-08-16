import inspect
import io
import os

import microtest
import microtest.api
import microtest.core
import microtest.objects
import microtest.assertion
import microtest.logging
import microtest.scanner
import microtest.utils


INDENT = '  '

modules = (
    microtest,
    microtest.api,
    microtest.core,
    microtest.objects,
    microtest.assertion,
    microtest.logging,
    microtest.scanner,
    microtest.utils,
)


def generate_filepath(module_name: str) -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, 'docs')
    path = os.path.join(path, 'modules')
    path = os.path.join(path, module_name + '.md')
    return path


def generate_docs(module: object, *, markdown=True, path=None):
    stream = io.StringIO() if path is None else open(path, 'w+')
    if markdown:
        stream.write('## ')
    
    stream.write(module.__name__)
    stream.write('\n')

    if markdown:
        stream.write('```python\n')
    
    for obj in (value for attr, value in vars(module).items() if not attr.startswith('_')):
        if inspect.isclass(obj) and obj.__module__ == module.__name__:
            stream.write(generate_class_docs(obj))

        elif inspect.isfunction(obj) and obj.__module__ == module.__name__:
            stream.write(generate_func_docs(obj))

    if markdown:
        stream.write('```\n')

    stream.seek(0)
    data = stream.read()
    stream.close()
    return data


def generate_func_docs(func):
    source_lines, _ = inspect.getsourcelines(func)
    index = 0
    for line in source_lines:
        index += 1
        if line.strip().startswith('def '):
            break
    
    function_def = '\n'.join(( line.strip() for line in source_lines[0:index]))
    
    docs = inspect.getdoc(func)
    if docs:
        parts = [ INDENT + line for line in docs.splitlines(True) ]
        parts.insert(0, f'\n{INDENT}"""\n')
        parts.insert(0, function_def)
        parts.append(f'\n{INDENT}"""\n\n')
        return ''.join(parts)
    return function_def + f'\n{INDENT}pass\n\n\n'
        


def generate_class_docs(class_):
    parts = list()
    parts.append('class ' + class_.__name__ + ':\n')

    docs = inspect.getdoc(class_)
    if docs:
        parts.append(f'{INDENT}"""\n')
        for line in docs.splitlines(True):
            parts.append(f'{INDENT}{line}\n')
        parts.append(f'{INDENT}"""\n\n')

    for obj in (value for attr, value in vars(class_).items() if attr != '__init__'):
        if inspect.ismethod(obj) or inspect.isfunction(obj):
            parts.extend([INDENT + line for line in generate_func_docs(obj).splitlines(True)])
    
    return ''.join(parts)


if __name__ == '__main__':
    for module in modules:
        generate_docs(module, path=generate_filepath(module.__name__))
