# utils/ui.py — Premium UI kit for Streamlit (English-only, no icons)

import streamlit as st

# Brand palette (edit to match your brand)
PRIMARY = "#0A66C2"
PRIMARY_DARK = "#084C91"
ACCENT = "#19B5FE"
TEXT = "#1B1F24"
MUTED = "#6B7280"
SURFACE = "#FFFFFF"
SURFACE_ALT = "#F7F8FA"
BORDER = "#E5E7EB"

DARK_BG = "#0F141B"
DARK_SURFACE = "#121923"
DARK_SURFACE_ALT = "#0F1722"
DARK_TEXT = "#E5E7EB"
DARK_MUTED = "#9CA3AF"
DARK_BORDER = "#273142"


def inject_global_css():
    st.markdown(
        f"""
<style>
:root {{
  --primary: {PRIMARY};
  --primary-dark: {PRIMARY_DARK};
  --accent: {ACCENT};
  --text: {TEXT};
  --muted: {MUTED};
  --surface: {SURFACE};
  --surface-alt: {SURFACE_ALT};
  --border: {BORDER};
}}

html[data-theme="dark"] {{
  --text: {DARK_TEXT};
  --muted: {DARK_MUTED};
  --surface: {DARK_SURFACE};
  --surface-alt: {DARK_BG};
  --border: {DARK_BORDER};
  --primary: {PRIMARY};
  --primary-dark: {PRIMARY_DARK};
}}

html, body {{
  background: var(--surface-alt);
  color: var(--text);
}}

.block-container {{
  padding-top: 0.75rem;
  padding-bottom: 1rem;
  max-width: 1480px;
}}

h1, h2, h3 {{
  letter-spacing: 0.2px;
  color: var(--text);
}}

h1 {{ font-weight: 800; }}
h2 {{ font-weight: 700; }}
h3 {{ font-weight: 700; }}

[data-testid="stToolbar"], [data-testid="StyledFullScreenButton"] {{
  display: none !important;
}}

.sidebar .sidebar-content {{ background: var(--surface); }}

section.main > div:has(> .kpibar) {{
  margin-top: 0.25rem;
}}

/* ===== Sticky header bar ===== */
.premium-header {{
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 10px 8px 8px 8px;
  margin: -0.75rem -1rem 10px -1rem;
}}
.premium-header .row {{
  display: flex; align-items: center; gap: 16px;
}}
.premium-badge {{
  background: var(--primary);
  color: white; font-weight: 700; font-size: 13px;
  padding: 6px 10px; border-radius: 10px;
  letter-spacing: .3px;
}}
.premium-title {{
  font-size: 22px; font-weight: 800;
}}
.premium-sub {{
  font-size: 13px; color: var(--muted);
}}

/* ===== Tab bar (pill style) ===== */
[data-testid="stTabs"] div[role="tablist"] {{
  gap: 10px; padding: 6px; border: 1px solid var(--border);
  border-radius: 12px; background: var(--surface);
}}
[data-testid="stTabs"] button[role="tab"] {{
  background: transparent; color: var(--text);
  padding: 8px 14px; border-radius: 10px; border: none;
  font-weight: 600;
}}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
  background: var(--primary); color: white;
  font-weight: 700;
}}
[data-testid="stTabs"] button[role="tab"]:focus {{ outline: none; }}

/* ===== Cards ===== */
.card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px 16px;
}}
.card-title {{
  font-size: 13px; color: var(--muted); margin-bottom: 4px;
}}
.card-value {{
  font-size: 22px; font-weight: 800; letter-spacing: .3px;
}}
.card-delta-up {{ color: #0FA958; font-weight: 700; }}
.card-delta-down {{ color: #C62828; font-weight: 700; }}

/* ===== Dataframes ===== */
[data-testid="stDataFrame"] div[role="grid"] {{
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--surface);
}}
[data-testid="stDataFrame"] thead th {{
  font-weight: 700 !important;
  background: var(--surface-alt) !important;
  color: var(--text) !important;
  border-bottom: 1px solid var(--border) !important;
  font-size: 13px !important;
}}
[data-testid="stDataFrame"] tbody td {{
  font-size: 13px;
}}

</style>
<script>
  // Minimal client-side theme switch: adds data-theme to <html>
  const setTheme = (mode) => {{
    document.documentElement.setAttribute('data-theme', mode === 'dark' ? 'dark' : 'light');
    localStorage.setItem('__premium_theme__', mode);
  }};
  const saved = localStorage.getItem('__premium_theme__') || 'light';
  setTheme(saved);
  window.__setPremiumTheme = setTheme;
</script>
        """,
        unsafe_allow_html=True,
    )


def header(title: str, right_note: str = ""):
    """Sticky header row."""
    st.markdown(
        f"""
<div class="premium-header">
  <div class="row">
    <div class="premium-badge">Corporate Dashboard</div>
    <div class="premium-title">{title}</div>
    <div class="premium-sub">{right_note}</div>
    <div style="margin-left:auto;"></div>
    <div class="premium-sub">Theme</div>
    <button id="theme-light" style="margin-left:6px;padding:4px 10px;border-radius:8px;border:1px solid var(--border);background:var(--surface);cursor:pointer;">Light</button>
    <button id="theme-dark" style="margin-left:6px;padding:4px 10px;border-radius:8px;border:1px solid var(--border);background:var(--surface);cursor:pointer;">Dark</button>
  </div>
</div>
<script>
  const l = document.getElementById('theme-light');
  const d = document.getElementById('theme-dark');
  if (l && d) {{
    l.onclick = () => window.__setPremiumTheme('light');
    d.onclick = () => window.__setPremiumTheme('dark');
  }}
</script>
        """,
        unsafe_allow_html=True,
    )


def kpi_row(items):
    """
    Render a responsive KPI row.
    items: list[dict] with keys: title, value, delta (optional, can be "+1.2%" or "-0.7%")
    """
    cols = st.columns(len(items), gap="small")
    for col, item in zip(cols, items):
        with col:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f'<div class="card-title">{item["title"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-value">{item["value"]}</div>', unsafe_allow_html=True)
            if "delta" in item and item["delta"]:
                klass = "card-delta-up" if str(item["delta"]).startswith("+") else "card-delta-down"
                st.markdown(f'<div class="{klass}">{item["delta"]}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
