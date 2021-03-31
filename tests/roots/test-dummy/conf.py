import pathlib
import sys

# Make dummy_module.py available for autodoc.
sys.path.insert(0, str(pathlib.Path(__file__).parent))


master_doc = 'index'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx_autodoc_defaultargs',
]

rst_prolog = """
.. |default| raw:: html

    <div class="default-value-section">""" + \
    ' <span class="default-value-label">Default:</span>'

always_document_param_types = True