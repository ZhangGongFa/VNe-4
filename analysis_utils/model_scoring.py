"""Model loading and scoring utilities.

This module contains helpers to load the LightGBM model used to
predict default probability, extract the names of the trained
features, compute predicted probabilities for given rows of data,
explain predictions via SHAP values, run simple stress tests by
perturbing individual features, and ensure that feature matrices
align with the model's expected column order.
"""

import numpy as np
import pandas as pd
import joblib
import shap


def load_lgbm_model(model_path: str):
    """Load a LightGBM model from a pickle file.

    Parameters
    ----------
    model_path : str
        Path to a joblib/pickle file storing the model.

    Returns
    -------
    Any
        A scikit‑learn compatible model object.
    """
    model = joblib.load(model_path)
    return model


def model_feature_names(model):
    """Return the list of feature names used by the model.

    The function attempts to access either the ``feature_name_``
    attribute on the model itself or the ``booster_``.  If neither
    provides names a ``None`` value is returned.
    """
    names = None
    try:
        if hasattr(model, 'feature_name_') and model.feature_name_:
            names = list(model.feature_name_)
        elif hasattr(model, 'booster_'):
            names = list(model.booster_.feature_name())
    except Exception:
        names = None
    return names


def predict_pd(model, X_df: pd.DataFrame) -> float:
    """Predict the probability of default for a single row.

    Parameters
    ----------
    model : object
        A trained classifier supporting ``predict_proba`` or ``predict``.
    X_df : pandas.DataFrame
        A feature DataFrame with exactly one row.

    Returns
    -------
    float
        The predicted default probability.
    """
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_df)[:, 1]
    else:
        preds = model.predict(X_df)
        proba = np.array(preds).astype(float)
    return float(proba[0])


def explain_shap(model, X_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Explain a prediction using SHAP values.

    Parameters
    ----------
    model : object
        A trained LightGBM model.
    X_df : pandas.DataFrame
        Feature DataFrame for which to explain the prediction.
    top_n : int, optional
        Number of features to return, sorted by absolute SHAP value.

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns ``feature``, ``value``, ``shap`` and
        ``abs_shap`` containing the top contributing features.
    """
    try:
        explainer = shap.TreeExplainer(model)
        sv = explainer(X_df)
        vals = sv.values
        if isinstance(vals, list):
            vals = vals[-1]
        abs_vals = np.abs(vals[0])
        out = pd.DataFrame({
            "feature": X_df.columns,
            "value": X_df.iloc[0].values,
            "shap": vals[0],
            "abs_shap": abs_vals
        }).sort_values("abs_shap", ascending=False).head(top_n)
        return out
    except Exception:
        return pd.DataFrame(columns=["feature", "value", "shap", "abs_shap"])


def run_stress_test(model, base_row: pd.Series, features: list, shocks: dict) -> pd.DataFrame:
    """Perform a simple stress test by shocking individual features.

    Starting from a baseline row, apply multiplicative shocks to
    specified features and compute the resulting PD.  Returns a DataFrame
    summarising the base and shocked scenarios.

    Parameters
    ----------
    model : object
        The trained LightGBM model.
    base_row : pandas.Series
        A row of engineered features representing the baseline.
    features : list of str
        Names of features to include in the stress test.
    shocks : dict
        Mapping of feature names to shock multipliers (e.g., {"ROA": 0.1}).

    Returns
    -------
    pandas.DataFrame
        Scenarios with PD values and feature levels.
    """
    base_df = pd.DataFrame([base_row[features].values], columns=features).replace([np.inf, -np.inf], 0.0).fillna(0.0)
    base_pd = predict_pd(model, base_df)
    rows = [{"Scenario": "Base", "PD": base_pd, **{k: float(base_row.get(k, 0.0)) for k in features}}]
    for feat, pct in shocks.items():
        sim = base_df.copy()
        if feat in sim.columns:
            sim.loc[:, feat] = sim[feat] * (1.0 + pct)
        sim_pd = predict_pd(model, sim)
        rows.append({"Scenario": f"{feat} {pct:+.0%}", "PD": sim_pd, **{k: float(sim.iloc[0][k]) for k in features}})
    out = pd.DataFrame(rows)
    out["Delta_PD"] = out["PD"] - out.loc[out["Scenario"] == "Base", "PD"].values[0]
    return out


def align_features_to_model(X_df: pd.DataFrame, model):
    """Ensure that a feature DataFrame has the same columns as the model.

    Missing columns are added with zeros and extra columns are removed.
    Column order is aligned to match the model's feature order.
    """
    model_features = getattr(model, 'feature_name_', None)
    if model_features is None:
        # If the model does not expose feature names, return the input as is
        return X_df.copy()
    X = X_df.copy()
    # Add missing columns
    for col in model_features:
        if col not in X.columns:
            X[col] = 0
    # Drop extra columns
    X = X[model_features]
    return X