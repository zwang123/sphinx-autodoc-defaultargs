"""
    sphinx-autodoc-defaultargs
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    Automatic generation of default arguments
    for the Sphinx autodoc extension.
    :copyright: Copyright 2021 by Zhi Wang.
    :license: MIT, see LICENSE for details.
"""

import inspect
import itertools
import re
import sys
from typing import Any, AnyStr, Optional, Union

if sys.version_info.major == 3 and sys.version_info.minor >= 9:
    from collections.abc import Callable, Collection, Iterable, Sequence
    List = list
    OrderedDictType = dict
    Tuple = tuple
else:
    # typing.OrderedDict is new in Python 3.7.2.
    # but OrderedDict is a subclass of dict
    from typing import Callable
    from typing import Dict as OrderedDictType
    from typing import Iterable, List, Sequence, Tuple

    try:
        from typing import Collection
    except ImportError:
        from typing import Container, Sized, TypeVar
        T_co = TypeVar('T_co', covariant=True)

        class Collection(Sized, Iterable[T_co], Container[T_co]):
            __slots__ = ()

if sys.version_info.major == 3 and sys.version_info.minor >= 7:
    OrderedDict = dict
    from re import Pattern
else:
    from collections import OrderedDict
    Pattern = type(re.compile(''))

from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.util.inspect import object_description
from sphinx.util.inspect import signature as Signature
from sphinx.util.inspect import unwrap_all

logger = logging.getLogger(__name__)

param_fields = ('param', 'parameter', 'arg', 'argument')
other_fields = (
    'raises', 'raise', 'except', 'exception', 'var', 'ivar', 'cvar',
    'vartype', 'returns', 'return', 'rtype', 'meta', 'key', 'keyword')


def match_field(lines: Iterable[AnyStr],
                searchfor: Union[AnyStr, Iterable[AnyStr], Pattern],
                include_blank: bool = False,
                ) -> Tuple[bool, int, int,
                           Optional[AnyStr], Optional[List[AnyStr]]]:
    """Find fields in ``lines``.

    Args:
        include_blank:
            If False, match ends as soon as an empty line is reached.
            Otherwise, it will keep searching until an nonempty line
            starting with nonwhitespace is reached, or till the end.

    Returns:
        ``(found, starting_line_index, ending_line_index,
        matched, text)``.
        Line index is left inclusive and right exclusive.
    """

    found = False
    starting_line_index = None
    ending_line_index = None
    matched = None
    text = None
    for i, line in enumerate(lines):
        # Only match once
        if not found:
            if isinstance(searchfor, Pattern):
                # Match the **beginning** of ``line``
                match = searchfor.match(line)
                if match:
                    found = True
                    starting_line_index = i
                    matched = match.group(0)
            elif isinstance(searchfor, str) or isinstance(searchfor, bytes):
                if line.startswith(searchfor):
                    found = True
                    starting_line_index = i
                    matched = searchfor
            else:
                for search_string in searchfor:
                    if line.startswith(search_string):
                        found = True
                        starting_line_index = i
                        matched = search_string
                        break

        # Found the next item
        # NOTE bytes[0] is not bytes
        #      type(line)(line[0]).isspace() <- bugged
        #      bytes(int) -> \x00 array of length arg
        elif line and line.lstrip() == line or not line and not include_blank:
            ending_line_index = i
            break

    # i is len(lines) - 1 if the loop goes completely
    if ending_line_index is None:
        if not found:
            assert starting_line_index is None
            starting_line_index = i + 1  # Set no matter found or not
        ending_line_index = i + 1  # Set no matter found or not

    assert (starting_line_index == ending_line_index) == (not found)

    # matched is `:...:`
    # should remove `:...: `

    if found:
        text = [line[len(matched) + 1:] for line in itertools.islice(
            lines, starting_line_index, ending_line_index)]

    return found, starting_line_index, ending_line_index, matched, text

# TODO
#   test default after a Note block


def rstrip_min(string: AnyStr, min_len: int,
               chars: Optional[AnyStr] = None) -> AnyStr:
    """:meth:`str.rstrip` but keep first ``min_len`` chars unchanged."""
    str_copy = string
    result = string.rstrip(chars)
    return str_copy[:min_len] if len(result) < min_len else result


