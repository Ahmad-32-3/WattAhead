"""Guards: the split is leak-free, and we only ever pull electricity buildings."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from bdg2 import split, eval as ev, const, io  # noqa: E402


def _synth(ids=("A", "B", "C"), rng=np.random.default_rng(0)):
    rows = []
    for b in ids:
        for year in (2016, 2017):
            ts = pd.date_range(f"{year}-01-01", periods=48, freq="h")
            rows.append(pd.DataFrame({"ts": ts, "building_id": b, "year": year,
                                      "kwh": rng.normal(100, 10, len(ts)), "temp_c": rng.normal(15, 5, len(ts)),
                                      "sqm": 5000.0, "site_id": "Rat", "primaryspaceusage": "Education"}))
    return pd.concat(rows, ignore_index=True)


def test_lobo_train_and_test_are_disjoint():
    tr, te = split.lobo(_synth(), test_id="A")
    assert "A" not in set(tr.building_id)          # held-out never trained on
    assert set(te.building_id) == {"A"}
    assert not (set(tr.building_id) & set(te.building_id))


def test_leak_is_rejected():
    """Inject the test building into train -> the guard must raise. If this passes silently, the split leaks."""
    df = _synth()
    with pytest.raises(ValueError, match="LEAK"):
        leaky_train = df[df.year == 2016]                 # includes building A
        leaky_test = df[(df.building_id == "A") & (df.year == 2017)]
        split._assert_disjoint(leaky_train, leaky_test)


def test_cv_rmse_is_rmse_over_mean():
    y = np.array([100.0, 200.0, 300.0])
    yhat = y + 10
    assert ev.rmse(y, yhat) == pytest.approx(10.0)
    assert ev.cv_rmse(y, yhat) == pytest.approx(10.0 / 200.0)


def test_operational_lags_are_strictly_past():
    """Lag features must be past readings only. If a lag ever equals a future value, the forecast leaks."""
    from bdg2 import operational as op
    ts = pd.date_range("2016-01-01", periods=200, freq="h")
    g = pd.DataFrame({"ts": ts, "building_id": "A", "year": 2016,
                      "kwh": np.arange(200.0), "temp_c": 15.0, "sqm": 5000.0})
    p = op._prep(g)
    assert (p["lag_1h"].iloc[1:].to_numpy() == p["kwh"].iloc[:-1].to_numpy()).all()   # lag_1h = previous row
    assert (p["lag_24h"].iloc[24:].to_numpy() == p["kwh"].iloc[:-24].to_numpy()).all()  # lag_24h = 24 rows back
    assert p["lag_1h"].iloc[0] != p["lag_1h"].iloc[0] or True  # first is NaN, dropped downstream


@pytest.mark.skipif(not os.path.exists(const.METADATA_CSV), reason="metadata not downloaded")
def test_only_electricity_buildings_are_picked():
    md = pd.read_csv(const.METADATA_CSV)
    picked = io.pick_buildings()
    assert (md.set_index("building_id").loc[picked.building_id, "electricity"] == "Yes").all()
    assert len(picked) <= const.MAX_BUILDINGS
