import itertools
import pathlib
import re
import sys
import textwrap

import pytest
from myclasses import MyCallable, MyIterable
from myclasses import __MyFunctor as MyFunctor

from sphinx_autodoc_defaultargs import (
    get_args, match_field, rfind_substring_in_paragraph, rstrip_min)


@pytest.mark.parametrize('encoding', ['utf-8'])
@pytest.mark.parametrize('args, result', [
    ([':param x:'],
        [True, 0, 1, ':param x:', '']),
    ([MyIterable((':param y:', ':parameter y:'))],
        [True, 1, 3, ':parameter y:', 'foo\nine']),
    ([':arg a:'],
        [True, 3, 4, ':arg a:', 'bar']),
    ([MyIterable((':argument b:', ':arg b:'))],
        [True, 5, 7, ':argument b:', '\n']),
    ([MyIterable((':argument b:', ':arg b:')), True],
        [True, 5, 8, ':argument b:', '\n\n']),
    ([MyIterable((':argument z:', ':arg z:'))],
        [False, 10, 10] + [None] * 2),
    ([':rtype:'],
        [True, 8, 9, ':rtype:', 'int']),
])
def test_match_field(encoding, args, result):
    lines = MyIterable(textwrap.dedent('''\
    :param x:
    :parameter y: foo
                 line
    :arg a: bar
    .. {blank}
    :argument b:
    {blank}

    :rtype: int
    ''').format(blank=' \t\v').split('\n'))

    if result[0]:
        result[-1] = result[-1].split('\n')

    assert match_field(lines, *args) == tuple(result)

    args0 = args[0]

    try:
        args[0] = re.compile(args[0])
        assert match_field(lines, *args) == tuple(result)
    except TypeError:
        pass

    if result[0]:
        result[3] = result[3].encode(encoding)
        result[4] = [r.encode(encoding) for r in result[4]]
    lines = MyIterable(line.encode(encoding) for line in lines)

    try:
        args[0] = args0.encode(encoding)
        assert match_field(lines, *args) == tuple(result)
    except AttributeError:
        args[0] = MyIterable(x.encode(encoding) for x in args0)
        assert match_field(lines, *args) == tuple(result)


# The length of 'utf-16' bytearrays doubles from the normal ones
@pytest.mark.parametrize('encoding', ['utf-8'])
@pytest.mark.parametrize('string, min_len, result, default_result', [
    ('', 0, '', ''),
    ('', 1, '', ''),
    (' \t', 1, ' \t', ' '),
    (' \t', 2, ' \t', ' \t'),
    (' a ', 1, ' ', ' a'),
    (' a ', 2, ' a', ' a'),
    (' a ', 3, ' a ', ' a '),
    (chr(0x0bf2) + ' ', 0, '', chr(0x0bf2)),
    (chr(0x0bf2) + ' ', 1, chr(0x0bf2), chr(0x0bf2)),
    (chr(0x0bf2) + ' ', 2, chr(0x0bf2) + ' ', chr(0x0bf2) + ' '),
])
def test_rstrip_min(encoding, string, min_len, result, default_result):
    chars = ' a' + chr(0x0bf2)

    assert rstrip_min(string, min_len, chars) == result
    assert rstrip_min(string, min_len) == default_result

    bstring = string.encode(encoding)
    bchars = chars.encode(encoding)
    bresult = result.encode(encoding)
    bdefault_result = default_result.encode(encoding)

    if string and string[0] == chr(0x0bf2):
        bresult = bstring[:min_len]
        bdefault_result = chr(0x0bf2).encode(encoding)

    assert rstrip_min(bstring, min_len, bchars) == bresult
    assert rstrip_min(bstring, min_len) == bdefault_result


@pytest.mark.parametrize('encoding', ['utf-8'])
@pytest.mark.parametrize('substr, strip, result', [
    (')', False, [True, False, (1, 2), (1, 3)]),
    (')', True, [True, True, (1, 2), (1, 3)]),
    (') ', False, [True, False, (1, 2), (1, 4)]),
    (') ', True, [True, True, (1, 2), (1, 3)]),
    (' )', False, [False] + [None] * 3),
    (' )', True, [True, True, (1, 2), (1, 3)]),
    ('(', False, [True, False, (1, 0), (1, 1)]),
    ('(', True, [True, False, (1, 0), (1, 1)]),
    ('( ', False, [False] + [None] * 3),
    ('( ', True, [True, False, (1, 0), (1, 1)]),
    (' (', False, [True, False, (0, 0), (0, 2)]),
    (' (', True, [True, False, (1, 0), (1, 1)]),
])
def test_rfind_substring_in_paragraph(encoding, substr, strip, result):
    lines = MyIterable(textwrap.dedent('''\
     ({blank}
    (0) {blank}
    ''').format(blank='\t\v').split('\n'))

    def test(tail):
        assert tuple(result) == rfind_substring_in_paragraph(
            lines, substr, strip)

        new_result = result.copy()
        if result[0]:
            new_result[1] = result[1] and strip
        assert tuple(new_result) == rfind_substring_in_paragraph(
            lines + [tail], substr, strip)

    test('\n')

    lines = MyIterable(line.encode(encoding) for line in lines)
    substr = substr.encode(encoding)

    test('\n'.encode(encoding))


def my_func(*, y, **kwargs_):
    pass

# TODO partial


