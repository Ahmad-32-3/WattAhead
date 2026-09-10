"""Load BDG2: pick electricity buildings for one site+use, melt long, join weather. Functions only."""
import pandas as pd
from . import const


def pick_buildings(site=const.SITE, use=const.USE, cap=const.MAX_BUILDINGS, metadata_csv=const.METADATA_CSV):
    """building_ids at one site with one primaryspaceusage that have an electricity meter. Needs sqm (a feature)."""
    md = pd.read_csv(metadata_csv)
    m = md[(md.site_id == site) & (md.primaryspaceusage == use) & (md.electricity == "Yes")].dropna(subset=["sqm"])
    m = m.sort_values("building_id").head(cap)
    if len(m) < 2:
        raise ValueError(f"need >=2 buildings for a leave-one-building-out split, got {len(m)} for {site}/{use}")
    return m[["building_id", "site_id", "primaryspaceusage", "sqm"]].reset_index(drop=True)


def load(site=const.SITE, use=const.USE, cap=const.MAX_BUILDINGS):
    """Long frame: ts, building_id, site_id, primaryspaceusage, sqm, kwh, temp_c, year. Electricity only."""
    meta = pick_buildings(site, use, cap)
    ids = meta.building_id.tolist()

    elec = pd.read_csv(const.ELECTRICITY_CSV, usecols=lambda c: c == "timestamp" or c in ids)
    missing = set(ids) - set(elec.columns)
    if missing:
        raise ValueError(f"electricity.csv missing building columns: {sorted(missing)}")
    elec["timestamp"] = pd.to_datetime(elec["timestamp"])
    long = elec.melt(id_vars="timestamp", var_name="building_id", value_name="kwh").rename(columns={"timestamp": "ts"})
    long = long.dropna(subset=["kwh"])  # do not fill across buildings

    wx = pd.read_csv(const.WEATHER_CSV, usecols=["timestamp", "site_id", "airTemperature"])
    wx = wx[wx.site_id == site].rename(columns={"timestamp": "ts", "airTemperature": "temp_c"})
    wx["ts"] = pd.to_datetime(wx["ts"])
    wx = wx.dropna(subset=["temp_c"])[["ts", "temp_c"]]

    df = long.merge(meta, on="building_id", how="left").merge(wx, on="ts", how="inner")
    df["year"] = df.ts.dt.year
    return df[["ts", "building_id", "site_id", "primaryspaceusage", "sqm", "kwh", "temp_c", "year"]]
