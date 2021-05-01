import functools
import sys
import textwrap


def func(x=None, y=None):
    """
    Example docstring.

    :param x: The default value ``None`` will be added here.
    :param y: The text of default value is unchanged.
              (Default: ``'Default Value'``)
    """

    if y is None:
        y = 'Default Value'

    ...


class TestClassWithReturn:
    """
    Class docstring.
    """

    def __init__(self, x=None):
        pass

    # a should be param
    def method_with_last_defargs(self, x, y, a=0, **kw):
        r"""
        Method docstring.

        :return: 0
        :param x: foo
        :param y: bar
        :keyword \*\*kw: null
        """
        return 0

    def method_with_mid_defargs(self, x, a=0, y=''):
        """
        Method docstring.

        :return: 0
        :param x: foo
        :type x: int, str
        :type y: str
        :parameter y: bar (Default: empty)
        """
        return 0


class TestClassWithArgs:
    """
    Class docstring.
    """

    def method_with_args(self, a, x=0, *args):
        r"""
        Method docstring.

        :param a: foo
        :param \*args: bar
        """
        pass

    def method_with_args_asterisk_not_escaped(self, a, x=0, *args):
        r"""
        Method docstring.

        :arg a: foo
        :arg *args: bar
        """
        pass

    def method_with_args_no_asterisk(self, a, x=0, *args):
        r"""
        Method docstring.

        :argument a: foo
        :argument args: bar
        """
        pass

    # param
    def method_with_kwargs_as_kw_x_forced_param(self, a, *, x=0, **kwargs):
        r"""
        Method docstring.

        :param a: foo
        :param \*\*kwargs: bar
        """
        pass

    # keyword
    def method_with_kwargs_as_kw_x_kw(self, *, a, x=0, **kwargs):
        r"""
        Method docstring.

        :keyword a: foo
        :keyword \*\*kwargs: bar
        """
        pass

    # param
    exec(textwrap.dedent("""\
    def method_with_kwargs_as_kw_x_param(self, x=0, {}**kwargs):
        {}
        pass""".format(
        '' if sys.version_info[:2] < (3, 8) else '/, ', repr(r"""
            Method docstring.

            :keyword \*\*kwargs: foo
            """))))

    # param
    def method_with_kwargs_as_param(self, a, x=0, **kwargs):
        r"""
        Method docstring.

        :param a: foo
        :param \*\*kwargs: bar
        """
        pass

    def method_with_last_kw_optional(self, *args, x=0):
        r"""
        Method docstring.

        :return: 0
        :param \*args: foo
        :raises ValueError: If ``x`` is nonzero.
        """
        if x != 0:
            raise ValueError
        return x


class __TestClassWithDefaultArgsOnSelf:
    """
    Class docstring.
    """

    def __init__(_self_=None):
        """Method docstring."""
        pass

    def __new__(_self_=None):
        """Method docstring."""
        pass

    @staticmethod
    def _staticmethod(self=None, other=''):
        """Method docstring."""
        pass

    @classmethod
    def _classmethod_(_cls_=None):
        """Method docstring."""
        pass

    def _method(self=None, other=0, arg3=''):
        """Method docstring."""
        pass

    @property
    def __property_(self=None):
        """Method docstring."""
        pass

    _staticmethod_ = _staticmethod
    __classmethod_ = _classmethod_
    __method = functools.partialmethod(_method, None)


__partial_func_of_method = functools.partial(
    __TestClassWithDefaultArgsOnSelf._TestClassWithDefaultArgsOnSelf__method,
    arg3=None)


__partial_func_of_static_method = functools.partial(
    __TestClassWithDefaultArgsOnSelf._staticmethod_,
    other=__TestClassWithDefaultArgsOnSelf.
    _TestClassWithDefaultArgsOnSelf__property_)
