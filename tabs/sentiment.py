# tabs/sentiment.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render(fin_df: pd.DataFrame):
    """
    Render Sentiment Analysis tab.
    Displays news sentiment and market perception data.
    """
    st.header("📰 Sentiment Analysis")
    st.markdown("Analysis of news sentiment and market perception related to the selected stock.")
    
    if fin_df.empty:
        st.warning("No data available for sentiment analysis.")
        return
    
    # Find sentiment-related columns
    sentiment_keywords = ["sentiment", "tone", "news", "score", "positive", "negative", "neutral"]
    cand = [c for c in fin_df.columns if any(k in c.lower() for k in sentiment_keywords)]
    
    if not cand:
        st.info("📊 No sentiment columns found in the dataset.")
        st.markdown("""
        **Expected columns:**
        - Sentiment scores (positive/negative/neutral)
        - News tone indicators
        - Market sentiment metrics
        
        Please ensure your CSV file contains sentiment-related data columns.
        """)
        return
    
    # Prepare data
    if "display_year" in fin_df.columns:
        year_col = "display_year"
    elif "Year" in fin_df.columns:
        year_col = "Year"
    elif "year" in fin_df.columns:
        year_col = "year"
    else:
        st.error("No year column found in data.")
        return
    
    # Create view dataframe
    view_cols = [year_col] + cand
    view = fin_df[view_cols].drop_duplicates().copy()
    
    if view.empty:
        st.warning("No sentiment data available after processing.")
        return
    
    # Sort by year
    try:
        view = view.sort_values(year_col)
    except:
        pass
    
    # Display metrics in columns
    st.subheader("Sentiment Metrics Overview")
    
    # Show latest sentiment scores if available
    if len(view) > 0:
        latest_row = view.iloc[-1]
        cols = st.columns(min(len(cand), 4))
        
        for i, col_name in enumerate(cand[:4]):
            with cols[i]:
                try:
                    value = latest_row[col_name]
                    if pd.notna(value):
                        st.metric(
                            label=col_name.replace("_", " ").title(),
                            value=f"{float(value):.2f}" if isinstance(value, (int, float)) else str(value)
                        )
                    else:
                        st.metric(label=col_name.replace("_", " ").title(), value="N/A")
                except:
                    st.metric(label=col_name.replace("_", " ").title(), value="—")
    
    st.markdown("---")
    
    # Visualize sentiment trends
    st.subheader("Sentiment Trends Over Time")
    
    try:
        # Create plotly chart
        fig = make_subplots(
            rows=min(len(cand), 3), 
            cols=1,
            subplot_titles=[c.replace("_", " ").title() for c in cand[:3]],
            vertical_spacing=0.1
        )
        
        for i, col_name in enumerate(cand[:3], 1):
            # Convert to numeric if possible
            y_data = pd.to_numeric(view[col_name], errors='coerce')
            
            fig.add_trace(
                go.Scatter(
                    x=view[year_col],
                    y=y_data,
                    mode='lines+markers',
                    name=col_name.replace("_", " ").title(),
                    line=dict(width=3),
                    marker=dict(size=8)
                ),
                row=i, col=1
            )
        
        fig.update_layout(
            height=300 * min(len(cand), 3),
            showlegend=False,
            hovermode='x unified'
        )
        
        fig.update_xaxes(title_text="Year", row=min(len(cand), 3), col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Unable to create visualization: {str(e)}")
    
    st.markdown("---")
    
    # Display full data table
    st.subheader("Detailed Sentiment Data")
    
    # Rename columns for better display
    display_view = view.copy()
    display_view = display_view.rename(columns={
        year_col: "Year",
        **{c: c.replace("_", " ").title() for c in cand}
    })
    
    st.dataframe(
        display_view.set_index("Year"),
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = display_view.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Sentiment Data as CSV",
        data=csv,
        file_name=f"sentiment_analysis.csv",
        mime="text/csv",
    )
