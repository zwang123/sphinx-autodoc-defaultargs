import sys


class MyIterable(object):
    """My Iterable class."""

    Type = tuple

    def __init__(self, *args, **kwargs):
        self.contents = self.Type(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self.contents.__iter__(*args, **kwargs)

    def __eq__(self, other):
        return isinstance(
            other, type(self)) and self.contents == other.contents

    def __add__(self, other):
        try:
            other = other.contents
        except AttributeError:
            pass
        return self.__class__(self.contents + self.Type(other))


class MyCallable(object):
    """My Callable class."""

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    # must keep the same type
    def __eq__(self, other):
        return isinstance(other, type(self)) and self.func == other.func


class __MyFunctor(object):
    exec('def __call__(self=None, x=None, {}y_=0): pass'.format(
        '' if sys.version_info[:2] < (3, 8) else '/, '))

    def __eq__(self, other):
        try:
            return isinstance(other, self.__class__)
        except Exception:
            return False

    def __method(self=None):
        pass

    @classmethod
    def _classmethod_(cls=r'_\\'):
        pass

    @staticmethod
    def _staticmethod(x=0):
        pass
    __staticmethod = _staticmethod
    _classmethod = _classmethod_
