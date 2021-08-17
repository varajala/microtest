"""
Utility functions for microtest.core that don't require any state.

Author: Valtteri Rajalainen
"""

import os
import functools
import inspect


from microtest.objects import Module, Types


def capture_exception(func: Types.Function) -> Types.Function:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        error = None
        try:
            func(*args, **kwargs)
        except Exception as exc:
            error = exc
        return error
    return wrapper


def generate_signature(obj: object) -> list:
    """
    Generate a list of argument names from the function signature.

    The provided object must be a function method or a wrapper object
    with the actual function object available as obj.func attribute.
    
    TypeError is raised if these restrictions aren\'t met.
    """
    func_obj = None
    if inspect.isfunction(obj) or inspect.ismethod(obj):
        func_obj = obj

    if hasattr(obj, 'func'):
        func_obj = obj.func

    if func_obj is None:
        info = '\n'.join([
            'Failed to create a function signature.',
            'The provided object must be a function, method',
            'or some wrapper object with the actual',
            'function object available as object.func attribute...',
            ])
        raise TypeError(info)
    
    signature = inspect.signature(func_obj)
    return [ param for param in signature.parameters ]


def check_logger_object(obj: object):
    logger_interface = (
        ('log_start_info', list()),
        ('log_module_info', ['module_path']),
        ('log_test_info', ['name', 'result', 'exc']),
        ('log_module_exec_error', ['module_path', 'exc_type', 'exc', 'tb']),
        ('log_results', ['tests', 'failed', 'errors', 'time']),
        ('terminate', list())
    )
    
    if obj is None:
        raise TypeError('No logger object set')

    for requirement in logger_interface:
        method_name, signature = requirement
        if not hasattr(obj, method_name):
            info = f'Invalid Logger implementation: Expected Logger to have attribute "{method_name}"'
            raise TypeError(info)
        
        method_obj = getattr(obj, method_name)
        if not hasattr(method_obj, '__call__'):
            info = f'Invalid Logger implementation: Attribute "{method_name}" is not callable'
            raise TypeError(info)
        
        method_obj_signature = generate_signature(method_obj)
        if method_obj_signature != signature:
            info = ''.join([
                'Invalid Logger implementation: ',
                f'Signature of "{method_name}" doesn\'t match the interface requirement.\n\n',
                f'{method_obj_signature} != {signature}'
                ])
            raise TypeError(info)
    

def filter_tests(module: Module, included_groups: set, excluded_groups: set) -> Types.Iterable:
    """
    Filter tests inside a given module based on their groups.

    If included_groups is not empty, only tests with those groups are returned,
    even if their group is in exclude_groups.

    If included_group is empty, the excluded_group is checked for filters.

    If the module has a fixture, the tests are passed to the fixture and
    the fixture instance is returned.
    """
    tests = module.tests.copy()
    if included_groups:
        tests = list(filter(lambda test: test.group in included_groups, module.tests))
    
    elif excluded_groups:
        tests = list(filter(lambda test: test.group not in excluded_groups, module.tests))

    if module.fixture:
        module.fixture.tests = tests
        return module.fixture
    return tests


def filter_modules(modules: tuple, included_modules: set, excluded_modules: set) -> tuple:
    """
    Filter the executed modules based on inlcuded_modules and exclude_modules.

    These sets can contain restrictions as strings representing filepaths or parts of filepaths.
    If the restriction is an absolute filepath the paths are comapred with '=='.
    Otherwise the comaprison will be 'restriction in path' (path is an absolute filepath).

    If included_modules is not empty only those modules will be executed,
    even if exclude_modules is not empty.
    
    If exclude_modules is not empty these modules will be filtered out.
    """
    def path_meets_restriction(module_path: str, restriction: str) -> bool:
        if os.path.isabs(restriction):
            return module_path == restriction
        return restriction in module_path

    if included_modules:
        filtered_modules = list()
        for restriction in included_modules:
            for module_path in modules:
                if path_meets_restriction(module_path, restriction):
                    filtered_modules.append(module_path)
        return tuple(filtered_modules)
    
    filtered_modules = list(modules)
    
    for restriction in excluded_modules:
        removed = 0
        for index, module_path in enumerate(modules):
            if path_meets_restriction(module_path, restriction):
                filtered_modules.pop(index - removed)
                removed += 1
    
    return tuple(filtered_modules)