# -*- coding: utf-8 -*-
"""
Default backends.
"""
import datetime
import time
from collections import defaultdict
from threading import Lock


class BaseBackend(object):
    """
    Base backend interface help to inherit other 'real' backend such as
    redis or memcache.
    """
    def set(self, args_list, value, timeout):
        """
        Set value in cache.
        """
        raise NotImplementedError('subclasses of BaseBackend must provide an' +
                                  ' set() method')

    def get(self, args_list):
        """
        Get value from cache.
        """
        raise NotImplementedError('subclasses of BaseBackend must provide an' +
                                  ' get() method')

    def make_key(self, args):
        """
        Making key from args.
        """
        raise NotImplementedError('subclasses of BaseBackend must provide an' +
                                  ' make_key() method')


class MemoryBackend(BaseBackend):
    """
    Memory cache backend. Storing all data in local memory (RAM).
    This backend shared storege variable between threads.
    """
    def __init__(self):
        self.storage = defaultdict(dict)
        self._lock = Lock()

    def set(self, args_list, value, timeout):
        """
        Set data in cache.
        """
        key = self.make_key(args_list)

        with self._lock:
            self.storage[key] = {
                'data': value,
                'timestamp': int(time.time()),
                'timeout': timeout,
            }

    def get(self, args_list):
        """
        Get data from cache.
        """
        key = self.make_key(args_list)

        item = self.storage[key]
        if item:
            now_ts = int(time.time())
            if (now_ts - item['timestamp']) <= item['timeout']:
                return item['data']
        return None

    def make_key(self, args):
        """
        Method making key from arguments.
        """
        allow_types = (int, str, unicode)
        extra = [args[0], ]
        for x in args[1:]:
            if type(x) in allow_types:
                extra.append(str(x))
            else:
                extra.append(repr(x))
        key = '_'.join(extra)
        return key
