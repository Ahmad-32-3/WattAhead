"""Slice 2: three feature sets on the SAME leave-one-building-out split. Keep the worse column too."""
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from . import features, eval as ev, split


def _ridge(train_df, test_df, feats):
    Xtr, ytr, _ = features.build(train_df, feats)
    Xte, yte, _ = features.build(test_df, feats)
    m = make_pipeline(StandardScaler(), Ridge()).fit(Xtr, ytr)
    return ev.rmse(yte, m.predict(Xte)), ev.cv_rmse(yte, m.predict(Xte))


def _how_mean(train_df, test_df):
    """No model: predict each test hour with the mean kWh of the OTHER buildings at that hour-of-week."""
    tr = train_df.copy()
    tr["how"] = tr.ts.dt.dayofweek * 24 + tr.ts.dt.hour
    table = tr.groupby("how").kwh.mean()
    te = test_df.dropna(subset=["kwh"]).copy()
    te["how"] = te.ts.dt.dayofweek * 24 + te.ts.dt.hour
    yhat = te.how.map(table).fillna(tr.kwh.mean()).to_numpy()
    y = te.kwh.to_numpy()
    return ev.rmse(y, yhat), ev.cv_rmse(y, yhat)


def table(df, test_id):
    """Same lobo split for every row. Returns {name: {rmse, cv_rmse}}."""
    tr, te = split.lobo(df, test_id)
    return {
        "weather+calendar+area": dict(zip(("rmse", "cv_rmse"), _ridge(tr, te, ["hour", "dow", "month", "temp_c", "sqm"]))),
        "area_only": dict(zip(("rmse", "cv_rmse"), _ridge(tr, te, ["sqm"]))),
        "hour_of_week_mean": dict(zip(("rmse", "cv_rmse"), _how_mean(tr, te))),
    }
