# -*- coding: utf-8 -*-
"""
Decorators.
"""
from importlib import import_module

from presence_analyzer.main import app


def import_class(name):
    """
    Funtion return class from module (on based string path).
    """
    components = name.split('.')
    module = import_module('.'.join(components[:-1]))
    return getattr(module, components[-1])


cache_backend = import_class(app.config['CACHE_BACKEND'])()
default_timeout = app.config.get('CACHE_BACKEND_TIMEOUT', 600)
