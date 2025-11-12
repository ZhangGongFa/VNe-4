
# -*- coding: utf-8 -*-
"""
Upgraded Finance Tab
- Margin chart with 3 contrasting colours + reference lines
- Auto-adjust axes and labels for number of years
- Zoom via Plotly range slider and Streamlit year filter
"""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from utils_new.lang import get_text

GM_COLOR = "#10B981"  # green
OM_COLOR = "#F59E0B"  # amber
NM_COLOR = "#EF4444"  # red

def _to_num(v, default=np.nan):
    try:
        return float(str(v).replace(",",""))
    except Exception:
        return default

def render(feats_df: pd.DataFrame, raw_df: pd.DataFrame, ticker: str, year: int,
           model, thresholds, sector: str, final_features: list):
    lang = st.session_state.get("current_lang", "vi")
    st.subheader(get_text("finance_header", lang) or "Detailed Financial Analysis")

    # Historical slice for ticker
    sub = raw_df[raw_df["Ticker"].astype(str)==str(ticker)].copy()
    if sub.empty:
        st.info(get_text("warning_no_data", lang))
        return
    sub["Year"] = pd.to_numeric(sub["Year"], errors="coerce")
    sub = sub.dropna(subset=["Year"]).sort_values("Year")

    min_y, max_y = int(sub["Year"].min()), int(sub["Year"].max())
    yr_lo, yr_hi = st.slider("Năm", min_value=min_y, max_value=max_y, value=(max(min_y, max_y-5), max_y), step=1, key=f"fin_year_range_{ticker}")
    sub_f = sub[(sub["Year"]>=yr_lo) & (sub["Year"]<=yr_hi)].copy()

    # Compute margins
    rev = sub_f.get("Net Sales", sub_f.get("Revenue", sub_f.get("Revenue (Bn. VND)", np.nan)))
    gp = sub_f.get("Gross Profit", np.nan)
    op = sub_f.get("Operating Profit/Loss", np.nan)
    npf = sub_f.get("Net Profit For the Year", sub_f.get("Net Profit", np.nan))
    years = sub_f["Year"].astype(int).tolist()
    gross_margin = [(_to_num(gp.iloc[i])/max(_to_num(rev.iloc[i]),1e-9))*100 if not pd.isna(_to_num(gp.iloc[i])) and not pd.isna(_to_num(rev.iloc[i])) and _to_num(rev.iloc[i])!=0 else None for i in range(len(sub_f))]
    operating_margin = [(_to_num(op.iloc[i])/max(_to_num(rev.iloc[i]),1e-9))*100 if not pd.isna(_to_num(op.iloc[i])) and not pd.isna(_to_num(rev.iloc[i])) and _to_num(rev.iloc[i])!=0 else None for i in range(len(sub_f))]
    net_margin = [(_to_num(npf.iloc[i])/max(_to_num(rev.iloc[i]),1e-9))*100 if not pd.isna(_to_num(npf.iloc[i])) and not pd.isna(_to_num(rev.iloc[i])) and _to_num(rev.iloc[i])!=0 else None for i in range(len(sub_f))]

    lbl_gm = 'Biên LN gộp' if lang=='vi' else 'Gross Margin'
    lbl_om = 'Biên LN HĐ' if lang=='vi' else 'Operating Margin'
    lbl_nm = 'Biên LN ròng' if lang=='vi' else 'Net Margin'

    fig = go.Figure()
    fig.add_trace(go.Scatter(name=lbl_gm, x=years, y=gross_margin, mode="lines+markers", line=dict(width=2, color=GM_COLOR)))
    fig.add_trace(go.Scatter(name=lbl_om, x=years, y=operating_margin, mode="lines+markers", line=dict(width=2, color=OM_COLOR)))
    fig.add_trace(go.Scatter(name=lbl_nm, x=years, y=net_margin, mode="lines+markers", line=dict(width=2, color=NM_COLOR)))

    # Reference lines at 0%, 10%, 20%
    for yref in [0, 10, 20]:
        fig.add_shape(type="line", x0=years[0] if years else 0, x1=years[-1] if years else 1, y0=yref, y1=yref, line=dict(dash="dash", width=1))

    fig.update_layout(
        title=("Xu Hướng Biên Lợi Nhuận" if lang=='vi' else "Profit Margin Trends"),
        height=380,
        yaxis=dict(title="%", rangemode="tozero", autorange=True),
        xaxis=dict(rangeslider=dict(visible=True), tickmode="linear", tick0=min(years) if years else 0, dtick=1),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

    # (Optional) other charts in the original tab remain unchanged if present.
