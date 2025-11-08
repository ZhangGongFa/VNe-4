import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def default_distribution_by_year(df: pd.DataFrame):
    summary_year_total = df.groupby(['Year', 'Default']).size().unstack(fill_value=0)
    summary_year_total.columns = ['No Default', 'Default']
    summary_year_total['Total'] = summary_year_total['No Default'] + summary_year_total['Default']
    summary_year_total['Default Rate (%)'] = (summary_year_total['Default'] / summary_year_total['Total'] * 100).round(2)
    summary_year_total = summary_year_total.reset_index().sort_values('Year', ascending=True)

    pie_data = df.groupby('Year')['Default'].value_counts().unstack(fill_value=0).stack()
    pie_data = pie_data.rename(index={0: 'No Default', 1: 'Default'}).reset_index(name='Count')

    pie_fig = px.pie(
        pie_data,
        names='Default',
        values='Count',
        title='Overall Default Distribution by Year',
        hole=0.3,
        template='plotly_white'
    )
    pie_fig.update_traces(textinfo='percent+label')

    bar_default_rate_year_total = px.bar(
        summary_year_total,
        x='Year',
        y='Default Rate (%)',
        text='Default Rate (%)',
        template='plotly_white',
        title='Default Rate by Year'
    )
    bar_default_rate_year_total.update_traces(texttemplate='%{text}%', textposition='outside')
    bar_default_rate_year_total.update_xaxes(showgrid=False)
    bar_default_rate_year_total.update_yaxes(showgrid=False)

    table_fig_year_total = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Year</b>', '<b>No Default</b>', '<b>Default</b>', '<b>Total</b>', '<b>Default Rate (%)</b>'],
            fill_color='lightblue', align='center', font=dict(color='black', size=12)
        ),
        cells=dict(
            values=[
                summary_year_total['Year'],
                summary_year_total['No Default'],
                summary_year_total['Default'],
                summary_year_total['Total'],
                summary_year_total['Default Rate (%)'].astype(str) + '%'
            ],
            fill_color='white', align='center', font=dict(color='black', size=12)
        )
    )])
    table_fig_year_total.update_layout(title='Summary Table: Default Statistics by Year', template='plotly_white')

    return pie_fig, bar_default_rate_year_total, table_fig_year_total

def default_distribution_by_sector(df: pd.DataFrame):
    summary = df.groupby(['Sector', 'Default']).size().unstack(fill_value=0)
    summary.columns = ['No Default', 'Default']
    summary['Total'] = summary['No Default'] + summary['Default']
    summary['Default Rate (%)'] = (summary['Default'] / summary['Total'] * 100).round(2)
    summary = summary.reset_index().sort_values('Default Rate (%)', ascending=False)

    bar_fig = go.Figure([
        go.Bar(name='No Default', x=summary['Sector'], y=summary['No Default']),
        go.Bar(name='Default', x=summary['Sector'], y=summary['Default'])
    ])
    bar_fig.update_layout(barmode='stack', title='Number of Companies by Default Status per Sector',
                          xaxis_title='Sector', yaxis_title='Number of Companies',
                          template='plotly_white', xaxis_tickangle=-40)
    bar_fig.update_xaxes(showgrid=False)
    bar_fig.update_yaxes(showgrid=False)

    default_counts = df['Default'].value_counts().rename(index={0: 'No Default', 1: 'Default'})
    pie_fig = px.pie(
        names=default_counts.index,
        values=default_counts.values,
        title='Overall Default Distribution',
        hole=0.3,
        template='plotly_white'
    )
    pie_fig.update_traces(textinfo='percent+label')

    bar_default_rate = px.bar(
        summary,
        x='Sector',
        y='Default Rate (%)',
        text='Default Rate (%)',
        template='plotly_white',
        title='Default Rate by Sector'
    )
    bar_default_rate.update_traces(texttemplate='%{text}%', textposition='outside')
    bar_default_rate.update_layout(xaxis_tickangle=-40)
    bar_default_rate.update_xaxes(showgrid=False)
    bar_default_rate.update_yaxes(showgrid=False)

    table_fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Sector</b>', '<b>No Default</b>', '<b>Default</b>', '<b>Total</b>', '<b>Default Rate (%)</b>'],
            fill_color='lightblue', align='center', font=dict(color='black', size=12)
        ),
        cells=dict(
            values=[
                summary['Sector'],
                summary['No Default'],
                summary['Default'],
                summary['Total'],
                summary['Default Rate (%)'].astype(str) + '%'
            ],
            fill_color='white', align='center', font=dict(color='black', size=12)
        )
    )])
    table_fig.update_layout(title='Summary Table: Default Statistics by Sector', template='plotly_white')

    return bar_fig, pie_fig, bar_default_rate, table_fig