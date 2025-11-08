"""
UI helper functions for the upgraded VNe‑4 application.

This module defines a very small surface compared to the original
``utils.ui`` in the VNe‑4 repository.  The functions here are
minimal placeholders to satisfy imports from other modules.  Global
styling is injected from ``app.py`` via the ``inject_global_css``
function.
"""

import streamlit as st

def inject_global_css() -> None:
    """Placeholder for global CSS injection.

    The application injects its styling in ``app.py`` so this
    function intentionally does nothing.  It remains for backwards
    compatibility with modules that import it.
    """
    return None


def header(title: str, right_note: str = "") -> None:
    """Render a simple sticky header.

    Parameters
    ----------
    title : str
        The primary title text.
    right_note : str, optional
        An optional note to display on the right side of the header.
    """
    st.markdown(f"### {title}")
    if right_note:
        st.markdown(f"<small>{right_note}</small>", unsafe_allow_html=True)


def kpi_row(items):
    """Render a row of KPI cards.

    The input ``items`` should be a list of dictionaries each
    containing ``title``, ``value`` and optionally ``delta`` keys.
    """
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        with col:
            st.markdown(
                f'<div class="kpi-card"><div class="kpi-title">{item["title"]}</div>'
                f'<div class="kpi-value">{item["value"]}</div></div>',
                unsafe_allow_html=True,
            )
            if "delta" in item and item["delta"]:
                st.markdown(f'<small>{item["delta"]}</small>', unsafe_allow_html=True)