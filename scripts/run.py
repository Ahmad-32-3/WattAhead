"""download (if missing) -> split -> fit Ridge -> metrics.json + preds. Prints lobo next to same-building RMSE."""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from bdg2 import const, io, split, predict, eval as ev, ablate  # noqa: E402
import download  # noqa: E402

OUT = "out"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=const.SITE)
    ap.add_argument("--use", default=const.USE)
    ap.add_argument("--max-buildings", type=int, default=const.MAX_BUILDINGS)
    ap.add_argument("--test-id", default=None, help="held-out building; default = first by name")
    a = ap.parse_args()

    if a.max_buildings > const.MAX_BUILDINGS:
        raise SystemExit(f"--max-buildings {a.max_buildings} over cap {const.MAX_BUILDINGS}")

    download.main()
    df = io.load(a.site, a.use, a.max_buildings)
    ids = sorted(df.building_id.unique())
    n_buildings = len(ids)
    if n_buildings > const.MAX_BUILDINGS:
        raise SystemExit(f"n_buildings {n_buildings} over cap {const.MAX_BUILDINGS}")

    has2017 = set(df[df.year == 2017].building_id)
    has_both = has2017 & set(df[df.year == 2016].building_id)
    test_id = a.test_id or next(b for b in ids if b in has2017)  # test needs 2017 rows
    # same-meter debug: a DIFFERENT building that has both years on its own meter
    debug_id = next(b for b in ids if b != test_id and b in has_both)

    tr, te = split.lobo(df, test_id)
    lobo_pred, n_train, train_cv = predict.fit_predict(tr, te)
    lobo_rmse, lobo_cv = ev.score(lobo_pred)

    dtr, dte = split.same_building(df, debug_id)
    sb_pred, _, _ = predict.fit_predict(dtr, dte)
    sb_rmse, sb_cv = ev.score(sb_pred)

    ablation = ablate.table(df, test_id)  # same lobo split, three feature sets
    results = _results(lobo_pred, lobo_cv, sb_cv, train_cv, ablation)

    os.makedirs(OUT, exist_ok=True)
    lobo_pred = lobo_pred.assign(split="lobo")
    sb_pred = sb_pred.assign(split="same_building")
    preds = __import__("pandas").concat([lobo_pred, sb_pred])[["ts", "building_id", "y", "yhat", "split"]]
    preds.to_json(f"{OUT}/preds.jsonl", orient="records", lines=True, date_format="iso")

    metrics = {
        "rmse": lobo_rmse, "cv_rmse": lobo_cv,
        "same_building_rmse": sb_rmse, "same_building_cv_rmse": sb_cv,
        "n_train": n_train, "n_test": int(len(lobo_pred)),
        "train_ids": [b for b in ids if b != test_id],
        "test_id": test_id, "same_building_debug_id": debug_id,
        "site_id": a.site, "primaryspaceusage": a.use,
        "n_buildings": n_buildings, "features": const.FEATURES,
        "kwh_test_min": float(lobo_pred.y.min()), "kwh_test_max": float(lobo_pred.y.max()),
        "ablation": ablation,
        "results": results,
        "illustrative": False,
    }
    with open(f"{OUT}/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nsite={a.site} use={a.use} n_buildings={n_buildings} test_id={test_id}")
    print(f"  leave-one-building-out  RMSE={lobo_rmse:8.1f} kWh   CV-RMSE={lobo_cv:.3f}   (n_test={len(lobo_pred)})")
    print(f"  same-building (debug)   RMSE={sb_rmse:8.1f} kWh   CV-RMSE={sb_cv:.3f}   ({debug_id})")
    print("  ablation (same lobo split):")
    for name, m in ablation.items():
        print(f"    {name:24s} RMSE={m['rmse']:8.1f} kWh   CV-RMSE={m['cv_rmse']:.3f}")
    print("  results:")
    for k, v in results.items():
        print(f"    {k:22s} {v}")
    print(f"  wrote {OUT}/metrics.json, {OUT}/preds.jsonl")


def _results(lobo_pred, lobo_cv, sb_cv, train_cv, ablation):
    """Honest derived numbers for the held-out forecast. Skill = 1 - model_error/baseline_error."""
    import numpy as np
    y = lobo_pred.y.to_numpy()
    yhat = lobo_pred.yhat.to_numpy()
    ape = np.abs((y - yhat) / y)  # kwh min > 0, no divide-by-zero
    how_cv = ablation["hour_of_week_mean"]["cv_rmse"]
    area_cv = ablation["area_only"]["cv_rmse"]
    return {
        "mae_kwh": round(float(np.mean(np.abs(y - yhat))), 2),
        "median_ape_pct": round(float(np.median(ape) * 100), 1),
        "hours_within_20pct": round(float(np.mean(ape <= 0.20) * 100), 1),
        "typical_error_pct_of_load": round(lobo_cv * 100, 1),   # CV-RMSE as a percent
        "skill_vs_hour_of_week_pct": round((1 - lobo_cv / how_cv) * 100, 1),
        "skill_vs_area_only_pct": round((1 - lobo_cv / area_cv) * 100, 1),
        "holdout_penalty_pct": round((lobo_cv / sb_cv - 1) * 100, 1),  # how much harder a new building is
        "train_cv_rmse": round(train_cv, 3),
        "test_cv_rmse": round(lobo_cv, 3),
        "overfit_gap_pct": round((lobo_cv / train_cv - 1) * 100, 1),   # small = not overfit
    }


if __name__ == "__main__":
    main()
