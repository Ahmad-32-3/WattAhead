"""Fetch metadata + electricity + weather from BDG2 (Git LFS media endpoint) into data/.

Electricity only. If you ever add another meter type here, that is the 'every meter file' mistake -> fail loud.
"""
import os
import sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from bdg2 import const  # noqa: E402

MEDIA = "https://media.githubusercontent.com/media/buds-lab/building-data-genome-project-2/master/data/"
FILES = {
    const.METADATA_CSV: "metadata/metadata.csv",
    const.WEATHER_CSV: "weather/weather.csv",
    const.ELECTRICITY_CSV: "meters/cleaned/electricity_cleaned.csv",  # the ONLY meter file we pull
}

_METER_TYPES = ("chilledwater", "steam", "gas", "hotwater", "water", "irrigation", "solar")


def main():
    for remote in FILES.values():
        if remote.startswith("meters/") and any(t in remote for t in _METER_TYPES):
            raise SystemExit(f"refusing to pull non-electricity meter file: {remote}")
    for local, remote in FILES.items():
        if os.path.exists(local):
            print("have", local)
            continue
        os.makedirs(os.path.dirname(local), exist_ok=True)
        print("downloading", remote, "...")
        urllib.request.urlretrieve(MEDIA + remote, local)
        print("  ->", local)


if __name__ == "__main__":
    main()
