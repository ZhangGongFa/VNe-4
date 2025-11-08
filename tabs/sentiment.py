"""Sentiment tab renderer.

The Sentiment tab visualises market sentiment metrics associated with
the selected ticker.  It attempts to use sentiment‑related columns
present in the dataset (e.g. ``Sentiment``, ``Sentiment Change`` and
``News Shock``).  If these columns are missing, the tab computes
simple proxies from available financial data.  The tab displays a
line chart of sentiment over time, bar charts of sentiment changes
and news shocks, and summary statistics.
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def _get_column(df: pd.DataFrame, candidates: list, default: pd.Series = None) -> pd.Series:
    """Return the first matching column among a list of candidates.

    If none of the candidate columns exist, ``default`` is returned.  If
    no default is provided, an empty Series is returned.
    """
    for c in candidates:
        if c in df.columns:
            return df[c]
    return default if default is not None else pd.Series(dtype=float)


def render(fin_df):
    """Render the Sentiment tab.

    Parameters
    ----------
    fin_df : pandas.DataFrame
        Filtered dataframe containing rows for the selected ticker.
    """
    if fin_df is None or fin_df.empty:
        st.info("No sentiment data available for this ticker.")
        return

    st.subheader("Market Sentiment Analysis")

    # Derive year for x axis
    years = fin_df.get('Year') if 'Year' in fin_df.columns else fin_df.get('display_year')
    years = years.astype(str) if years is not None else pd.Series([])

    # Extract sentiment columns if present
    sentiment_series = _get_column(fin_df, ['Sentiment', 'sentiment'])
    sentiment_change = _get_column(fin_df, ['Sentiment Change', 'sentiment change', 'sentiment_change'])
    news_shock = _get_column(fin_df, ['News Shock', 'news shock', 'news_shock'])

    # If no sentiment column, derive a simple proxy: normalised net profit margin
    if sentiment_series is None or sentiment_series.empty:
        if 'Net Profit For the Year' in fin_df.columns and 'Net Sales' in fin_df.columns:
            tmp = (fin_df['Net Profit For the Year'].astype(float) / fin_df['Net Sales'].astype(float)).replace([np.inf, -np.inf], np.nan)
            tmp = (tmp - tmp.min()) / (tmp.max() - tmp.min() + 1e-9)
            sentiment_series = tmp.rename("Sentiment")
        else:
            sentiment_series = pd.Series(np.zeros(len(fin_df)), name="Sentiment")

    # Compute changes if not provided
    if sentiment_change is None or sentiment_change.empty:
        sentiment_change = sentiment_series.diff().fillna(0.0).rename("Sentiment Change")
    if news_shock is None or news_shock.empty:
        # Proxy for news shock: absolute change scaled
        news_shock = sentiment_change.abs().rename("News Shock")

    # Build line chart for sentiment
    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(x=years, y=sentiment_series, mode='lines+markers', name='Sentiment'))
    line_fig.update_layout(title='Sentiment over Time', xaxis_title='Year', yaxis_title='Sentiment Score', height=360)
    # Build bar chart for changes and news shock
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(x=years, y=sentiment_change, name='Sentiment Change'))
    bar_fig.add_trace(go.Bar(x=years, y=news_shock, name='News Shock'))
    bar_fig.update_layout(title='Sentiment Change & News Shock', xaxis_title='Year', yaxis_title='Value', barmode='group', height=360)

    # Summary statistics
    avg_sent = float(sentiment_series.mean()) if not sentiment_series.empty else 0.0
    avg_change = float(sentiment_change.mean()) if not sentiment_change.empty else 0.0
    avg_shock = float(news_shock.mean()) if not news_shock.empty else 0.0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Sentiment", f"{avg_sent:.3f}")
    with col2:
        st.metric("Average Sentiment Change", f"{avg_change:.3f}")
    with col3:
        st.metric("Average News Shock", f"{avg_shock:.3f}")

    st.plotly_chart(line_fig, use_container_width=True)
    st.plotly_chart(bar_fig, use_container_width=True)