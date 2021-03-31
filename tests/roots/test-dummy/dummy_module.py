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

    # def method_with_one_defargs(self, x):
    #     """
    #     Method docstring.

    #     """

    #     pass
