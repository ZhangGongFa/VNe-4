"""Tab rendering functions.

This subpackage contains one module per top‑level tab in the
dashboard: ``financial``, ``sentiment`` and ``summary``.  Each
module exposes a single ``render`` function that accepts a
filtered dataframe (for the selected ticker) and is responsible
for generating the appropriate Streamlit components.

Importing this package will automatically discover the modules so
that ``app.py`` can call ``tabs.financial.render(...)`` etc.
"""

from . import financial  # noqa: F401
from . import sentiment  # noqa: F401
from . import summary  # noqa: F401