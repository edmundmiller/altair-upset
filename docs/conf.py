"""Sphinx configuration for altair-upset documentation."""

import sys
from datetime import datetime
from pathlib import Path

# Add project root to Python path for autodoc
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

# Project information
project = "altair-upset"
copyright = f"2024-{datetime.now().year}, Edmund Miller"
author = "Edmund Miller"

# Extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinxext_altair.altairplot",
]

# Theme settings
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "show_toc_level": 2,
    "navigation_depth": 4,
    "collapse_navigation": True,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/edmundmiller/altair-upset",
            "icon": "fab fa-github-square",
        },
    ],
    "use_edit_page_button": True,
    "show_nav_level": 2,
}

# GitHub repository
html_context = {
    "github_user": "edmundmiller",
    "github_repo": "altair-upset",
    "github_version": "main",
    "doc_path": "docs",
}

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "altair": ("https://altair-viz.github.io/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
}

# Paths and static files
html_static_path = ["_static"]  # Include _static directory
html_css_files = [
    "custom.css",
]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Numpydoc settings
numpydoc_show_class_members = False
numpydoc_show_inherited_class_members = False
numpydoc_class_members_toctree = False

# Autodoc settings
autodoc_default_flags = ["members", "inherited-members"]
autodoc_member_order = "groupwise"
autodoc_typehints = "none"

# Generate autosummary even if no references
autosummary_generate = True

# Altair plot output settings
altair_plot_links = True
altair_output_type = "html"
altair_plot_width = None  # Let Altair handle width responsively
altair_plot_height = None  # Let Altair handle height responsively
altairplot_html_renderer = "html"
altairplot_vega_js_url = "https://cdn.jsdelivr.net/npm/vega@5"
altairplot_vegalite_js_url = "https://cdn.jsdelivr.net/npm/vega-lite@5"
altairplot_vegaembed_js_url = "https://cdn.jsdelivr.net/npm/vega-embed@6"
