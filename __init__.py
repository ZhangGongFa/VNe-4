"""Public package for the upgraded VNe‑4 application.

This package exposes modules that collectively power the corporate
financial dashboard, including:  

* ``app.py`` – the Streamlit entry point that defines the layout,
  ticker selection and high‑level navigation for the app.  

* ``tabs`` – a subpackage containing individual tab rendering
  functions for the Finance, Sentiment and Summary sections.  These
  modules encapsulate the visualisation logic and make it easier to
  maintain discrete parts of the user interface.  

* ``financial_subtabs`` – helper modules used by the Finance tab for
  rendering income statements, balance sheets, cashflow statements
  and computed financial indicators.  

* ``utils`` – shared helpers for loading CSV data, transforming
  financial statements into a clean format and injecting global CSS
  across the app.

* ``analysis_utils`` – (added in this upgrade) a collection of
  functions used exclusively by the Summary tab to load and score
  corporate default probabilities using a LightGBM model.  This
  package contains logic ported from the user‑provided PD‑monotonic
  constraints repository so that the final application is fully
  self‑contained.

Users should import from these subpackages rather than from the
private modules directly.  See ``app.py`` for usage.
"""

# Expose top level subpackages for easier import
from . import tabs  # noqa: F401
from . import financial_subtabs  # noqa: F401
from . import utils  # noqa: F401
from . import analysis_utils  # noqa: F401