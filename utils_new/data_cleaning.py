import numpy as np
import pandas as pd

def clean_and_log_transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cols_to_keep = ['Year', 'Ticker', 'Sector', 'Exchange']
    df_keep = df[cols_to_keep].copy()

    for col in df.columns:
        if col not in cols_to_keep and df[col].dtype == 'object':
            try:
                df[col] = df[col].str.replace(',', '', regex=False).astype(float)
            except Exception:
                df[col] = np.nan

    for col in df.columns:
        if col not in cols_to_keep:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cols_to_transform = [c for c in numeric_cols if c not in cols_to_keep]
    df[cols_to_transform] = df[cols_to_transform].applymap(
        lambda x: np.log(x + 1) if pd.notnull(x) and x > 0 else np.nan
    )

    cols_check = [c for c in df.columns if c not in cols_to_keep]
    drop_cols = [c for c in cols_check if df[c].isna().all() or df[c].nunique(dropna=True) <= 1]
    if drop_cols:
        df.drop(columns=drop_cols, inplace=True)

    df = pd.concat([df_keep, df.drop(columns=cols_to_keep, errors='ignore')], axis=1)
    df.fillna(0, inplace=True)
    df.drop_duplicates(inplace=True)
    return df
