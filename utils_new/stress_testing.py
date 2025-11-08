from __future__ import annotations
import numpy as np
import pandas as pd

def align_features_to_model(X_df: pd.DataFrame, model):
    """Ensure X_df has the exact same columns (and order) as the model was trained on."""
    model_features = model.feature_name_

    # Tạo DataFrame mới với đầy đủ các cột của mô hình, điền 0 cho cột thiếu
    for col in model_features:
        if col not in X_df.columns:
            X_df[col] = 0

    # Loại bỏ các cột thừa không có trong model
    X_df = X_df[model_features]

    return X_df

# ---------- Sector mapping ----------
def detect_sector_alias(sector_raw: str) -> str:
    s = (sector_raw or "").lower()
    if any(k in s for k in ["tech", "information", "software", "it"]): return "Technology"
    if "tele" in s: return "Telecom"
    if any(k in s for k in ["material", "metal", "mining", "cement"]): return "Materials"
    if any(k in s for k in ["energy", "oil", "gas", "coal"]): return "Energy"
    if any(k in s for k in ["bank", "finance", "insurance", "securities"]): return "Financials"
    if any(k in s for k in ["real estate", "property", "construction"]): return "Real Estate"
    if any(k in s for k in ["industrial", "manufacturing", "machinery"]): return "Industrials"
    if any(k in s for k in ["consumer", "retail", "food", "beverage"]): return "Consumer"
    if any(k in s for k in ["utilit"]): return "Utilities"
    return "__default__"

def exchange_intensity(exchange: str) -> float:
    # UPCoM nuance: often low-observed default but weak fundamentals -> tone down deterministic sector shocks
    x = (exchange or "").upper()
    return {"UPCOM": 0.6, "HNX": 1.0, "HOSE": 1.0}.get(x, 1.0)

# ---------- Sector-specific deterministic shocks (multiplicative) ----------
# Multiplier <1.0 => decrease (e.g., ROA * 0.7). Multiplier >1.0 => increase (e.g., Debt_to_Assets * 1.3)
SECTOR_CRISIS_SPEC = {
    "Technology":   {"ROA": 0.70, "ROE": 0.70, "Revenue_CAGR_3Y": 0.70, "EBITDA_to_Interest": 0.70},
    "Telecom":      {"ROA": 0.75, "EBITDA_to_Interest": 0.70, "Revenue_CAGR_3Y": 0.75},
    "Materials":    {"Net_Profit_Margin": 0.75, "ROA": 0.75, "Debt_to_Assets": 1.15},
    "Energy":       {"Net_Profit_Margin": 0.75, "ROE": 0.75, "Debt_to_Assets": 1.15},
    "Financials":   {"ROE": 0.60, "Interest_Coverage": 0.70, "Current_Ratio": 0.85},
    "Real Estate":  {"Debt_to_Assets": 1.30, "Current_Ratio": 0.80, "Quick_Ratio": 0.80, "EBITDA_to_Interest": 0.70},
    "Industrials":  {"Asset_Turnover": 0.75, "EBITDA_to_Interest": 0.75, "ROA": 0.80},
    "Consumer":     {"Net_Profit_Margin": 0.75, "Revenue_CAGR_3Y": 0.80, "Debt_to_Equity": 1.10},
    "Utilities":    {"EBITDA_to_Interest": 0.75, "ROA": 0.85},
    "__default__":  {"ROA": 0.80, "EBITDA_to_Interest": 0.80, "Revenue_CAGR_3Y": 0.85},
}

def apply_sector_crisis_row(X_row: pd.DataFrame, sector_alias: str, exch_intensity: float = 1.0) -> pd.DataFrame:
    """
    Apply deterministic, sector-specific crisis multipliers on a 1xN feature row.
    Intensity is scaled by listing exchange (e.g., UPCoM -> 0.6).
    """
    assert X_row.shape[0] == 1, "X_row must be a single-row DataFrame."
    spec = SECTOR_CRISIS_SPEC.get(sector_alias, SECTOR_CRISIS_SPEC["__default__"])
    Xs = X_row.copy()
    for f, mult in spec.items():
        if f in Xs.columns:
            Xs[f] = float(Xs[f].iloc[0]) * (mult * exch_intensity)
    return Xs

