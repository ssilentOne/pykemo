# Configuration file for the Sphinx documentation builder.

# -- Project information

from os.path import abspath
from sys import path

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
path.insert(0, abspath("../../src"))
path.append(abspath("extensions"))

project = "pykemo"
author = "ssilentOne"

version = "0.5.1"

# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.autodoc",
    "sphinx_design",
    "sphinx_rtd_dark_mode"
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

# -- Options for HTML output
html_theme = "sphinx_rtd_theme"
html_logo = "../../media/img/pykemo_logo.png"

# -- Options for EPUB output
epub_show_urls = "footnote"

# -- autodoc extension configs
autodoc_typehints = "description"
autodoc_mock_imports = ["grequests", "requests", "tqdm"]
