"""Calendar + temp + area. X matrix from a long frame."""
from . import const


def build(df, features=const.FEATURES):
    d = df.copy()
    d["hour"] = d.ts.dt.hour
    d["dow"] = d.ts.dt.dayofweek
    d["month"] = d.ts.dt.month
    d = d.dropna(subset=features)  # temp gaps drop the row; do not fill
    return d[features], d["kwh"].to_numpy(), d
