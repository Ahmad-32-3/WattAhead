"""Experiment harness: full 12-fold leave-one-building-out. Report hours-within-20% mean +/- std.

Levers, all lobo-clean (nothing from the held-out building enters training):
  - one-hot calendar (a linear model can't read raw hour 0..23 as a daily profile)
  - EUI target: predict kWh per m2, rescale by the held-out building's KNOWN sqm
  - hour-of-week mean from TRAIN buildings as a feature (DESIGN's allowed lag swap)
  - HistGradientBoosting for hour x temperature interactions Ridge can't reach
"""
import os
import sys
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingRegressor

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from bdg2 import io  # noqa: E402

TOL = 0.20


def _cal(df):
    d = df.copy()
    d["hour"] = d.ts.dt.hour
    d["dow"] = d.ts.dt.dayofweek
    d["month"] = d.ts.dt.month
    d["is_weekend"] = (d["dow"] >= 5).astype(int)
    return d


def _onehot(d):
    return pd.get_dummies(d[["hour", "dow", "month"]], columns=["hour", "dow", "month"]).astype(float)


def _how_mean_eui(train):
    """hour-of-week mean of EUI (kwh/sqm) over the training buildings. A shape prior for the held-out one."""
    t = train.copy()
    t["how"] = t.ts.dt.dayofweek * 24 + t.ts.dt.hour
    t["eui"] = t.kwh / t.sqm
    return t.groupby("how").eui.mean()


def hours_within(y, yhat, tol=TOL):
    return float(np.mean(np.abs((y - yhat) / y) <= tol) * 100)


def cv_rmse(y, yhat):
    return float(np.sqrt(np.mean((y - yhat) ** 2)) / np.mean(y))


def run_fold(df, test_id, model_kind):
    train = df[(df.building_id != test_id) & (df.year == 2016)]
    test = df[(df.building_id == test_id) & (df.year == 2017)]
    if len(test) == 0 or len(train) == 0:
        return None
    tr, te = _cal(train).dropna(subset=["temp_c"]), _cal(test).dropna(subset=["temp_c"])
    if len(tr) == 0 or len(te) == 0:
        return None

    how = _how_mean_eui(train)
    for d in (tr, te):
        d["how"] = d.ts.dt.dayofweek * 24 + d.ts.dt.hour
        d["how_eui"] = d["how"].map(how).fillna(how.mean())

    eui = model_kind.endswith("_eui")
    ytr = (tr.kwh / tr.sqm).to_numpy() if eui else tr.kwh.to_numpy()
    scale = te.sqm.to_numpy() if eui else 1.0

    if model_kind.startswith("ridge_onehot"):
        extra = ["temp_c", "how_eui"] + ([] if eui else ["sqm"])
        Xtr = pd.concat([_onehot(tr).reset_index(drop=True), tr[extra].reset_index(drop=True)], axis=1)
        Xte = pd.concat([_onehot(te).reset_index(drop=True), te[extra].reset_index(drop=True)], axis=1)
        Xte = Xte.reindex(columns=Xtr.columns, fill_value=0.0)
        m = make_pipeline(StandardScaler(with_mean=False), Ridge()).fit(Xtr, ytr)
        yhat = m.predict(Xte) * scale
    elif model_kind.startswith("gbm"):
        cols = ["hour", "dow", "month", "is_weekend", "temp_c", "how_eui"] + ([] if eui else ["sqm"])
        m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_depth=6).fit(tr[cols], ytr)
        yhat = m.predict(te[cols]) * scale
    else:
        raise ValueError(model_kind)

    y = te.kwh.to_numpy()
    return hours_within(y, yhat), cv_rmse(y, yhat)


def good_buildings(df, min_hours=8000, min_mean_kwh=5.0):
    """Objective data-quality gate: near-complete years and a live meter. Drops dead/partial meters."""
    keep = []
    for b in sorted(df.building_id.unique()):
        d16 = df[(df.building_id == b) & (df.year == 2016)]
        d17 = df[(df.building_id == b) & (df.year == 2017)]
        if len(d16) >= min_hours and len(d17) >= min_hours and d16.kwh.mean() >= min_mean_kwh and d17.kwh.mean() >= min_mean_kwh:
            keep.append(b)
    return keep


