// Horizontal CV-RMSE bars. Lower is better. Used for the split contrast and the ablation.
type Row = { label: string; value: number; tone?: 'good' | 'bad' | 'accent'; note?: string }

const TONE: Record<string, string> = {
  good: 'var(--chart-1)',
  bad: 'var(--chart-2)',
  accent: 'var(--chart-3)',
}

export function ResultBars({ rows, max = 0.6, pct = false }: { rows: Row[]; max?: number; pct?: boolean }) {
  return (
    <figure className="story-viz" style={{ margin: 0 }}>
      <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
        {rows.map((r, i) => (
          <li key={r.label}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--fs-sm)', marginBottom: 4 }}>
              <span style={{ color: 'var(--fg-hi)' }}>{r.label}</span>
              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--fg-low)' }}>{pct ? `${r.value}%` : r.value.toFixed(3)}</span>
            </div>
            <div style={{ background: 'var(--bg-sunk)', border: '1px solid var(--line-hairline)', height: 16, borderRadius: 2 }}>
              <div className="bar-grow" style={{
                width: `${Math.min(100, (r.value / max) * 100)}%`, height: '100%',
                background: TONE[r.tone ?? 'accent'], borderRadius: 2, animationDelay: `${i * 90}ms`,
              }} />
            </div>
            {r.note ? <p className="meta" style={{ margin: '4px 0 0', textTransform: 'none', letterSpacing: 0 }}>{r.note}</p> : null}
          </li>
        ))}
      </ul>
    </figure>
  )
}
