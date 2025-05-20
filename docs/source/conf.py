# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath('../../src'))

from dendrotweaks import __version__

project = 'DendroTweaks'
copyright = '2024, Roman Makarov'
author = 'Roman Makarov'
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_copybutton',
    'myst_nb'
]

templates_path = ['_templates']
exclude_patterns = []

autodoc_member_order = 'bysource'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'

html_static_path = ['_static']
html_css_files = ['custom.css']

pygments_dark_style = "stata-dark"

copybutton_prompt_text = r'>>> '
copybutton_only_copy_prompt_lines = True

html_theme_options = {
    'sidebar_hide_name': True,
    'light_logo': 'logo.png',
    'dark_logo': 'logo.png',
}
html_favicon = '_static/favicon.png'

nb_execution_mode = "off"