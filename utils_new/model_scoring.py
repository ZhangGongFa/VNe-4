import numpy as np
import pandas as pd
import joblib
# Attempt to import shap for SHAP value computation.  If not available,
# fall back gracefully when computing per‑feature contributions.
try:
    import shap  # type: ignore
except Exception:
    shap = None  # type: ignore

def load_lgbm_model(model_path: str):
    """Load a LightGBM model from the specified file path.

    Parameters
    ----------
    model_path : str
        Path to a pickled LightGBM model (.pkl).

    Returns
    -------
    model
        The loaded LightGBM model instance.
    """
    return joblib.load(model_path)

def model_feature_names(model) -> list[str] | None:
    """Extract the feature names from a LightGBM model.

    Supports both wrapper classes (e.g., ``LGBMClassifier``) and raw
    Booster objects.  If feature names cannot be determined, returns
    ``None``.

    Parameters
    ----------
    model
        The trained LightGBM model.

    Returns
    -------
    list[str] | None
        List of feature names or ``None`` if unavailable.
    """
    try:
        if hasattr(model, 'feature_name_') and model.feature_name_:
            return list(model.feature_name_)
        booster = getattr(model, 'booster_', None)
        if booster is not None:
            return list(booster.feature_name())
    except Exception:
        pass
    return None

def predict_pd(model, X_df: pd.DataFrame) -> float:
    """Predict the probability of default for a single observation.

    Handles both classification models exposing ``predict_proba`` and
    regressors returning raw predictions.  Only the first row of
    ``X_df`` is used.

    Parameters
    ----------
    model
        The trained model.
    X_df : pd.DataFrame
        DataFrame with at least one row of features aligned with the model.

    Returns
    -------
    float
        The predicted PD.
    """
    # Ensure a single-row DataFrame
    if X_df.shape[0] != 1:
        X_df = X_df.iloc[[0]]
    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(X_df)[:, 1]
    else:
        preds = model.predict(X_df)
        proba = np.array(preds, dtype=float)
    return float(proba[0])

def explain_shap(model, X_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Compute per‑feature SHAP or contribution values for an observation.

    Attempts to compute SHAP values via the ``shap`` library; if not
    available, falls back to LightGBM's ``pred_contrib`` output.  The
    returned DataFrame contains columns ``feature``, ``value``,
    ``shap`` and ``abs_shap``, sorted by absolute value.  Only the
    top ``top_n`` features are returned.

    Parameters
    ----------
    model
        Trained LightGBM model or Booster.
    X_df : pd.DataFrame
        DataFrame with one row of input features.
    top_n : int, default 10
        Number of top features to return.  Use ``None`` to return all.

    Returns
    -------
    pd.DataFrame
        DataFrame of per‑feature contributions.
    """
    import pandas as _pd
    # Ensure a single-row DataFrame
    if X_df.shape[0] != 1:
        X_df = X_df.iloc[[0]]
    contributions = None
    # Use shap if available
    if shap is not None:
        try:
            explainer = shap.TreeExplainer(model)  # type: ignore
            sv = explainer(X_df)
            vals = sv.values
            if isinstance(vals, list):
                vals = vals[-1]
            contributions = vals[0]
        except Exception:
            contributions = None
    # Fallback using LightGBM pred_contrib
    if contributions is None:
        try:
            booster = getattr(model, 'booster_', None) or model
            contrib = booster.predict(X_df, pred_contrib=True)
            # The last element is the bias term; drop it
            contributions = contrib[0][:-1]
        except Exception:
            contributions = None
    if contributions is None:
        return _pd.DataFrame(columns=["feature", "value", "shap", "abs_shap"])
    values = X_df.iloc[0].values
    cols = X_df.columns
    abs_vals = np.abs(contributions)
    df = _pd.DataFrame({
        "feature": cols,
        "value": values,
        "shap": contributions,
        "abs_shap": abs_vals
    })
    df = df.sort_values("abs_shap", ascending=False)
    if top_n is not None and top_n > 0:
        df = df.head(top_n)
    return df

def run_stress_test(model, base_row: pd.Series, features: list, shocks: dict) -> pd.DataFrame:
    base_df = pd.DataFrame([base_row[features].values], columns=features).replace([np.inf,-np.inf], 0.0).fillna(0.0)
    base_pd = predict_pd(model, base_df)
    rows = [{"Scenario":"Base", "PD": base_pd, **{k: float(base_row.get(k, 0.0)) for k in features}}]
    for feat, pct in shocks.items():
        sim = base_df.copy()
        if feat in sim.columns:
            sim.loc[:, feat] = sim[feat] * (1.0 + pct)
        sim_pd = predict_pd(model, sim)
        rows.append({"Scenario": f"{feat} {pct:+.0%}", "PD": sim_pd, **{k: float(sim.iloc[0][k]) for k in features}})
    out = pd.DataFrame(rows)
    out["Delta_PD"] = out["PD"] - out.loc[out["Scenario"]=="Base","PD"].values[0]
    return out

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
