import inspect
from typing import Union, AnyStr, Optional

import sys
if sys.version_info.major == 3 and sys.version_info.minor >= 9:
    from collections.abc import Iterable, Callable
    Tuple = tuple
else:
    from typing import Iterable, Callable, Tuple

from sphinx.util import logging
from sphinx.util.inspect import signature as Signature
from sphinx.util.inspect import object_description

from sphinx.application import Sphinx

logger = logging.getLogger(__name__)


def get_default_args(func: Callable):
    signature = Signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }
#        # what if default has \
#        default = object_description(default)
#
#        starting_line_index = None
#        for i, line in enumerate(lines):
#            if any(line.startswith(search_string) for search_string in searchfor):
#                starting_line_index = i
#            elif starting_line_index is not None and line.startswith(':'):
#                ending_line_index = i
#        if starting_line_index is None:
#            if app.config.always_document_param_types:
#                lines.append(':param {}: {} :code:`{}`'.format(
#                    argname, app.config.docstring_default_arg_substitution, default))
#        else:
#            param_text = ' '.join(lines[i].strip() for i in range(starting_line_index,ending_line_index))
#            if app.config.docstring_default_arg_substitution not in param_text
#
#                # Extracts all the flags
#                for begins, ends in app.config.docstring_default_arg_flags:
#                    if begins in line and line.endswith(ends):
#                        idx = line.rfind(begins)
#                        # what if default has \
#                        default = line[idx + len(begins):-len(ends)]
#                        # Remove all trailing whitespaces
#                        lines[i] = line[:idx].rstrip()
#                        break
#                lines[i] += ' |default| :code:`{}`'.format(default)
#                break
#
#
#        insert_index = None
#        for i, line in enumerate(lines):
#            if line.startswith(':{} {}:'.format('type', argname)):
#                insert_index = i
#                if not line.endswith('optional'):
#                    lines[i] += ', optional'
#                break
#
#        if insert_index is None and app.config.always_document_param_types:
#            lines.append(':type {}: optional'.format(argname))
#            insert_index = len(lines)
#

def match_directive(lines: Iterable[AnyStr], searchfor: Union[AnyStr, Iterable[AnyStr]]) -> Tuple[bool, int, int, Optional[AnyStr], Optional[AnyStr]]: # , Optional[AnyStr]]:
    """Find directives in ``lines``."""
    found = False
    starting_line_index = len(lines)
    ending_line_index = None
    matched = None
    text = None
    # concatenated_text = None
    for i, line in enumerate(lines):
        # Only match once
        if not found:
            if isinstance(searchfor, str) or isinstance(searchfor, bytes):
                # found = line.startswith(searchfor)
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
                # found = any(line.startswith(search_string) for search_string in searchfor)

            # if found:
            #     starting_line_index = i
            #     # continue
        # Found the next item
        elif line and not line[0].isspace():
        # elif not line or not line[0].isspace():
        # elif line.startswith(':'):
            ending_line_index = i
            break
        # elif starting_line_index is not None and line.startswith(':'):
        #     ending_line_index = i

    # i is len(lines) - 1 if the loop goes completely
    if ending_line_index is None:
        ending_line_index = len(lines) # Set no matter found or not

    # logger.warning(f'{searchfor}')
    # logger.warning(f'{starting_line_index}')
    # logger.warning(f'{ending_line_index}')
    # logger.warning('before match_directive returns')
    # logger.warning(starting_line_index == ending_line_index)
    # logger.warning(not found)
    assert (starting_line_index == ending_line_index) == (not found)
    # logger.warning('before match_directive returns')

    # matched is `:...:`
    # should remove `:...: `

    if found:
        text = [lines[i][len(matched)+1:] for i in range(starting_line_index,ending_line_index)] # if len(lines[i]) > len(matched)]
        # concatenated_text = ' '.join(text)

    return found, starting_line_index, ending_line_index, matched, text