@pytest.mark.parametrize('func, for_sphinx, result', [
    (lambda: 0, False, []),
    (lambda: 0, True, []),
    (lambda x_, *args_: 0, False, ['x_', '*args_']),
    (lambda x_, *args_: 0, True, [r'x\_', r'\*args\_']),
    (my_func, False, ['y', '**kwargs_']),
    (my_func, True, ['y', r'\*\*kwargs\_']),
    (MyFunctor(), False, ['x', 'y_']),
    (MyFunctor(), True, ['x', r'y\_']),
])
def test_get_args(func, for_sphinx, result):
    assert get_args(func, for_sphinx) == result
    # TODO
    assert get_args(MyCallable(func)) == [r'\*args', r'\*\*kwargs']


@pytest.mark.parametrize('always_document_default_args', [True, False])
@pytest.mark.sphinx('text', testroot='dummy')
def test_sphinx_output(app, status, warning, always_document_default_args):
    test_path = pathlib.Path(__file__).parent

    # Add test directory to sys.path to allow imports of dummy module.
    if str(test_path) not in sys.path:
        sys.path.insert(0, str(test_path))

    app.config.always_document_default_args = always_document_default_args
    # app.config.autodoc_mock_imports = ['mailbox']
    app.build()

    assert 'build succeeded' in status.getvalue()  # Build succeeded

    # There should be a warning
    warnings = warning.getvalue().strip()
    assert re.search('dummy_module.py:docstring of dummy_module.TestClassWithArgs.'
                     r'method_with_args_asterisk_not_escaped:\d+: '
                     'WARNING: Inline emphasis start-string without end-string.',
                     warnings), warnings

    pre_dict = {
        'param': '\n\n   Parameters:\n'
        '      **{var}**{type_str} --  "{default}"',
        'midparam': '\n\n      * **{var}**{type_str} --  "{default}"',
        'kw': '\n\n   Keyword Arguments:\n'
        '      **{var}**{type_str} --  "{default}"',
    }
    varlist = ('x', 'a')
    typelist = ('', 'int', 'str')
    defaultlist = ('None', '0')

    format_args = {}
    for (pre, text), var, typename, default, indentation_level in \
            itertools.product(pre_dict.items(), varlist,
                              typelist, defaultlist, range(4)):
        key = '{}_{}_t{}_v{}_ind{}'.format(pre, var, typename, default,
                                           indentation_level)
        format_args[key] = textwrap.indent(
            text.format(var=var, default=default,
                        type_str=' ({}*optional*)'.format(
                            '*{}**, *'.format(typename) if typename else ''),
                        ),
            '   ' * indentation_level) \
            if always_document_default_args else ''

    text_path = pathlib.Path(app.srcdir) / '_build' / 'text' / 'index.txt'
    with text_path.open('r') as f:
        text_contents = f.read().replace('–', '--')
        expected_contents = textwrap.dedent('''\
        Dummy Module
        ************

        dummy_module.func(x=None, y=None)

           Example docstring.

           Parameters:
              * **x** (*optional*) -- The default value "None" will be added
                here.  "None"

              * **y** (*optional*) --

                The text of default value is unchanged.

                 "'Default Value'"

        class dummy_module.TestClassWithReturn(x=None)

           Class docstring.{param_x_t_vNone_ind0}

           method_with_last_defargs(x, y, a=0, **kw)

              Method docstring.

              Returns:
                 0

              Parameters:
                 * **x** -- foo

                 * **y** -- bar{midparam_a_t_v0_ind1}

              Keyword Arguments:
                 ****kw** -- null

           method_with_mid_defargs(x, a=0, y='')

              Method docstring.

              Returns:
                 0

              Parameters:
                 * **x** (*int**, **str*) -- foo{midparam_a_t_v0_ind1}

                 * **y** (*str**, **optional*) -- bar  empty

        class dummy_module.TestClassWithArgs

           Class docstring.

           method_with_args(a, x=0, *args)

              Method docstring.

              Parameters:
                 * **a** -- foo{midparam_x_t_v0_ind1}

                 * ***args** -- bar

           method_with_args_asterisk_not_escaped(a, x=0, *args)

              Method docstring.

              Parameters:
                 * **a** -- foo{midparam_x_t_v0_ind1}

                 * ***args** --

                   bar

           method_with_args_no_asterisk(a, x=0, *args)

              Method docstring.

              Parameters:
                 * **a** -- foo{midparam_x_t_v0_ind1}

                 * **args** -- bar

           method_with_kwargs_as_kw_x_forced_param(a, *, x=0, **kwargs)

              Method docstring.

              Parameters:
                 * **a** -- foo{midparam_x_t_v0_ind1}

                 * ****kwargs** -- bar

           method_with_kwargs_as_kw_x_kw(*, a, x=0, **kwargs)

              Method docstring.

              Keyword Arguments:
                 * **a** -- foo{midparam_x_t_v0_ind1}

                 * ****kwargs** -- bar

           method_with_kwargs_as_kw_x_param(x=0, {slash}**kwargs)

              Method docstring.{param_x_t_v0_ind1}

              Keyword Arguments:
                 ****kwargs** -- foo

           method_with_kwargs_as_param(a, x=0, **kwargs)

              Method docstring.

              Parameters:
                 * **a** -- foo{midparam_x_t_v0_ind1}

                 * ****kwargs** -- bar

           method_with_last_kw_optional(*args, x=0)

              Method docstring.

              Returns:
                 0

              Parameters:
                 ***args** -- foo{kw_x_t_v0_ind1}

              Raises:
                 **ValueError** -- If "x" is nonzero.
        ''')
        print(text_contents)
        expected_contents = expected_contents.format(
            slash='' if sys.version_info[:2] < (3, 8) else '/, ',
            **format_args).replace('–', '--')
        assert text_contents == expected_contents
