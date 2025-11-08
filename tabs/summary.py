# tabs/summary.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def _pickcol(df, cands):
    """Pick first matching column from candidates"""
    lower = {c.lower(): c for c in df.columns}
    for c in cands:
        if c in df.columns: return c
        if c.lower() in lower: return lower[c.lower()]
    return None

def render(fin_df: pd.DataFrame):
    """
    Render Risk Summary tab.
    Displays comprehensive risk indicators and default probability metrics.
    """
    st.header("📈 Risk Summary & Analysis")
    st.markdown("Comprehensive view of key financial metrics and risk indicators.")
    
    if fin_df.empty:
        st.warning("No data available for risk summary.")
        return
    
    # Find year column
    ycol = _pickcol(fin_df, ["display_year", "year", "Year"])
    if ycol is None:
        st.error("❌ No year column found in dataset.")
        return
    
    # Get unique years data
    show = fin_df.drop_duplicates(subset=[ycol]).copy()
    
    # Define core financial metrics to display
    core_metrics = [
        ("Net Revenue", ["Net Revenue", "Revenue", "Doanh thu thuần"]),
        ("Total Assets", ["Total Assets", "Tổng tài sản"]),
        ("Equity", ["Equity", "Owner's Equity", "Vốn chủ sở hữu"]),
        ("Total Debt", ["Total Debt", "Total interest bearing debt"]),
        ("Short-Term Debt", ["Short-Term Loans", "Short term loans"]),
        ("Long-Term Debt", ["Long-Term Loans", "Long term loans"]),
        ("Net Income", ["Net profit after tax", "Profit after tax", "Lợi nhuận sau thuế"]),
        ("EBIT", ["EBIT", "Operating profit"]),
    ]
    
    # Find available columns
    cols = []
    col_mapping = {}
    for display_name, candidates in core_metrics:
        found_col = _pickcol(show, candidates)
        if found_col:
            cols.append(found_col)
            col_mapping[found_col] = display_name
    
    if not cols:
        st.info("""
        📊 **No core financial metrics found.**
        
        Expected columns include:
        - Net Revenue / Revenue
        - Total Assets
        - Equity
        - Total Debt
        - Short-Term Loans
        - Long-Term Loans
        
        Please ensure your CSV contains these financial indicators.
        """)
        return
    
    # Prepare display dataframe
    display_df = show[[ycol] + cols].copy()
    
    # Rename columns for better display
    display_df = display_df.rename(columns={
        ycol: "Year",
        **col_mapping
    })
    
    # Sort by year
    try:
        display_df = display_df.sort_values("Year")
    except:
        pass
    
    # Calculate risk indicators if possible
    st.subheader("🎯 Key Risk Indicators")
    
    if len(display_df) > 0:
        latest = display_df.iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if "Total Debt" in display_df.columns and "Equity" in display_df.columns:
                try:
                    debt = float(latest["Total Debt"])
                    equity = float(latest["Equity"])
                    debt_to_equity = debt / equity if equity != 0 else 0
                    st.metric(
                        "Debt-to-Equity Ratio",
                        f"{debt_to_equity:.2f}",
                        help="Lower is better. <1 is generally healthy."
                    )
                except:
                    st.metric("Debt-to-Equity Ratio", "N/A")
            else:
                st.metric("Debt-to-Equity Ratio", "N/A")
        
        with col2:
            if "Total Debt" in display_df.columns and "Total Assets" in display_df.columns:
                try:
                    debt = float(latest["Total Debt"])
                    assets = float(latest["Total Assets"])
                    debt_ratio = debt / assets if assets != 0 else 0
                    st.metric(
                        "Debt Ratio",
                        f"{debt_ratio:.2%}",
                        help="Percentage of assets financed by debt."
                    )
                except:
                    st.metric("Debt Ratio", "N/A")
            else:
                st.metric("Debt Ratio", "N/A")
        
        with col3:
            if "Net Income" in display_df.columns and "Net Revenue" in display_df.columns:
                try:
                    net_income = float(latest["Net Income"])
                    revenue = float(latest["Net Revenue"])
                    margin = net_income / revenue if revenue != 0 else 0
                    st.metric(
                        "Net Profit Margin",
                        f"{margin:.2%}",
                        help="Profitability indicator."
                    )
                except:
                    st.metric("Net Profit Margin", "N/A")
            else:
                st.metric("Net Profit Margin", "N/A")
        
        with col4:
            if "Net Income" in display_df.columns and "Equity" in display_df.columns:
                try:
                    net_income = float(latest["Net Income"])
                    equity = float(latest["Equity"])
                    roe = net_income / equity if equity != 0 else 0
                    st.metric(
                        "ROE",
                        f"{roe:.2%}",
                        help="Return on Equity - efficiency of capital use."
                    )
                except:
                    st.metric("ROE", "N/A")
            else:
                st.metric("ROE", "N/A")
    
    st.markdown("---")
    
    # Trend visualization
    st.subheader("📊 Financial Trends")
    
    try:
        # Select numeric columns for visualization
        numeric_cols = []
        for col in display_df.columns:
            if col != "Year":
                if pd.api.types.is_numeric_dtype(display_df[col]):
                    numeric_cols.append(col)
        
        if numeric_cols:
            # Create subplots
            num_charts = min(len(numeric_cols), 4)
            fig = make_subplots(
                rows=2, 
                cols=2,
                subplot_titles=numeric_cols[:4],
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            positions = [(1,1), (1,2), (2,1), (2,2)]
            
            for i, col in enumerate(numeric_cols[:4]):
                row, col_pos = positions[i]
                
                y_data = pd.to_numeric(display_df[col], errors='coerce')
                
                fig.add_trace(
                    go.Scatter(
                        x=display_df["Year"],
                        y=y_data,
                        mode='lines+markers',
                        name=col,
                        line=dict(width=3),
                        marker=dict(size=10),
                        fill='tonexty' if i == 0 else None,
                    ),
                    row=row, col=col_pos
                )
            
            fig.update_layout(
                height=600,
                showlegend=False,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Unable to create trend visualization: {str(e)}")
    
    st.markdown("---")
    
    # Display full data table
    st.subheader("📋 Detailed Financial Summary")
    
    st.dataframe(
        display_df.set_index("Year"),
        use_container_width=True,
        height=400
    )
    
    # Additional risk assessment
    st.markdown("---")
    st.subheader("⚠️ Risk Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Liquidity Risk**")
        if "Short-Term Debt" in display_df.columns:
            st.info("Evaluate ability to meet short-term obligations.")
            # Add your liquidity analysis logic here
        else:
            st.warning("Short-term debt data not available.")
    
    with col2:
        st.markdown("**Solvency Risk**")
        if "Total Debt" in display_df.columns and "Total Assets" in display_df.columns:
            st.info("Evaluate long-term financial stability.")
            # Add your solvency analysis logic here
        else:
            st.warning("Solvency metrics not fully available.")
    
    # Download button
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Summary Report as CSV",
        data=csv,
        file_name=f"risk_summary.csv",
        mime="text/csv",
    )
