import inspect
import io
import os
import sys
import importlib
from types import ModuleType


INDENT = '  '


def generate_filepath(module_name: str) -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, 'docs')
    path = os.path.join(path, 'modules')
    path = os.path.join(path, module_name + '.md')
    return path


def find_modules(pkg_root_path: str) -> tuple:
    if '__init__.py' not in { entry.name for entry in os.scandir(pkg_root_path) }:
        info = 'This path can\'t be a package root directory, it doesn\'t contain "__init__.py" file...'
        raise ValueError(info)
    
    def create_module_name(pkg_name: str, path: str) -> str:
        name, _ = os.path.splitext(os.path.basename(path))
        return pkg_name + '.' + name if name != '__init__' else pkg_name

    def create_pkg_name(parent_pkg: str, path: str) -> str:
        return parent_pkg + '.' + os.path.basename(path)

    def handle_pkg(path: str, pkg_name: str, modules: list):
        for entry in os.scandir(path):
            if entry.is_dir() and '__init__.py' in { entry.name for entry in os.scandir(entry.path) }:
                handle_pkg(entry.path, create_pkg_name(pkg_name, entry.path), modules)
            
            elif entry.path.endswith('__main__.py'):
                continue

            elif entry.path.endswith('.py'):
                path = os.path.abspath(entry.path)
                modules.append((create_module_name(pkg_name, path), path))

    modules = list()
    handle_pkg(pkg_root_path, os.path.basename(pkg_root_path), modules)
    return tuple(modules)


def generate_module_docs(module: object, *, markdown=True, path=None):
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



def generate_docs(pkg_root_path: str):
    for name, path in find_modules(pkg_root_path):
        importlib.import_module(name)
        module = sys.modules[name]
        generate_module_docs(module, path=generate_filepath(module.__name__))


if __name__ == '__main__':
    generate_docs('/home/varajala/dev/py/microtest/microtest')