# -*- coding: utf-8 -*-
#
# xotl.tools documentation build configuration file, created by
# sphinx-quickstart on Fri Jun 15 14:31:00 2012.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# fmt: off

import sys, os

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

sys.path.insert(0, os.path.abspath('../'))

# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.autosummary',
              'sphinx.ext.doctest',
              'sphinx.ext.viewcode',
              'sphinx.ext.intersphinx',
              'sphinx.ext.todo']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'xotl.tools'

from datetime import datetime    # noqa
# Any year before to 2012 xotl.tools copyrights to "Medardo Rodriguez"
copyright = u'2012-{} Merchise Autrement [~º/~] and Contributors'
copyright = copyright.format(datetime.now().year)
del datetime

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
try:
    from xotl.tools._version import version_tuple
    version = ".".join(str(p) for p in version_tuple[:3])
    release = ".".join(str(p) for p in version_tuple[:4])
except ImportError:
    from importlib import metadata
    from importlib.metadata import PackageNotFoundError

    try:
        dist = metadata.distribution("xotl-tools")
        version = release = dist.version
    except PackageNotFoundError:
        version = "dev"
        release = "dev"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
language = 'en'

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []


# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
default_role = "code"
html_theme = "furo"
html_theme = "furo"
html_theme_options = {
    "light_css_variables": {
        "font-stack--monospace": '"Roboto Mono", "SFMono-Regular", Menlo, Consolas, Monaco, "Liberation Mono", "Lucida Console", monospace',
    },
}
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'xotl-tools-doc'


# Configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'py3': ('https://docs.python.org/3.12/', None),
    'py38': ('https://docs.python.org/3.8/', None),
    'py39': ('https://docs.python.org/3.9/', None),
    'py310': ('https://docs.python.org/3.10/', None),
    'py311': ('https://docs.python.org/3.11/', None),
    'py313': ('https://docs.python.org/3.13/', None),
    'gevent': ('http://www.gevent.org', None),
    'greenlet': ('https://greenlet.readthedocs.org/en/latest/', None),
    'hypothesis': ('https://hypothesis.readthedocs.io/en/latest/', None),
    'typing_extensions': ('https://typing-extensions.readthedocs.io/en/latest/', None),
}

# Maintain the cache forever.
intersphinx_cache_limit = 365

autosummary_generate = True

# Produce output for todo and todolist
todo_include_todos = True
