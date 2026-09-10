"""Operational day-ahead forecast: a DIFFERENT question from leave-one-building-out.

Cold-start (the thesis) asks: forecast a building you have never metered. It can't, honestly (~18%).
This asks the everyday operational question: you run this building and have its meter history, so
forecast the next day. Features are strictly PAST readings of the same building (lag 24h/168h + a
weekly-profile roll), which in real day-ahead operation you always have. No leakage: every lag is >=24h old.

Success rate = share of hourly forecasts within +/-20% of actual, per building, then averaged (with std).
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

DAY_AHEAD = ["lag_24h", "lag_168h", "roll168_mean", "hour", "dow", "month", "is_weekend", "temp_c"]
NEXT_HOUR = ["lag_1h"] + DAY_AHEAD  # last reading is available when forecasting the next hour
TOL = 0.20
MIN_MEAN_KWH = 5.0  # data-quality gate: drop dead/near-zero meters (percentage error is meaningless there)


def _prep(g):
    """Per-building frame -> lagged features. g must be one building, sorted by ts, hourly."""
    g = g.sort_values("ts").copy()
    g["hour"] = g.ts.dt.hour
    g["dow"] = g.ts.dt.dayofweek
    g["month"] = g.ts.dt.month
    g["is_weekend"] = (g["dow"] >= 5).astype(int)
    g["lag_1h"] = g["kwh"].shift(1)        # last reading (available for next-hour forecasting)
    g["lag_24h"] = g["kwh"].shift(24)      # same hour yesterday (available day-ahead)
    g["lag_168h"] = g["kwh"].shift(168)    # same hour last week
    g["roll168_mean"] = g["kwh"].shift(24).rolling(168, min_periods=48).mean()  # recent weekly level
    return g


def within(y, yhat, tol=TOL):
    return float(np.mean(np.abs((y - yhat) / y) <= tol) * 100)


def cv_rmse(y, yhat):
    return float(np.sqrt(np.mean((y - yhat) ** 2)) / np.mean(y))


def forecast_building(df, b, feats=NEXT_HOUR):
    """Train on the building's 2016, forecast its 2017. Returns per-building metrics or None."""
    g = _prep(df[df.building_id == b])
    g = g.dropna(subset=feats + ["kwh"])
    g = g[g.kwh > 0]
    tr, te = g[g.year == 2016], g[g.year == 2017]
    if len(tr) < 2000 or len(te) < 2000 or tr.kwh.mean() < MIN_MEAN_KWH:
        return None
    m = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, max_depth=6).fit(tr[feats], tr.kwh)
    yhat = np.clip(m.predict(te[feats]), 0, None)
    y = te.kwh.to_numpy()
    persistence = te["lag_1h"].to_numpy() if "lag_1h" in feats else te["lag_24h"].to_numpy()
    return {"building_id": b, "within20": within(y, yhat), "cv_rmse": cv_rmse(y, yhat),
            "persistence_within20": within(y, persistence), "n": int(len(y))}


def evaluate(df, buildings, feats=NEXT_HOUR):
    rows = [r for r in (forecast_building(df, b, feats) for b in buildings) if r]
    w = np.array([r["within20"] for r in rows])
    cv = np.array([r["cv_rmse"] for r in rows])
    pw = np.array([r["persistence_within20"] for r in rows])
    return rows, {
        "within20_mean": round(float(w.mean()), 1),
        "within20_std": round(float(w.std()), 1),
        "within20_min": round(float(w.min()), 1),
        "cv_rmse_mean": round(float(cv.mean()), 3),
        "cv_rmse_std": round(float(cv.std()), 3),
        "persistence_within20_mean": round(float(pw.mean()), 1),
        "n_buildings": len(rows),
    }


if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from bdg2 import io
    df = io.load()
    buildings = sorted(df.building_id.unique())
    rows, agg = evaluate(df, buildings)
    for r in sorted(rows, key=lambda r: -r["within20"]):
        print(f"  {r['building_id']:26s} within20={r['within20']:5.1f}%  CV-RMSE={r['cv_rmse']:.3f}")
    print(f"\nDAY-AHEAD operational: within +/-20% = {agg['within20_mean']}% +/- {agg['within20_std']} "
          f"(min {agg['within20_min']}%)   CV-RMSE {agg['cv_rmse_mean']} +/- {agg['cv_rmse_std']}   n={agg['n_buildings']}")
