def func(x=None, y=None):
    """
    Example docstring.

    :param x: The default value ``None`` will be added here.
    :param y: The text of default value is unchanged.
              (Default: ``'Default Value'``)
    """

    if y is None:
        y = 'Default Value'
    pass


class TestClass:
    """
    Class docstring.
    """

    def __init__(self, x=None):
        pass

    def method_with_last_defargs(self, x, y, a=0, **kw):
        """
        Method docstring.

        :return: 0
        :param x: foo
        :param y: bar
        :keyword kw: null
        """

        return 0

    def method_with_mid_defargs(self, x, a=0, y=''):
        """
        Method docstring.

        :return: 0
        :param x: foo
        :type x: int, str
        :type y: str
        :param y: bar (Default: empty)
        """

        return 0