def rfind_substring_in_paragraph(lines: Iterable[AnyStr],
                                 substr: AnyStr, strip: bool = True,
                                 multiline_matching: bool = False
                                 ) -> Tuple[bool, Optional[bool],
                                            Optional[Tuple[int, int]],
                                            Optional[Tuple[int, int]]]:
    """
    Find the last matching ``substr`` in ``lines``.

    Returns:
        ``(found, is_end, match_start, match_end)``.

        If not None, ``match_start`` and ``match_end`` are in format
        ``(line index, column index)``.
        Both line indices are inclusive,
        but column follows left inclusive,
        right exclusive convention.
    """

    found = False
    is_end = None
    match_start = None
    match_end = None

    last_nonempty = len(lines) - 1

    # test empty substr
    if strip:
        substr = substr.strip()

    if not multiline_matching:
        for i, line in reversed(list(enumerate(lines))):
            idx_start = line.rfind(substr)
            if idx_start >= 0:
                # found substr
                found = True
                idx_end = idx_start + len(substr)
                # Empty string is not space
                line_end = line[idx_end:].strip() if strip else line[idx_end:]
                is_end = i == last_nonempty and not line_end
                match_start = (i, idx_start)
                match_end = (i, idx_end)
                break
            elif strip and not line.strip():
                last_nonempty -= 1
    else:
        raise NotImplementedError

    return found, is_end, match_start, match_end


def get_args(func: Callable, for_sphinx: bool = True) -> List[str]:
    signature = Signature(unwrap_all(func))
    return ['{}\\_'.format(k[:-1]) if for_sphinx and k.endswith('_')
            else k for k in signature.parameters]


def get_default_args(func: Callable,
                     for_sphinx: bool = True) -> OrderedDictType[str, Any]:
    signature = Signature(func)

    # Backward Compatibility
    #   The built-in Parameter object is guaranteed
    #   an ordered mapping in >= 3.5.
    default_args = OrderedDict()
    for k, v in signature.parameters.items():
        if v.default is not inspect.Parameter.empty:
            if for_sphinx and k.endswith('_'):
                k = '{}\\_'.format(k[:-1])
            default_args[k] = v.default
    return default_args


def find_next_arg(
        lines: Collection[str], args: Sequence[str],
        arg: str, template=r':\S+ {}:') -> Optional[int]:
    """Finds the next argument following ``arg`` before other fields."""

    if arg not in args:
        return None

    nextarg_idx = args.index(arg) + 1

    for nextarg in args[nextarg_idx:]:
        found, start = match_field(
            lines, re.compile(template.format(nextarg)))[:2]
        if found:
            return start

    # Other fields might come before param field
    prev_line_idx = 0
    for prevarg in reversed(args[:nextarg_idx]):
        found, start = match_field(
            lines, re.compile(template.format(prevarg)))[:2]
        if found:
            prev_line_idx = start
            break

    start = match_field(
        lines[prev_line_idx:], [':{}'.format(field)
                                for field in other_fields])[1]

    # Should return len(lines) if nextarg not found
    return start + prev_line_idx


