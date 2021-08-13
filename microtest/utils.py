"""
Utility classes and functions for testing.

Author: Valtteri Rajalainen
"""

class Namespace:
    def __init__(self, items=dict()):
        object.__setattr__(self, 'items', items)

    def __getattribute__(self, attr):
        items = object.__getattribute__(self, 'items')
        if attr not in self:
            raise AttributeError(f'No memeber "{attr}" in namespace')
        return items[attr]

    def __setattr__(self, attr, value):
        object.__getattribute__(self, 'items').__setitem__(attr, value)

    def __contains__(self, item):
        items = object.__getattribute__(self, 'items')
        return item in items.keys()