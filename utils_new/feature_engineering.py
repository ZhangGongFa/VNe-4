import numpy as np
import pandas as pd

def safe_div(a, b):
    a = a.astype(float)
    b = b.astype(float)
    with np.errstate(divide='ignore', invalid='ignore'):
        out = np.where((b==0) | (~np.isfinite(b)), 0.0, a/b)
    return out

def preprocess_and_create_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['Total_Assets'] = df['TOTAL ASSETS (Bn. VND)']
    df['Equity'] = df["OWNER'S EQUITY(Bn.VND)"]
    df['Current_Liabilities'] = df['Current liabilities (Bn. VND)']
    df['Long_Term_Liabilities'] = df['Long-term liabilities (Bn. VND)']
    df['Short_Term_Borrowings'] = df['Short-term borrowings (Bn. VND)']
    df['Total_Debt'] = df['Current_Liabilities'] + df['Long_Term_Liabilities'] + df['Short_Term_Borrowings']

    df['Operating_Profit'] = df['Operating Profit/Loss']
    df['Net_Profit'] = df['Net Profit For the Year']
    df['Revenue'] = df['Net Sales']
    df['Gross_Profit'] = df['Gross Profit']
    df['Financial_Expenses'] = df['Financial Expenses']
    df['Interest_Expenses'] = df['Interest Expenses']
    df['Cash'] = df['Cash and cash equivalents (Bn. VND)']
    df['Receivables'] = df['Accounts receivable (Bn. VND)']
    df['Inventories'] = df['Net Inventories']
    df['Current_Assets'] = df['CURRENT ASSETS (Bn. VND)']
    df['OCF'] = df['Net cash inflows/outflows from operating activities']

    df = df.sort_values(['Ticker', 'Year']).reset_index(drop=True)
    df['is_loss'] = (df['Net_Profit'] <= 0).astype(int)

    def mark_consecutive_losses(group):
        years = group['Year'].values
        losses = group['is_loss'].values
        streak = [False] * len(group)
        for i in range(len(group) - 2):
            if losses[i] and losses[i+1] and losses[i+2] and                years[i+1] == years[i]+1 and years[i+2] == years[i]+2:
                streak[i] = streak[i+1] = streak[i+2] = True
        group['Loss_Streak3'] = streak
        return group

    df = df.groupby('Ticker', group_keys=False).apply(mark_consecutive_losses)
    default_years = df[df['Loss_Streak3']].groupby('Ticker')['Year'].min().rename("Default_Year")
    df = df.merge(default_years, on='Ticker', how='left')
    df['Years_Before_Default'] = df['Default_Year'] - df['Year']
    df['Will_Default_Within_5Y'] = ((df['Years_Before_Default'] >= 0) & (df['Years_Before_Default'] <= 5)).astype(int)
    df['Already_Defaulted'] = np.where(df['Default_Year'].notna(), (df['Year'] > df['Default_Year']).astype(int), 0)
    df.drop(columns=['Default'], errors='ignore', inplace=True)
    df['Default'] = df.groupby('Ticker')['Will_Default_Within_5Y'].transform('max')
    df.drop(columns=['is_loss', 'Loss_Streak3', 'Default_Year', 'Years_Before_Default'], inplace=True)

    # Ratios
    df['Current_Ratio'] = safe_div(df['Current_Assets'], df['Current_Liabilities'])
    df['Quick_Ratio'] = safe_div(df['Cash'] + df['Receivables'], df['Current_Liabilities'])
    df['Working_Capital_to_Total_Assets'] = safe_div(df['Current_Assets'] - df['Current_Liabilities'], df['Total_Assets'])

    df['Debt_to_Assets'] = safe_div(df['Total_Debt'], df['Total_Assets'])
    df['Debt_to_Equity'] = safe_div(df['Total_Debt'], df['Equity'])
    df['Equity_to_Liabilities'] = safe_div(df['Equity'], df['Total_Debt'])
    df['Long_Term_Debt_to_Assets'] = safe_div(df['Long_Term_Liabilities'], df['Total_Assets'])

    df['Receivables_Turnover'] = safe_div(df['Revenue'], df['Receivables'])
    df['Inventory_Turnover'] = safe_div(df.get('Cost of Sales', 0.0), df['Inventories'])
    df['Asset_Turnover'] = safe_div(df['Revenue'], df['Total_Assets'])

    df['ROA'] = safe_div(df['Net_Profit'], df['Total_Assets'])
    df['ROE'] = safe_div(df['Net_Profit'], df['Equity'])
    df['EBIT_to_Assets'] = safe_div(df['Operating_Profit'], df['Total_Assets'])
    df['Operating_Income_to_Debt'] = safe_div(df['Operating_Profit'], df['Total_Debt'])
    df['Net_Profit_Margin'] = safe_div(df['Net_Profit'], df['Revenue'])
    df['Gross_Margin'] = safe_div(df['Gross_Profit'], df['Revenue'])

    df['Interest_Coverage'] = safe_div(df['Operating_Profit'], df['Interest_Expenses'])

    if 'Depreciation and Amortisation' in df.columns:
        df['EBITDA'] = df['Operating_Profit'] + df['Depreciation and Amortisation']
    else:
        df['EBITDA'] = 0.0

    df['EBITDA_to_Interest'] = safe_div(df['EBITDA'], df['Interest_Expenses'])
    df['Total_Debt_to_EBITDA'] = safe_div(df['Total_Debt'], df['EBITDA'])
    df['Net_Debt'] = df['Total_Debt'] - df['Cash']
    df['Net_Debt_to_Equity'] = safe_div(df['Net_Debt'], df['Equity'])

    df['OCF_Negative'] = (df['OCF'] < 0).astype(int)
    df['OCF_Deficit_2of3'] = df.groupby('Ticker')['OCF_Negative'].transform(lambda x: x.rolling(3, min_periods=3).sum() >= 2).astype(int)
    df['Revenue_Growth'] = df.groupby('Ticker')['Revenue'].pct_change()
    df['Revenue_CAGR_3Y'] = df.groupby('Ticker')['Revenue_Growth'].transform(lambda x: x.rolling(3, min_periods=3).mean()).fillna(0)
    df['PAT_Std_3Y'] = df.groupby('Ticker')['Net_Profit'].transform(lambda x: x.rolling(3, min_periods=3).std()).fillna(0)

    df['LowRiskFlag'] = ((df['Debt_to_Assets'] < 0.5) & (df['ROA'] > 0.1) & (df['Current_Ratio'] > 1)).astype(int)

    if 'Sector' in df.columns:
        sector_default_rate_map = df[df['Already_Defaulted'] == 0].groupby('Sector')['Default'].mean()
        df['Sector_Default_Rate'] = df['Sector'].map(sector_default_rate_map).fillna(0)
    else:
        df['Sector_Default_Rate'] = 0

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.drop(columns=['OCF_Negative', 'Revenue_Growth'], inplace=True)
    df.fillna(0, inplace=True)

    return df

def default_financial_feature_list():
    return [
        'Current_Ratio', 'Quick_Ratio', 'Working_Capital_to_Total_Assets',
        'Debt_to_Assets', 'Debt_to_Equity', 'Equity_to_Liabilities',
        'Long_Term_Debt_to_Assets', 'Receivables_Turnover', 'Inventory_Turnover',
        'Asset_Turnover', 'ROA', 'ROE', 'EBIT_to_Assets',
        'Operating_Income_to_Debt', 'Net_Profit_Margin', 'Gross_Margin',
        'Interest_Coverage', 'EBITDA_to_Interest', 'Total_Debt_to_EBITDA',
        'Net_Debt_to_Equity', 'LowRiskFlag', 'OCF_Deficit_2of3',
        'Revenue_CAGR_3Y', 'PAT_Std_3Y', 'Sector_Default_Rate'
    ]