import numpy as np
import pandas as pd

def _psi(expected, actual, buckets=10):
    expected = pd.Series(expected).replace([np.inf, -np.inf], np.nan).dropna()
    actual = pd.Series(actual).replace([np.inf, -np.inf], np.nan).dropna()
    if expected.empty or actual.empty:
        return float("nan")
    q = np.unique(np.quantile(expected, np.linspace(0,1,buckets+1)))
    if len(q) < 3:
        return 0.0
    e_cnt, _ = np.histogram(expected, bins=q)
    a_cnt, _ = np.histogram(actual, bins=q)
    e_pct = np.where(e_cnt==0, 1e-6, e_cnt/e_cnt.sum())
    a_pct = np.where(a_cnt==0, 1e-6, a_cnt/a_cnt.sum())
    psi = np.sum((a_pct - e_pct) * np.log(a_pct / e_pct))
    return float(psi)

def compute_psi_table(train_df: pd.DataFrame, current_df: pd.DataFrame, features: list, buckets=10) -> pd.DataFrame:
    rows = []
    for f in features:
        if f in train_df.columns and f in current_df.columns:
            try:
                val = _psi(train_df[f], current_df[f], buckets=buckets)
            except Exception:
                val = float("nan")
            rows.append({"feature": f, "psi": val})
    out = pd.DataFrame(rows)
    out["status"] = out["psi"].apply(_status)
    out = out.sort_values("psi", ascending=False)
    return out

def _status(x):
    import pandas as pd
    if pd.isna(x): return "NA"
    if x < 0.1: return "Stable"
    if x < 0.25: return "Moderate"
    return "Shift"