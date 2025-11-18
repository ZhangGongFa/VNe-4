import numpy as np
import pandas as pd
import joblib
# Attempt to import shap for SHAP value computation.  If the module
# isn't available, we set ``shap`` to None and rely on LightGBM's
# pred_contrib fallback for per‑feature contributions.  Importing
# ``shap`` may fail in environments where the library isn't installed.
try:
    import shap  # type: ignore
except Exception:
    shap = None  # type: ignore

def load_lgbm_model(model_path: str):
    """Load a LightGBM model from disk.

    Parameters
    ----------
    model_path : str
        Path to the pickled LightGBM model.

    Returns
    -------
    model
        The loaded model instance.
    """
    return joblib.load(model_path)

def model_feature_names(model) -> list[str] | None:
    """Return the feature names from a LightGBM model.

    Supports both the sklearn wrappers (e.g., ``LGBMClassifier``) and
    raw Booster objects.  If names cannot be determined, returns
    ``None``.

    Parameters
    ----------
    model
        The trained LightGBM model.

    Returns
    -------
    list[str] | None
        A list of feature names or ``None`` if unavailable.
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

    This helper handles both classifiers exposing ``predict_proba`` and
    regressors returning raw predictions.  Only the first row of
    ``X_df`` is used.

    Parameters
    ----------
    model
        The trained model.
    X_df : pd.DataFrame
        A DataFrame containing at least one row aligned with the
        model's expected feature order.

    Returns
    -------
    float
        The predicted PD for the observation.
    """
    # Use only the first row
    if X_df.shape[0] != 1:
        X_df = X_df.iloc[[0]]
    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(X_df)[:, 1]
    else:
        preds = model.predict(X_df)
        proba = np.array(preds, dtype=float)
    return float(proba[0])

def explain_shap(model, X_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Compute SHAP or per‑feature contribution values for an observation.

    Attempts to compute SHAP values using the ``shap`` library.  If
    unavailable or failing, falls back to LightGBM's ``pred_contrib``
    mechanism, which returns per‑feature contributions.  Returns a
    DataFrame with columns ``feature``, ``value``, ``shap`` and
    ``abs_shap`` sorted by absolute contribution.

    Parameters
    ----------
    model
        Trained LightGBM model or Booster.
    X_df : pd.DataFrame
        DataFrame with one row of input features aligned to the model.
    top_n : int, default 10
        Number of top features to return.  Use ``None`` to return all.

    Returns
    -------
    pd.DataFrame
        DataFrame of feature contributions.
    """
    import pandas as _pd
    # Ensure single-row input
    if X_df.shape[0] != 1:
        X_df = X_df.iloc[[0]]
    contributions = None
    # Try using shap values if shap module available
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
            # Drop the bias term (last element)
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
    """Run stress scenarios by applying proportional shocks to features.

    For each feature in ``shocks``, the corresponding value in
    ``base_row`` is multiplied by ``1 + pct`` and the PD is recomputed.
    Returns a DataFrame including the base scenario, shocked
    scenarios and the delta PD relative to base.

    Parameters
    ----------
    model
        The trained model.
    base_row : pd.Series
        Original observation containing feature values.
    features : list
        List of feature names to include.
    shocks : dict
        Mapping from feature name to a fractional shock (e.g., 0.1 for +10%).

    Returns
    -------
    pd.DataFrame
        DataFrame with scenario names, PDs and deltas.
    """
    base_df = pd.DataFrame([base_row[features].values], columns=features)
    base_df = base_df.replace([np.inf, -np.inf], 0.0).fillna(0.0)
    base_pd = predict_pd(model, base_df)
    rows: list[dict] = [{"Scenario": "Base", "PD": base_pd, **{k: float(base_row.get(k, 0.0)) for k in features}}]
    for feat, pct in shocks.items():
        sim = base_df.copy()
        if feat in sim.columns:
            sim.loc[:, feat] = sim[feat] * (1.0 + pct)
        sim_pd = predict_pd(model, sim)
        rows.append({"Scenario": f"{feat} {pct:+.0%}", "PD": sim_pd, **{k: float(sim.iloc[0][k]) for k in features}})
    out = pd.DataFrame(rows)
    out["Delta_PD"] = out["PD"] - out.loc[out["Scenario"] == "Base", "PD"].values[0]
    return out

def align_features_to_model(X_df: pd.DataFrame, model) -> pd.DataFrame:
    """Align a DataFrame's columns to match the model's feature order.

    Adds missing columns with zeros, removes extra columns, and reorders
    the DataFrame so that the columns match exactly the order of the
    model's feature names.  Returns a new DataFrame; does not modify
    the input.

    Parameters
    ----------
    X_df : pd.DataFrame
        Input DataFrame containing feature values.
    model
        The trained LightGBM model.

    Returns
    -------
    pd.DataFrame
        A DataFrame aligned to the model's expected input format.
    """
    feat_names = model_feature_names(model)
    if not feat_names:
        return X_df.copy()
    aligned = X_df.copy()
    for c in feat_names:
        if c not in aligned.columns:
            aligned[c] = 0.0
    # Drop columns not in feat_names and reorder
    aligned = aligned[feat_names]
    return aligned