def process_docstring(app: Sphinx, what, name, obj, options, lines):
    """Process docstring after Sphinx.

    See `autodoc-process-docstring <https://www.sphinx-doc.org/en/master/
    usage/extensions/autodoc.html#event-autodoc-process-docstring>`_
    """

    # original_obj = obj
    if isinstance(obj, property):
        obj = obj.fget

    if not callable(obj):
        return

    if inspect.isclass(obj):
        obj = getattr(obj, '__init__', getattr(obj, '__new__', None))
        # obj = getattr(obj, '__init__')

    obj = inspect.unwrap(obj)

    default_args = get_default_args(obj)
    for argname, default in default_args.items():

        # what if default has \
        default = ':code:`{}`'.format(object_description(default))

        # TODO
        # should be arguments
        strip = app.config.docstring_default_arg_strip_matching
        docstring_default_arg_parenthesis = False

        # Search for parameters
        # TODO Test case: empty param
        searchfor = [':{} {}:'.format(field, argname)
                     for field in param_fields]
        param_found, param_start_line, param_end_line, \
            param_matched, param_text = match_field(
                lines, searchfor, include_blank=app.config.
                docstring_default_arg_after_directives)

        if param_found:

            if app.config.docstring_default_arg_substitution not in ' '.join(
                    param_text):

                # Extracts all the flags
                for head, tail in app.config.docstring_default_arg_flags:
                    tail_found, is_end, t_start, _ = \
                        rfind_substring_in_paragraph(
                            param_text, tail, strip,
                            app.config.
                            docstring_default_arg_flags_multiline_matching)
                    if tail_found and is_end:
                        head_found, _, h_start, h_end = \
                            rfind_substring_in_paragraph(
                                param_text, head, strip,
                                app.config.
                                docstring_default_arg_flags_multiline_matching)
                        if head_found:
                            # what if default has \
                            if h_end[0] == t_start[0]:
                                default = param_text[h_end[0]
                                                     ][h_end[1]:t_start[1]]
                            else:
                                default = ' '.join(
                                    [param_text[h_end[0]][h_end[1]:]] +
                                    param_text[h_end[0] + 1:t_start[0]] +
                                    [param_text[t_start[0]][:t_start[1]]])
                            if strip:
                                default = default.strip()
                            lines[param_start_line + h_start[0]] = \
                                lines[param_start_line + h_start[0]
                                      ][:len(param_matched) + 1 + h_start[1]]
                            del lines[param_start_line +
                                      h_start[0] + 1: param_end_line]
                            param_end_line = param_start_line + h_start[0] + 1
                            break

                if strip:
                    lines[param_end_line - 1] = rstrip_min(
                        lines[param_end_line - 1], len(param_matched) + 1)

                if docstring_default_arg_parenthesis:
                    raise NotImplementedError
                else:
                    # To prevent insertion into Note directives or so
                    lines.insert(
                        param_end_line,
                        ' ' * len(param_matched) + ' {} {}'.format(
                            app.config.docstring_default_arg_substitution,
                            default))
        elif app.config.always_document_default_args:

            # Since ``kwargs`` (no default args) might come
            # after ``argname``, it will not be in ``default_args``.
            # Need to generate the full args list.
            next_start = find_next_arg(lines, get_args(obj), argname)

            if docstring_default_arg_parenthesis:
                raise NotImplementedError
            else:
                lines.insert(
                    next_start, ':param {}: {} {}'.format(
                        argname,
                        app.config.docstring_default_arg_substitution,
                        default))

        # Search for type
        type_found, type_start, type_end, type_matched, type_text = \
            match_field(lines, ':{} {}:'.format('type', argname),
                        include_blank=False)

        if type_found:
            type_text = ' '.join(type_text)
            if strip:
                type_text = type_text.rstrip()
                lines[type_end - 1] = rstrip_min(lines[type_end - 1],
                                                 len(type_matched) + 1)
            if not type_text.endswith('optional'):
                if not type_text.strip():
                    lines[type_start] = '{} optional'.format(type_matched)
                elif '`' in type_text:
                    # TODO check \` escape
                    lines[type_end - 1] += ', *optional*'
                else:
                    # Do not insert newline to prevent whitespace before ','
                    lines[type_end - 1] += ', optional'
        elif param_found or app.config.always_document_default_args:
            next_start = find_next_arg(lines, get_args(obj), argname)
            lines.insert(
                next_start, ':type {}: optional'.format(argname))


def setup(app: Sphinx):
    app.add_config_value('always_document_default_args', False, 'html')
    app.add_config_value('docstring_default_arg_flags',
                         [('(Default: ', ')')], 'html')
    app.add_config_value(
        'docstring_default_arg_flags_multiline_matching',
        False, 'html')
    app.add_config_value(
        'docstring_default_arg_strip_matching',
        True, 'html')
    app.add_config_value(
        'docstring_default_arg_after_directives',
        False, 'html')
    app.add_config_value('docstring_default_arg_substitution',
                         '|default|', 'html')
    # app.add_config_value('docstring_default_arg_parenthesis', True, 'html')

    app.connect('autodoc-process-docstring', process_docstring)
    return dict(parallel_read_safe=True)
