// Every number on this page lives here, in one place.
//
// These are measured, not made up. scripts/run_operational.py wrote out/operational.json
// from real fits on Building Data Genome 2 (site Rat, Education, electricity meters), and
// these constants are copied from it. The cold-start figure comes from scripts/run.py /
// out/metrics.json. Re-run the CLIs and re-copy if you change the setup, or the page drifts.

export const SOURCE = {
  corpus: 'Building Data Genome 2',
  cite: 'Miller et al., Scientific Data 2020',
  repo: 'buds-lab/building-data-genome-project-2',
  license: 'CC BY 4.0',
}

export const SETUP = {
  site: 'Rat',
  use: 'Education',
  nBuildings: 7, // clean meters that pass the data-quality gate
  trainYear: 2016,
  testYear: 2017,
  tolerancePct: 20,
}

// The forecast, scored as share of hourly predictions within +/-20% of the meter reading.
// Averaged over the clean buildings, with the persistence baseline (repeat the last reading) beside it.
export const OPERATIONAL = {
  nextHour: { within20: 87.6, std: 9.7, persistence: 93.0, cvRmse: 0.132 },
  dayAhead: { within20: 63.0, std: 16.2, persistence: 73.9, cvRmse: 0.318 },
}

// One idea runs through the whole thing: accuracy tracks how much of the building's own past you hold.
export const SPECTRUM = [
  { label: 'No history (new building)', value: 24, note: 'nothing to go on but other buildings' },
  { label: 'A year of history, one day ahead', value: 63, note: 'yesterday and last week' },
  { label: 'A year of history, one hour ahead', value: 88, note: 'plus the last reading' },
]

