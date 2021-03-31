import itertools
import pathlib
import re
import sys
import textwrap
from collections import abc

import pytest
from conftest import MyIterable

from sphinx_autodoc_defaultargs import match_field, rstrip_min


@pytest.mark.parametrize('args', [(), ([],), ((1,),), ((0, 1),), (range(1),)])
@pytest.mark.parametrize('kwargs', [{}])
def test_my_iterable(args, kwargs):
    print(MyIterable, args, kwargs)
    assert issubclass(MyIterable, abc.Iterable)
    assert not issubclass(MyIterable, abc.Container)
    assert not issubclass(MyIterable, abc.Hashable)
    assert not issubclass(MyIterable, abc.Iterator)
    assert not issubclass(MyIterable, abc.Sized)
    assert not issubclass(MyIterable, abc.Callable)
    assert not issubclass(MyIterable, abc.Sequence)
    assert not issubclass(MyIterable, abc.Set)
    assert not issubclass(MyIterable, abc.Mapping)
    try:
        assert not issubclass(MyIterable, abc.Collection)
    except AttributeError:
        pass  # Python 3.5 Compatibility
    my_iterable = MyIterable(*args, **kwargs)
    print(my_iterable.contents)
    assert isinstance(my_iterable, abc.Iterable)
    for _ in my_iterable:
        pass
    [x for x in my_iterable]

    assert my_iterable.contents == tuple(*args, **kwargs)


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

    # # There should be a warning about an unresolved forward reference
    # warnings = warning.getvalue().strip()
    # assert 'Cannot ' in warnings, warnings

    pre_dict = {
        'param': '\n\n   Parameters:\n'
        '      **{var}**{type_str} --  "{default}"',
        'midparam': '\n\n      * **{var}**{type_str} --  "{default}"',
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

        class dummy_module.TestClass(x=None)

           Class docstring.{param_x_t_vNone_ind0}

           method_with_last_defargs(x, y, a=0, **kw)

              Method docstring.

              Returns:
                 0

              Parameters:
                 * **x** -- foo

                 * **y** -- bar{midparam_a_t_v0_ind1}

                 * **kw** -- null

           method_with_mid_defargs(x, a=0, y='')

              Method docstring.

              Returns:
                 0

              Parameters:
                 * **x** (*int**, **str*) -- foo{midparam_a_t_v0_ind1}

                 * **y** (*str**, **optional*) -- bar  empty
        ''')
        print(text_contents)
        expected_contents = expected_contents.format(
            **format_args).replace('–', '--')
        assert text_contents == expected_contents
