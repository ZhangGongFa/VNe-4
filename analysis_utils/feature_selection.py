"""Feature selection utilities for default modelling.

This module provides a simple helper to align candidate features
with those expected by the trained model.  If the model exposes
a ``feature_name_`` attribute, that list is used to intersect with
the dataset's columns.  Otherwise the supplied candidate list is
filtered to columns present in the DataFrame.
"""

import pandas as pd
from typing import List


def select_features_for_model(df: pd.DataFrame, candidate_features: List[str], model_feature_names: list = None) -> list:
    """Select the appropriate feature columns for inference.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing engineered features.
    candidate_features : list of str
        Pre‑determined list of candidate feature names.
    model_feature_names : list of str or None, optional
        If provided, this list is intersected with the DataFrame's
        columns; otherwise ``candidate_features`` are used.

    Returns
    -------
    list
        Ordered list of feature names to feed into the model.
    """
    if model_feature_names:
        inter = [f for f in model_feature_names if f in df.columns]
        if len(inter) > 0:
            return inter
    return [f for f in candidate_features if f in df.columns]