import pytest

from sphinx_autodoc_defaultargs import rstrip_min


# The length of 'utf-16' bytearrays doubles from the normal ones
@pytest.mark.parametrize('encoding', ['utf-8'])
@pytest.mark.parametrize('string, min_len, result, default_result', [
    ('',    0, '',    ''),
    ('',    1, '',    ''),
    (' \t', 1, ' \t', ' '),
    (' \t', 2, ' \t', ' \t'),
    (' a ', 1, ' ',   ' a'),
    (' a ', 2, ' a',  ' a'),
    (' a ', 3, ' a ', ' a '),
    (chr(0x0bf2) + ' ', 0, '',                chr(0x0bf2)),
    (chr(0x0bf2) + ' ', 1, chr(0x0bf2),       chr(0x0bf2)),
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
