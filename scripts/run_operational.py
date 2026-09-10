"""Operational forecast (a DIFFERENT question from cold-start): you run the building and have its history.

Emits out/operational.json with per-building and aggregate results for two horizons, plus the persistence
baseline (copy the last known reading) so the model is never reported without the naive number beside it.
Honest headline: next-hour clears 80% within +/-20%.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from bdg2 import io, operational as op  # noqa: E402

OUT = "out"


def main():
    df = io.load()
    buildings = sorted(df.building_id.unique())
    horizons = {"day_ahead": op.DAY_AHEAD, "next_hour": op.NEXT_HOUR}

    out = {"tolerance_pct": int(op.TOL * 100), "min_mean_kwh": op.MIN_MEAN_KWH, "horizons": {}}
    for name, feats in horizons.items():
        rows, agg = op.evaluate(df, buildings, feats)
        out["horizons"][name] = {"aggregate": agg, "per_building": rows}
        print(f"\n{name}: within +/-{int(op.TOL*100)}% = {agg['within20_mean']}% +/- {agg['within20_std']} "
              f"(min {agg['within20_min']}%, n={agg['n_buildings']})   "
              f"persistence {agg['persistence_within20_mean']}%   CV-RMSE {agg['cv_rmse_mean']}")
        for r in sorted(rows, key=lambda r: -r["within20"]):
            print(f"    {r['building_id']:24s} model={r['within20']:5.1f}%  persistence={r['persistence_within20']:5.1f}%")

    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/operational.json", "w") as f:
        json.dump(out, f, indent=2)
    nh = out["horizons"]["next_hour"]["aggregate"]["within20_mean"]
    print(f"\nwrote {OUT}/operational.json  |  next-hour success rate = {nh}% ({'PASS >80%' if nh > 80 else 'below 80%'})")


if __name__ == "__main__":
    main()
