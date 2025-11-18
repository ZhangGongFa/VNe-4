import numpy as np
import pandas as pd
import joblib
import shap

def load_lgbm_model(model_path: str):
    model = joblib.load(model_path)
    return model

def model_feature_names(model):
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
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_df)[:, 1]
    else:
        preds = model.predict(X_df)
        proba = np.array(preds).astype(float)
    return float(proba[0])

def explain_shap(model, X_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
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
        return pd.DataFrame(columns=["feature","value","shap","abs_shap"])

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
