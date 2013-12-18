# -*- coding: utf-8 -*-
"""
Decorators module.
"""
from functools import wraps, partial
from threading import Lock

from presence_analyzer.cache import cache_backend, default_timeout


def cache(func=None, timeout=default_timeout):
    """
    This decorator cache result.
    """
    lock_cache = Lock()

    if func is None:
        return partial(cache, timeout=timeout)

    @wraps(func)
    def wrapper(*args, **kwargs):
        args_list = (func.__name__,) + args + tuple(kwargs.values())
        with lock_cache:
            cache_item = cache_backend.get(args_list)
            if not cache_item:
                data = func(*args, **kwargs)
                cache_backend.set(args_list, data, timeout)
                return data
            else:
                return cache_item
    return wrapper