# ---------- Systemic shock (σ-based, common to all sectors) ----------
RISK_UP_FEATURES = {
    "Debt_to_Assets", "Debt_to_Equity", "Total_Debt_to_EBITDA",
    "Net_Debt_to_Equity", "Long_Term_Debt_to_Assets"
}
RISK_DOWN_FEATURES = {
    "ROA", "ROE", "Current_Ratio", "Quick_Ratio",
    "Interest_Coverage", "EBITDA_to_Interest", "Operating_Income_to_Debt"
}

def systemic_sigma(sector_alias: str) -> float:
    # Slightly stronger for Financials & Real Estate
    return 2.0 if sector_alias in {"Financials", "Real Estate"} else 1.8

def _feature_stats(df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    valid = [f for f in features if f in df.columns]
    sub = df[valid].replace([np.inf, -np.inf], np.nan)
    stats = pd.DataFrame({"mean": sub.mean(skipna=True), "std": sub.std(ddof=0, skipna=True)})
    stats["std"] = stats["std"].replace(0, np.nan)
    return stats

def apply_systemic_shock_row(X_row: pd.DataFrame, reference_df: pd.DataFrame, k_sigma: float = 1.8) -> pd.DataFrame:
    """
    Add +kσ to risk-up features and -kσ to risk-down features, using reference_df stdev.
    """
    assert X_row.shape[0] == 1
    feats = list(X_row.columns)
    stats = _feature_stats(reference_df, feats)
    Xs = X_row.copy()
    for f in feats:
        if f not in stats.index: 
            continue
        s = stats.loc[f, "std"]
        if not np.isfinite(s) or s == 0: 
            continue
        v = float(Xs[f].iloc[0])
        if f in RISK_UP_FEATURES:
            Xs[f] = v + k_sigma * float(s)
        elif f in RISK_DOWN_FEATURES:
            Xs[f] = v - k_sigma * float(s)
    return Xs

# ---------- Monte Carlo CVaR (correlated, clipped) ----------
def _shrink_cov(cov: np.ndarray, alpha: float = 0.1) -> np.ndarray:
    # Ledoit-Wolf style diagonal shrinkage
    d = np.diag(np.diag(cov))
    shrunk = (1 - alpha) * cov + alpha * d
    # ensure PSD
    eps = 1e-6
    eig_min = np.min(np.linalg.eigvalsh(shrunk))
    if eig_min < eps:
        shrunk += (eps - eig_min) * np.eye(shrunk.shape[0])
    return shrunk

def reference_stats(reference_df: pd.DataFrame, features: list[str]) -> tuple[np.ndarray, np.ndarray, list[str]]:
    cols = [f for f in features if f in reference_df.columns]
    ref = reference_df[cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    mu = ref.mean(axis=0).values.astype(float)
    cov = np.cov(ref.values.T)
    cov = _shrink_cov(cov, alpha=0.15)
    return mu, cov, cols

def monte_carlo_cvar_pd(model, X_row: pd.DataFrame, reference_df: pd.DataFrame,
                        sims: int = 5000, alpha: float = 0.95,
                        clip_q: tuple[float, float] = (0.01, 0.99)) -> dict:
    """
    Correlated Monte Carlo around the selected company's point, using market covariance (shrunk).
    Returns dict with PD_sims, VaR, CVaR.
    """
    assert X_row.shape[0] == 1
    features = list(X_row.columns)
    mu, cov, cols = reference_stats(reference_df, features)

    # Align vectors in the same order
    base_vec = X_row[cols].values.reshape(1, -1).astype(float)[0]
    # Draw multivariate normal (correlated)
    sims_mat = np.random.multivariate_normal(mean=base_vec, cov=cov, size=sims)

    # Clip each feature to [q1, q99] of reference to avoid unrealistic tails
    q_low = reference_df[cols].quantile(clip_q[0], numeric_only=True).values
    q_high = reference_df[cols].quantile(clip_q[1], numeric_only=True).values
    sims_mat = np.minimum(np.maximum(sims_mat, q_low), q_high)

    # Predict PD in batch
    X = pd.DataFrame(sims_mat, columns=cols).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if hasattr(model, "predict_proba"):
        pd_sims = model.predict_proba(X)[:, 1]
    else:
        pd_sims = model.predict(X).astype(float)

    var = float(np.quantile(pd_sims, alpha))
    cvar = float(pd_sims[pd_sims >= var].mean()) if (pd_sims >= var).any() else var
    return {"PD_sims": pd_sims, "VaR": var, "CVaR": cvar}
