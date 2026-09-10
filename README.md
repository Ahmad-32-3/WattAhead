# WattAhead

Large buildings burn electricity every hour. Operators need a decent guess for the next hour so they can plan peaks and spot meters that start to look wrong.

I train a forecast on one building and test it on another building the model never saw. If it only memorized building A's habits, building B fails. The number I trust is forecast error on that held-out building.

Same-building 2016-train / 2017-test is the debug column. Reported numbers are leave-one-building-out RMSE and CV-RMSE (RMSE divided by mean of test y). R-squared is not the headline.

## Data

[Building Data Genome 2](https://github.com/buds-lab/building-data-genome-project-2) (CC BY 4.0). Paper: [Miller et al. 2020](https://doi.org/10.1038/s41597-020-00712-x). Hourly electricity (kWh), education buildings at one site.

## Run

```bash
python -m pytest tests/ -q
python scripts/run.py
npm --prefix web install
npm --prefix web run dev
```

If the meter download is blocked, leak tests and the walkthrough still run. The CLI prints `ILLUSTRATIVE` plus a one-line blocker.

## Layout

- `src/` forecast and eval
- `scripts/run.py` train/test CLI
- `tests/` leakage checks (held-out building must not leak into train)
- `web/` case-study page
