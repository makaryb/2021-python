""" task_repeater

use @verbose
use @verbose_context()
use @repeater(count=n)
"""

import functools


def verbose(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        print("before function call")
        outcome = function(*args, **kwargs)
        print("after function call")
        return outcome

    return wrapper


class verbose_context:
    """ ContextVerbose sample """
    def __init__(self,):
        pass

    def __enter__(self):
        pass

    def __exit__(self, *args, **kwds):
        pass

    def __call__(self, func):
        @functools.wraps(func)
        def decorated(*args, **kwds):
            with self:
                print("class: before function call")
                outcome = func(*args, **kwds)
                print("class: after function call")
                return outcome

        return decorated


def repeater(count: int):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(count):
                val = func(*args, **kwargs)
            return val
        return wrapper
    return decorator
