"""
Find all Python modules inside a package structure and generate
simple docs from these modules.

Author: Valtteri Rajalainen
"""

import inspect
import io
import os
import sys
import importlib
from types import ModuleType


INDENT = '  '


def find_modules(pkg_root_path: str) -> tuple:
    """
    Recursively find all sub packages and modules.
    Raises ValueError if the provided directory path
    doesn\'t include a file called "__init__.py".

    Discards files called "__main__.py".
    """
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
    stream.write('\n\n')

    if markdown:
        stream.write('```python\n')
    
    def is_member(obj):
        return obj.__module__ == module.__name__

    def is_not_local_function(obj):
        return 'locals' not in repr(obj)

    def filter_classes(dict_):
        classes = list()
        for key, obj in dict_.copy().items():
            if inspect.isclass(obj) and is_member(obj):
                classes.append(dict_.pop(key))
        return tuple(classes)

    def filter_functions(dict_):
        functions = list()
        for key, obj in dict_.copy().items():
            if inspect.isfunction(obj) and is_member(obj) and is_not_local_function(obj):
                functions.append(dict_.pop(key))
        return tuple(functions)

    module_items = { attr: value for attr, value in vars(module).items() if not attr.startswith('_') }
    classes = filter_classes(module_items)
    functions = filter_functions(module_items)

    for name, value in module_items.items():
        generate_member_docs(name, value, stream)
    stream.write('\n\n')

    for class_ in classes:
        generate_class_docs(class_, stream)

    for func in functions:
        generate_func_docs(func, stream)


    if markdown:
        stream.write('```\n\n')

    stream.seek(0)
    data = stream.read()
    stream.close()
    return data


def generate_member_docs(name: str, value: object, stream, *, indent = 0):
    type_checks = (
        inspect.ismodule(value),
        inspect.isfunction(value),
        inspect.isclass(value)
        )

    containers = { dict, list, set, tuple }
    builtins = { str, float, int, bytes, bool }

    if not any(type_checks):
        stream.write(indent * INDENT)
        stream.write(name)
        stream.write(': ')
        
        if value.__class__ in builtins:
            stream.write(repr(value))

        elif value is None:
            stream.write('None')

        elif value.__class__ in containers:
            stream.write(repr(value) if value else value.__class__.__name__)

        else:
            stream.write('object')
        
        stream.write('\n')
    

def generate_func_docs(func, stream, *, indent = 0):
    source_lines, _ = inspect.getsourcelines(func)
    index = 0
    for line in source_lines:
        index += 1
        if line.strip().startswith('def '):
            break
    
    for line in source_lines[0:index]:
        stream.write(indent * INDENT)
        stream.write(line.strip())
        stream.write('\n')
    
    docs = inspect.getdoc(func)
    if docs:
        stream.write((indent + 1)* INDENT)
        stream.write('"""\n')
        for line in docs.splitlines(True):
            stream.write((indent + 1)* INDENT)
            stream.write(line)
        stream.write('\n')
        stream.write((indent + 1)* INDENT)
        stream.write('"""\n\n')
        return
    
    stream.write((indent + 1)* INDENT)
    stream.write('pass\n\n')
        

def generate_class_docs(class_, stream):
    stream.write('class ')
    stream.write(class_.__name__)
    stream.write(':\n')

    start_pos = stream.tell()

    docs = inspect.getdoc(class_)
    if docs:
        stream.write(INDENT)
        stream.write('"""\n')
        for line in docs.splitlines(True):
            stream.write(INDENT)
            stream.write(line)
        stream.write('\n')
        stream.write(INDENT)
        stream.write('"""\n')

    def is_documented_method(obj):
        is_method =  inspect.ismethod(obj) or inspect.isfunction(obj)
        return is_method and obj.__name__ != '__init__'

    class_items = vars(class_).items()
    methods = tuple((obj for _, obj in class_items if is_documented_method(obj)))
    members = { name: value for name, value in class_items if value not in set(methods) and not name.startswith('_') }

    for name, value in members.items():
        generate_member_docs(name, value, stream, indent = 1)

    if len(members) > 0:
        stream.write('\n')

    for method in methods:
        generate_func_docs(method, stream, indent = 1)

    pos = stream.tell()
    if pos == start_pos:
        stream.write(INDENT)
        stream.write('pass\n\n')


def generate_docs(pkg_root_path: str, docs_directory: str, *, markdown=True):
    """
    Generate documentation files from modules inside the given package.
    Doc files will be named after the found modules and '.md' suffix
    will be added if the markdown flag is set.

    Both filepaths should be absolute.
    """
    def generate_doc_filepath(module_name: str) -> str:
        path = os.path.join(docs_directory, module_name)
        if markdown:
            path += '.md'
        return path

    for name, path in find_modules(pkg_root_path):
        importlib.import_module(name)
        module = sys.modules[name]
        generate_module_docs(module, markdown=markdown, path=generate_doc_filepath(name))
