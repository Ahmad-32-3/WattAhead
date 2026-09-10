"""Defaults. Rat has 111 Education electricity buildings (metadata.csv) -> plenty above the 12 cap."""

SITE = "Rat"
USE = "Education"
MAX_BUILDINGS = 12

DATA = "data"
METADATA_CSV = f"{DATA}/metadata/metadata.csv"
ELECTRICITY_CSV = f"{DATA}/meters/raw/electricity.csv"  # wide: timestamp + one col per building_id
WEATHER_CSV = f"{DATA}/weather/weather.csv"

# calendar + temp + area. lags are the slice-2 swap.
FEATURES = ["hour", "dow", "month", "temp_c", "sqm"]