def warm_start(df, b, warmup_days=28):
    """Realistic deployment: anchor on the target's OWN first N days of 2017, forecast the rest of 2017.
    Profile = hour-of-week mean of the warm-up window. Test period is strictly after the window (held out in time).
    """
    d = _cal(df[(df.building_id == b) & (df.year == 2017)]).dropna(subset=["kwh"]).sort_values("ts")
    if len(d) < 8000:
        return None
    cutoff = d.ts.min() + pd.Timedelta(days=warmup_days)
    warm, test = d[d.ts < cutoff], d[d.ts >= cutoff]
    if len(warm) < 200 or len(test) == 0:
        return None
    warm = warm.assign(how=warm.ts.dt.dayofweek * 24 + warm.ts.dt.hour)
    prof = warm.groupby("how").kwh.mean()
    test = test.assign(how=test.ts.dt.dayofweek * 24 + test.ts.dt.hour)
    yhat = test["how"].map(prof).fillna(warm.kwh.mean()).to_numpy()
    y = test.kwh.to_numpy()
    # daily totals: aggregate predicted and actual by calendar day (smooths hourly noise)
    day = test.assign(yhat=yhat).groupby(test.ts.dt.date).agg(y=("kwh", "sum"), yhat=("yhat", "sum"))
    return hours_within(y, yhat), cv_rmse(y, yhat), hours_within(day.y.to_numpy(), day.yhat.to_numpy()), cv_rmse(day.y.to_numpy(), day.yhat.to_numpy())


def own_history(df, b):
    """You have a full prior year of this building. Train per-building on its 2016 (calendar + temp), forecast 2017."""
    tr = _cal(df[(df.building_id == b) & (df.year == 2016)]).dropna(subset=["kwh", "temp_c"])
    te = _cal(df[(df.building_id == b) & (df.year == 2017)]).dropna(subset=["kwh", "temp_c"])
    if len(tr) < 4000 or len(te) < 4000:
        return None
    cols = ["hour", "dow", "month", "is_weekend", "temp_c"]
    m = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, max_depth=6).fit(tr[cols], tr.kwh)
    yhat = m.predict(te[cols])
    y = te.kwh.to_numpy()
    day = te.assign(yhat=yhat).groupby(te.ts.dt.date).agg(y=("kwh", "sum"), yhat=("yhat", "sum"))
    return hours_within(y, yhat), cv_rmse(y, yhat), hours_within(day.y.to_numpy(), day.yhat.to_numpy()), cv_rmse(day.y.to_numpy(), day.yhat.to_numpy())


def main():
    df = io.load()
    folds = good_buildings(df)
    df = df[df.building_id.isin(folds)]  # dead/partial meters out of TRAIN too
    print(f"{len(folds)} clean held-out folds: {[b.split('_')[-1] for b in folds]}\n")
    print("A. NEVER-SEEN building (train on others, predict a new one):")
    for kind in ["ridge_onehot_raw", "ridge_onehot_eui", "gbm_eui"]:
        rows = [r for r in (run_fold(df, b, kind) for b in folds) if r]
        hw = np.array([r[0] for r in rows]); cv = np.array([r[1] for r in rows])
        print(f"  {kind:18s} hours<=20%: {hw.mean():5.1f}% +/- {hw.std():4.1f}   CV-RMSE: {cv.mean():.3f} +/- {cv.std():.3f}")
    print("\nB. WARM-START (anchor on target's own first 4 weeks of 2017, forecast the rest):")
    rows = [r for r in (warm_start(df, b) for b in folds) if r]
    hw = np.array([r[0] for r in rows]); cv = np.array([r[1] for r in rows])
    dw = np.array([r[2] for r in rows]); dcv = np.array([r[3] for r in rows])
    print(f"  {'hourly':18s} within 20%: {hw.mean():5.1f}% +/- {hw.std():4.1f}   CV-RMSE: {cv.mean():.3f} +/- {cv.std():.3f}")
    print(f"  {'daily total':18s} within 20%: {dw.mean():5.1f}% +/- {dw.std():4.1f}   CV-RMSE: {dcv.mean():.3f} +/- {dcv.std():.3f}")
    print("\nC. OWN HISTORY (full prior year of the target; GBM on calendar+temp; 2016 -> 2017):")
    rows = [r for r in (own_history(df, b) for b in folds) if r]
    hw = np.array([r[0] for r in rows]); cv = np.array([r[1] for r in rows])
    dw = np.array([r[2] for r in rows]); dcv = np.array([r[3] for r in rows])
    print(f"  {'hourly':18s} within 20%: {hw.mean():5.1f}% +/- {hw.std():4.1f}   CV-RMSE: {cv.mean():.3f} +/- {cv.std():.3f}")
    print(f"  {'daily total':18s} within 20%: {dw.mean():5.1f}% +/- {dw.std():4.1f}   CV-RMSE: {dcv.mean():.3f} +/- {dcv.std():.3f}")


if __name__ == "__main__":
    main()
