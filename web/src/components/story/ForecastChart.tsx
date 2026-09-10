import { FORECAST_SAMPLE } from '../../data'

// One week of hourly kWh: the meter reading against the next-hour forecast.
// The predicted line draws itself in on mount and on Replay.
const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

export function ForecastChart() {
  const { actual, predicted } = FORECAST_SAMPLE
  const n = actual.length
  const W = 340, H = 190, padL = 30, padR = 8, padT = 10, padB = 22
  const plotW = W - padL - padR
  const plotH = H - padT - padB
  const yMax = 280
  const x = (i: number) => padL + (i / (n - 1)) * plotW
  const y = (v: number) => padT + (1 - v / yMax) * plotH
  const line = (arr: number[]) => arr.map((v, i) => `${i === 0 ? 'M' : 'L'} ${x(i).toFixed(1)} ${y(v).toFixed(1)}`).join(' ')
  const areaActual = `${line(actual)} L ${x(n - 1).toFixed(1)} ${y(0)} L ${x(0).toFixed(1)} ${y(0)} Z`

  return (
    <figure className="story-viz" style={{ margin: 0 }}>
      <svg className="chart-svg" viewBox={`0 0 ${W} ${H}`} role="img"
        aria-label={`Hourly electricity for one building over a week. The forecast tracks the meter closely, ${FORECAST_SAMPLE.within20}% of hours within 20 percent.`}>
        <defs>
          <linearGradient id="fc-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.16" />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* y gridlines + labels */}
        {[100, 200].map((v) => (
          <g key={v}>
            <line x1={padL} y1={y(v)} x2={W - padR} y2={y(v)} stroke="var(--chart-grid)" strokeWidth="1" />
            <text x={padL - 6} y={y(v) + 3} textAnchor="end" fontSize="9" fill="var(--chart-label)" fontFamily="var(--font-mono)">{v}</text>
          </g>
        ))}
        {/* day separators + labels */}
        {DAYS.map((d, i) => (
          <g key={d}>
            {i > 0 && <line x1={x(i * 24)} y1={padT} x2={x(i * 24)} y2={padT + plotH} stroke="var(--line-hairline)" strokeWidth="1" />}
            <text x={x(i * 24 + 12)} y={H - 7} textAnchor="middle" fontSize="9" fill="var(--chart-label)" fontFamily="var(--font-mono)">{d}</text>
          </g>
        ))}

        <path d={areaActual} fill="url(#fc-fill)" stroke="none" />
        <path d={line(actual)} fill="none" stroke="var(--fg-low)" strokeWidth="1.4" strokeLinejoin="round" />
        <path className="draw-line" pathLength={1} d={line(predicted)} fill="none" stroke="var(--accent-bright)" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
      </svg>
      <ul className="legend">
        <li><span className="swatch" style={{ background: 'var(--fg-low)' }} /> meter reading</li>
        <li><span className="swatch" style={{ background: 'var(--accent-bright)' }} /> forecast</li>
      </ul>
    </figure>
  )
}
