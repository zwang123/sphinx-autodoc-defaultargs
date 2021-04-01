# sphinx-autodoc-defaultargs

[![PyPi Version](https://img.shields.io/pypi/v/sphinx-autodoc-defaultargs)](https://pypi.org/project/sphinx-autodoc-defaultargs/)
[![Build Status](https://github.com/zwang123/sphinx-autodoc-defaultargs/actions/workflows/python-package.yml/badge.svg)](https://github.com/zwang123/sphinx-autodoc-defaultargs/actions/workflows/python-package.yml)
[![Coverage Status](https://coveralls.io/repos/github/zwang123/sphinx-autodoc-defaultargs/badge.svg?branch=main)](https://coveralls.io/github/zwang123/sphinx-autodoc-defaultargs?branch=main)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/zwang123/sphinx-autodoc-defaultargs/blob/main/LICENSE)
[![Python Versions](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-informational)](https://pypi.org/project/sphinx-autodoc-defaultargs/)

## Overview

This extension automatically generates default arguments for the Sphinx autodoc extension.

## Example

With this package, the default values of all documented arguments, and undocumented arguments if enabled,
are automatically detected and added to the docstring.

It also detects existing documentation of default arguments with the text unchanged.

```python
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
```

## Installation

### pip

If you use `pip`, you can install the package with:

```bash
python -m pip install sphinx_autodoc_defaultargs
```

### setup.py

In the root directory, run the following command in the terminal.

```bash
python setup.py install
```

## Usage

Add the extension as well as the global substitution to the `conf.py` file:

```python
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_autodoc_defaultargs'
]

rst_prolog = """
.. |default| raw:: html

    <div class="default-value-section">""" + \
    ' <span class="default-value-label">Default:</span>'
```

Note that it should be loaded after [sphinx.ext.napoleon](http://www.sphinx-doc.org/en/stable/ext/napoleon.html).

## Config Options

* `always_document_default_args` (default: `False`):
If False, do not add info of default arguments for undocumented parameters.
If True, add stub documentation for undocumented parameters
to be able to add default value and to flag `optional` in the type.

* `docstring_default_arg_flags` (default: `[('(Default: ', ')')]`):
List of pairs indicating the header and the footer of an existing documentation of default values,
which is expected at the end of the `param` section.
If detected, it will be replaced by the unified style but the text should remain unchanged.

* `docstring_default_arg_after_directives` (default: `False`):
If True, the default value will be added after all
[directives](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html)
(e.g., note, warning).
Existing documentation of the default value is also expected after these directives.
Otherwise, it will be added, and expected to exist, before these directives.

* `docstring_default_arg_substitution` (default: `'|default|'`):
The substitution markup defined in the `conf.py` file.