# TODO
#   test default after a Note block

# def rfind_substring_in_paragraph(app: Sphinx, lines: Iterable[AnyStr], searchfor: Union[AnyStr, Iterable[AnyStr]], substr: AnyStr, strip: bool = True) -> Tuple[bool, Optional[bool], Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
def rfind_substring_in_paragraph(lines: Iterable[AnyStr], substr: AnyStr, strip: bool = True, multiline_matching : bool = False) -> Tuple[bool, Optional[bool], Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
    # if found and i == len(
    #     ending_line_index = len(lines)

    found = False
    is_end = None
    # (line index, column index)
    # both line indices are inclusive, but column follows left inclusive, right exclusive convention
    match_start = None
    match_end = None

    # last_nonempty = ending_line_index - 1
    last_nonempty = len(lines) - 1

    # test empty substr
    if strip:
        substr = substr.strip()
    else:
        raise NotImplementedError

    # if not app.config.docstring_default_arg_flags_multiline_matching:
    #    for i in reversed(range(starting_line_index, ending_line_index)):
    #        line = lines[i]
    if not multiline_matching:
        for i, line in reversed(list(enumerate(lines))):
            idx_start = line.rfind(substr)
            if idx_start >= 0:
                # found substr
                found = True
                idx_end = idx_start + len(substr)
                if strip:
                    # logger.warning(f'{i}')
                    # logger.warning(f'{last_nonempty}')
                    # logger.warning(f'{i == last_nonempty}')
                    # logger.warning(f'{line[idx_end:]}')
                    # logger.warning(f'{line[idx_end:].isspace()}')
                    # cannot use isspace here
                    # NOTE empty string is not space
                    is_end = i == last_nonempty and not line[idx_end:].strip()
                else:
                    raise NotImplementedError
                match_start = (i, idx_start)
                match_end = (i, idx_end)
                break
            else:
                last_nonempty -= 1 if line.isspace() else 0
    else:
        raise NotImplementedError

    # # if found:
    # #     for i, line in lines[starting_line_index: ending_line_index]:
    # for i in reversed(range(starting_line_index, ending_line_index)):
    #     line = lines[i]

    #     idx = line.rfind(substr)
    #     if idx >= 0:
    #         # found substr
    #         match_start = (i, idx)
    #         match_end = (i, idx + len(substr))
    #     else:
    #         substr[kk:]
    #         substr = substr[:kk]
    # #    if substr in line:
    # #    text = ' '.join(lines[i].strip() for i in range(starting_line_index, ending_line_index))
    # #    if app.config.docstring_default_arg_substitution not in param_text:

    # #        # Extracts all the flags
    # #        for begins, ends in app.config.docstring_default_arg_flags:
    # #            if begins in line and line.endswith(ends):
    # #                idx = line.rfind(begins)
    # #                # what if default has \
    # #                default = line[idx + len(begins):-len(ends)]
    # #                # Remove all trailing whitespaces
    # #                lines[i] = line[:idx].rstrip()
    # #                break
    # #        lines[i] += ' |default| :code:`{}`'.format(default)
    # #        break

    return found, is_end, match_start, match_end

    # if not found:
    #     if app.config.always_document_param_types:
    #         lines.append(':param {}: {} :code:`{}`'.format(
    #             argname, app.config.docstring_default_arg_substitution, default))


def process_docstring(app: Sphinx, what, name, obj, options, lines):
    # # logger.warning(f'___ obj{obj}')
    original_obj = obj
    if isinstance(obj, property):
        obj = obj.fget

    if not callable(obj):
        return

    # original_obj = obj
    if inspect.isclass(obj):
        obj = getattr(obj, '__init__', getattr(obj, '__new__', None))
        # obj = getattr(obj, '__init__')

    obj = inspect.unwrap(obj)

    # try:
    #     if original_obj.__name__.startswith('Exception') or original_obj.__name__.endswith('t_object'):
    #         logger.warning(f'obj {obj}')
    #         for i, line in enumerate(lines):
    #             logger.warning(f'line {i}: {repr(line)}')
    # except AttributeError:
    #     pass


    # type_hints = get_all_type_hints(obj, name)

    # for argname, annotation in type_hints.items():
    for argname, default in get_default_args(obj).items():
        # if argname == 'return':
        #     continue  # this is handled separately later
        if argname.endswith('_'):
            argname = '{}\\_'.format(argname[:-1])

        # formatted_annotation = format_annotation(
        #     annotation,
        #     fully_qualified=app.config.typehints_fully_qualified,
        #     simplify_optional_unions=app.config.simplify_optional_unions)

        # what if default has \
        default = ':code:`{}`'.format(object_description(default))

        # TODO
        strip = True
        docstring_default_arg_parenthesis = False

        # TODO Test case: empty param
        # searchfor = [':{} {}: '.format(field, argname)
        searchfor = [':{} {}:'.format(field, argname)
                     for field in ('param', 'parameter', 'arg', 'argument')]
        param_found, param_start_line, param_end_line, param_matched, param_text = match_directive(lines, searchfor)

        # starting_line_index = None
        # for i, line in enumerate(lines):
        #     if any(line.startswith(search_string) for search_string in searchfor):
        #         starting_line_index = i
        #     elif starting_line_index is not None and line.startswith(':'):
        #         ending_line_index = i

        if param_found:

            # param_text = ' '.join(lines[i].strip() for i in range(starting_line_index,ending_line_index))
            if app.config.docstring_default_arg_substitution not in ' '.join(param_text):

                # logger.warning('before docstring_default_arg_flags')
                # Extracts all the flags
                for head, tail in app.config.docstring_default_arg_flags:
                    # logger.warning('In docstring_default_arg_flags')

                    # logger.warning(f'param_text{param_text}')
                    # logger.warning(f'tail{tail}')
                    tail_found, is_end, tail_match_start, _ = \
                        rfind_substring_in_paragraph(
                                param_text, tail, strip,
                                app.config.docstring_default_arg_flags_multiline_matching)
                    # logger.warning(f'tail_found{tail_found}')
                    # logger.warning(f'is_end{is_end}')
                    if tail_found and is_end:
                        head_found, _, head_match_start, head_match_end = \
                            rfind_substring_in_paragraph(
                                    param_text, head, strip,
                                    app.config.docstring_default_arg_flags_multiline_matching)
                        # logger.warning(f'head_found{head_found}')
                        # logger.warning(f'head_match_start{head_match_start}')
                        if head_found:
                            # head_match_end tail_match_start + 1
                            # logger.warning('___ {}'.format(lines[param_start_line + head_match_start[0]+1: param_end_line]))
                            if head_match_end[0] == tail_match_start[0]:
                                default = param_text[head_match_end[0]][head_match_end[1]:tail_match_start[1]]
                            else:
                                default = ' '.join([param_text[head_match_end[0]][head_match_end[1]:]] + \
                                param_text[head_match_end[0] + 1:tail_match_start[0]] + \
                            [param_text[tail_match_start[0]][:tail_match_start[1]]])
                            if strip:
                                default = default.strip()
                            lines[param_start_line + head_match_start[0]] = \
                                    lines[param_start_line + head_match_start[0]][:len(param_matched) + 1 + head_match_start[1]]
                            del lines[param_start_line + head_match_start[0]+1: param_end_line]
                            param_end_line = param_start_line + head_match_start[0]+1
                            break

                    # if begins in line and line.endswith(ends):
                    #     idx = line.rfind(begins)
                    #     # what if default has \
                    #     default = line[idx + len(begins):-len(ends)]
                    #     # Remove all trailing whitespaces
                    #     lines[i] = line[:idx].rstrip()
                    #     break
                # lines[i] += ' |default| :code:`{}`'.format(default)
                if strip:
                    lines[param_end_line-1] = lines[param_end_line-1].rstrip()
                    if not lines[param_end_line-1]:
                        lines[param_end_line-1] = ' '*len(param_matched)

                if docstring_default_arg_parenthesis:
                    # lines[param_end_line-1] += ' ({} {})'.format(app.config.docstring_default_arg_substitution, default)
                    raise NotImplementedError
                else:
                    lines[param_end_line-1] += ' {} {}'.format(app.config.docstring_default_arg_substitution, default)
                # break
        else:
            if app.config.always_document_param_types:
                if docstring_default_arg_parenthesis:
                    raise NotImplementedError
                    # lines.append(':param {}: ({} {})'.format(
                    #     argname, app.config.docstring_default_arg_substitution, default))
                else:
                    lines.append(':param {}: {} {}'.format(
                        argname, app.config.docstring_default_arg_substitution, default))


        # Assume type is single line
        for i, line in enumerate(lines):
            if line.startswith(':{} {}:'.format('type', argname)):
                insert_index = i
                if not line.endswith('optional'):
                    lines[i] += ', optional'
                break

        if i == len(lines) and app.config.always_document_param_types:
            lines.append(':type {}: optional'.format(argname))
            insert_index = len(lines)

        # if insert_index is not None:
        #     lines.insert(
        #         insert_index,
        #         ':type {}: {}'.format(argname, formatted_annotation)
        #     )

        # if 'return' in type_hints and not inspect.isclass(original_obj):
        #     # This avoids adding a return type for data class __init__ methods
        #     if what == 'method' and name.endswith('.__init__'):
        #         return

        #     formatted_annotation = format_annotation(
        #         type_hints['return'], fully_qualified=app.config.typehints_fully_qualified,
        #         simplify_optional_unions=app.config.simplify_optional_unions
        #         )

        #     insert_index = len(lines)
        #     for i, line in enumerate(lines):
        #         if line.startswith(':rtype:'):
        #             insert_index = None
        #             break
        #         elif line.startswith(':return:') or line.startswith(':returns:'):
        #             insert_index = i

        #     if insert_index is not None and app.config.typehints_document_rtype:
        #         if insert_index == len(lines):
        #             # Ensure that :rtype: doesn't get joined with a paragraph of text, which
        #             # prevents it being interpreted.
        #             lines.append('')
        #             insert_index += 1

        #         lines.insert(insert_index, ':rtype: {}'.format(formatted_annotation))


    # try:
    #     if original_obj.__name__.startswith('Exception') or original_obj.__name__.endswith('t_object'):
    #         logger.warning(f'obj {obj}')
    #         for i, line in enumerate(lines):
    #             logger.warning(f'line {i}: {repr(line)}')
    # except AttributeError:
    #     pass


def setup(app: Sphinx):
    # app.add_config_value('set_type_checking_flag', False, 'html')
    try:
        app.add_config_value('always_document_param_types', False, 'html')
    except Exception:
        logger.info("Config value 'always_document_param_types' already present")
    app.add_config_value('docstring_default_arg_flags', 
                [('(Default: ', ')')],
            'html')
    app.add_config_value('docstring_default_arg_flags_multiline_matching', False, 'html')
    app.add_config_value('docstring_default_arg_substitution', 
                '|default|',
            'html')
    # app.add_config_value('docstring_default_arg_parenthesis', True, 'html')

    # app.add_config_value('typehints_fully_qualified', False, 'env')
    # app.add_config_value('typehints_document_rtype', True, 'env')
    # app.add_config_value('simplify_optional_unions', True, 'env')
    # app.connect('builder-inited', builder_ready)
    # app.connect('autodoc-process-signature', process_signature)
    app.connect('autodoc-process-docstring', process_docstring)
    return dict(parallel_read_safe=True)