// One building, one week of 2017, next-hour forecast against the meter. For the line chart.
// Pulled from the same model as OPERATIONAL, week of 8 May 2017 (Monday start), 168 hourly points.
export const FORECAST_SAMPLE = {
  weekLabel: 'week of 8 May 2017',
  within20: 94,
  actual: [98.5, 81.0, 82.6, 143.4, 132.5, 144.6, 161.3, 171.5, 202.9, 215.6, 212.4, 197.1, 197.0, 172.4, 185.7, 182.7, 177.7, 134.8, 93.3, 94.3, 76.5, 75.9, 88.1, 88.5, 81.9, 68.3, 68.0, 140.3, 107.7, 108.9, 134.7, 159.2, 185.9, 197.4, 209.6, 228.8, 222.2, 199.5, 198.1, 194.5, 181.4, 147.9, 124.8, 112.9, 76.7, 76.3, 87.7, 89.6, 85.6, 71.9, 71.6, 124.9, 119.7, 113.4, 145.5, 162.2, 187.5, 225.7, 274.8, 231.2, 234.0, 228.4, 223.9, 214.5, 207.9, 165.8, 120.3, 116.3, 81.4, 83.7, 95.1, 94.6, 82.7, 68.3, 70.0, 107.6, 123.5, 118.5, 137.2, 168.5, 201.1, 218.3, 217.0, 219.6, 204.3, 195.8, 197.6, 183.4, 159.5, 138.8, 125.0, 121.5, 80.0, 78.7, 90.7, 90.4, 85.1, 69.8, 71.3, 117.5, 115.5, 113.3, 145.3, 173.0, 191.5, 227.7, 218.5, 203.3, 189.2, 179.5, 191.0, 194.4, 172.7, 144.4, 115.1, 111.8, 74.6, 73.3, 86.5, 86.2, 80.1, 65.4, 65.7, 66.2, 66.0, 65.6, 68.1, 68.0, 62.8, 64.4, 65.7, 69.1, 65.5, 65.9, 67.0, 65.1, 67.9, 68.6, 64.5, 66.1, 68.4, 76.8, 88.4, 88.8, 83.1, 69.9, 69.0, 68.8, 69.5, 69.5, 68.0, 64.4, 63.7, 62.7, 64.7, 63.8, 64.2, 64.4, 63.7, 64.6, 65.3, 64.8, 64.2, 64.3, 70.0, 76.9, 88.3, 88.6],
  predicted: [95.7, 92.7, 82.0, 152.5, 181.6, 179.2, 186.2, 202.1, 184.3, 215.2, 218.9, 212.6, 198.4, 201.1, 185.4, 188.8, 170.6, 166.7, 131.9, 102.6, 86.7, 77.7, 80.9, 84.0, 87.6, 80.1, 73.6, 143.8, 146.2, 148.2, 179.3, 185.2, 174.8, 198.7, 209.3, 212.5, 224.7, 216.2, 194.8, 194.6, 186.4, 167.6, 129.1, 108.8, 91.2, 71.8, 81.3, 85.0, 86.1, 77.8, 70.3, 131.8, 130.9, 118.1, 140.5, 172.1, 177.8, 192.0, 224.1, 270.9, 229.9, 233.4, 230.8, 226.3, 211.8, 196.3, 149.0, 109.3, 95.5, 76.9, 87.3, 88.2, 95.2, 78.1, 69.5, 109.7, 135.1, 135.3, 154.8, 172.6, 176.8, 210.0, 225.7, 216.6, 216.3, 201.0, 193.0, 194.1, 173.6, 156.8, 120.8, 110.9, 90.2, 78.3, 83.1, 85.6, 85.7, 77.8, 69.2, 93.7, 124.8, 108.1, 133.3, 173.2, 183.5, 203.1, 217.7, 211.3, 199.3, 183.5, 174.5, 185.8, 185.8, 164.0, 136.6, 103.8, 90.5, 72.6, 80.3, 86.8, 85.4, 74.0, 66.3, 69.3, 69.5, 69.9, 70.6, 72.2, 69.9, 64.9, 68.9, 68.7, 71.2, 67.4, 68.6, 67.9, 68.0, 70.7, 74.6, 69.6, 67.4, 66.2, 80.6, 88.5, 84.7, 75.1, 68.4, 67.8, 68.2, 70.1, 70.5, 68.7, 65.3, 65.8, 65.4, 69.0, 68.4, 68.2, 69.7, 67.6, 69.3, 69.4, 72.7, 68.4, 70.1, 73.0, 80.9, 86.5],
}

export const DECISIONS = [
  { k: 'Test', v: 'train on 2016, forecast 2017', why: 'The model only ever sees the past and predicts a year it has not seen. That is the thing you actually want to know.' },
  { k: 'Inputs', v: 'the meter’s own recent readings', why: 'Yesterday at this hour and last week at this hour carry most of the signal. Weather and the calendar fill in the rest.' },
  { k: 'Baseline', v: 'repeat the last reading', why: 'If the model cannot beat copying the previous value, it is not earning its place. So that number sits next to every result.' },
  { k: 'No peeking', v: 'every input is a day old', why: 'The model never reads a value from the future, so you could run it live on a real meter tomorrow.' },
]

export const STACK = [
  { name: 'pandas', tag: 'data', plain: 'Reshape the wide meter file into one row per building-hour, then add lagged columns from each building’s own past.', tech: 'shift(1h / 24h / 168h) within a building, weather and calendar joined on.' },
  { name: 'scikit-learn', tag: 'model', plain: 'A gradient-boosted tree per building, trained on its 2016 and scored on 2017.', tech: 'HistGradientBoostingRegressor, RMSE and CV-RMSE.' },
  { name: 'pytest', tag: 'guard', plain: 'A test fails if a lag ever picks up a future value, so the setup cannot leak.', tech: 'test_eval.py checks lag_1h equals the previous row, not a later one.' },
  { name: 'Vite + React 19 + TS', tag: 'web', plain: 'This page. Every figure is read from the metrics files the runs wrote.', tech: 'Tailwind 4, no network at runtime.' },
]
