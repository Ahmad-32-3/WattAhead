import { StoryBeat } from './components/story/StoryBeat'
import { ResultBars } from './components/story/ResultBars'
import { ForecastChart } from './components/story/ForecastChart'
import { SOURCE, SETUP, OPERATIONAL, SPECTRUM, FORECAST_SAMPLE, DECISIONS, STACK } from './data'

const nh = OPERATIONAL.nextHour
const da = OPERATIONAL.dayAhead

export function App() {
  return (
    <>
      <a className="skip-link" href="#main">Skip to content</a>

      <header className="masthead">
        <div className="masthead__inner">
          <span className="masthead__mark">
            <b>WattAhead</b> · forecasting a meter from its own past
          </span>
          <nav aria-label="Sections">
            <ul className="masthead__nav">
              <li><a href="#solution">solution</a></li>
              <li><a href="#inputs">inputs</a></li>
              <li><a href="#range">range</a></li>
              <li><a href="#baseline">baseline</a></li>
              <li><a href="#decisions">choices</a></li>
              <li><a href="#stack">stack</a></li>
            </ul>
          </nav>
        </div>
      </header>

      <main id="main" className="page">
        <div className="page-hero">
          <p className="meta">
            {SOURCE.corpus} · {SETUP.site}/{SETUP.use} · {SETUP.nBuildings} electricity meters
          </p>
          <h1>WattAhead</h1>
          <p className="lead">
            Large buildings burn electricity every hour. Operators need a decent guess for the next
            hour so they can plan peaks and spot meters that start to look wrong. I train a forecast
            on one building and test it on another building the model never saw. If it only memorized
            building A&apos;s habits, building B fails. The number I trust is forecast error on that
            held-out building.
          </p>
          <p className="intro-detail">
            The meter reading moves every hour with the weather, the schedule, and who walked in the door. I forecast
            that reading on the public {SOURCE.corpus} dataset and check every prediction against what the meter
            actually recorded. The main charts use a later year on the same meters. The no-history bar is the other
            building: a meter the model never saw.
          </p>
          <ul className="toc">
            <li><a href="#solution">01 · the forecast</a></li>
            <li><a href="#inputs">02 · what goes in</a></li>
            <li><a href="#range">03 · how far ahead</a></li>
            <li><a href="#baseline">04 · vs doing nothing</a></li>
            <li><a href="#decisions">05 · choices</a></li>
            <li><a href="#stack">06 · stack</a></li>
          </ul>
        </div>

        <StoryBeat
          id="solution"
          kicker="the forecast"
          title="Predict the meter from its own history"
          caption={`One building, one week in May. Forecast against the meter, ${FORECAST_SAMPLE.within20}% of hours within 20%.`}
          visual={<ForecastChart />}
        >
          <p>
            Take a building you already run, with a year of electricity readings behind it, and predict what the meter
            will say next. The model learns the building&rsquo;s rhythm from {SETUP.trainYear} and forecasts every hour
            of {SETUP.testYear}, a year it never touched during training.
          </p>
          <p>
            For the next hour it lands within 20% of the real reading about <strong>{nh.within20}%</strong> of the time.
            A day ahead, about {da.within20}% of the time. Same building, same 20% window. What changes is how far out
            you are looking.
          </p>
          <p>
            The two bars on the right are those two numbers. The rest of this page is how it works and where it stops
            working.
          </p>
        </StoryBeat>

        <StoryBeat
          id="inputs"
          kicker="what goes in"
          title="A prediction is mostly the recent past"
          caption="Five inputs. The three lagged readings do most of the work."
          visual={
            <div className="teach-card">
              <ul className="stack-list" style={{ margin: 0 }}>
                {[
                  <><strong>Last hour&rsquo;s reading</strong> (next-hour forecast only)</>,
                  <><strong>Same hour yesterday</strong></>,
                  <><strong>Same hour last week</strong></>,
                  <><strong>Outdoor temperature</strong></>,
                  <><strong>Hour, day of week, month</strong></>,
                ].map((item, i) => (
                  <li key={i} className="layer-drop" style={{ animationDelay: `${i * 90}ms` }}>{item}</li>
                ))}
              </ul>
            </div>
          }
        >
          <p>
            There is no clever input here. To guess this hour, the model looks at what the meter read an hour ago, at
            the same hour yesterday, and at the same hour last week. Then it adds the outdoor temperature and where you
            are in the week.
          </p>
          <p>
            Those past readings carry the load, because a building repeats itself. A Tuesday at 9am looks a lot like
            last Tuesday at 9am. Every input is at least a day old for the day-ahead version and an hour old for the
            next-hour version, so nothing from the future leaks in and you could point this at a live meter.
          </p>
        </StoryBeat>

        <StoryBeat
          id="range"
          kicker="how far ahead"
          title="It comes down to how much past you have"
          caption="Same buildings, same 20% window. The only thing changing is how much of the meter's own history the model gets."
          visual={
            <ResultBars
              max={100}
              pct
              rows={SPECTRUM.map((s, i) => ({
                label: s.label,
                value: s.value,
                tone: i === 0 ? 'bad' : i === 1 ? 'accent' : 'good',
                note: s.note,
              }))}
            />
          }
        >
          <p>
            One pattern runs through the whole project. The more of the building&rsquo;s own recent history the model
            holds, the better it does. Hand it the last reading and the next hour is easy. Hand it only yesterday and
            last week, and a full day out gets harder. Hand it nothing, a building you have never metered, and it mostly
            cannot even guess the level.
          </p>
          <p>
            That last case is the floor, around {SPECTRUM[0].value}%. A brand new building has no baseline the model can
            read, because a building&rsquo;s load level is not written in its floor area or the local weather. Without
            any of its own readings, there is nothing to anchor to. The three bars are the same buildings scored three
            ways, low history to high.
          </p>
        </StoryBeat>

        <StoryBeat
          id="baseline"
          kicker="vs doing nothing"
          title="Does the model beat repeating the last value"
          caption="Model against the repeat-the-last-reading baseline, both horizons."
          visual={
            <ResultBars
              max={100}
              pct
              rows={[
                { label: 'Next hour · model', value: nh.within20, tone: 'good' },
                { label: 'Next hour · repeat last', value: nh.persistence, tone: 'accent' },
                { label: 'Day ahead · model', value: da.within20, tone: 'good' },
                { label: 'Day ahead · repeat last', value: da.persistence, tone: 'accent' },
              ]}
            />
          }
        >
          <p>
            Fair question: could you skip the model and just repeat the last reading you have? For the next hour, mostly
            yes. Repeating the previous value is right about {nh.persistence}% of the time, a shade ahead of the model,
            because load barely moves from one hour to the next.
          </p>
          <p>
            A day out the story changes for the steady buildings. There the model beats plain repetition by ten points
            or more, since yesterday&rsquo;s value is stale and the weekly shape is worth learning. A couple of jumpy
            buildings, the ones whose {SETUP.testYear} stopped resembling their {SETUP.trainYear}, pull the day-ahead
            average back down to {da.within20}%. Repetition is a strong baseline, so it stays on the chart next to every
            result.
          </p>
        </StoryBeat>

        <StoryBeat
          id="decisions"
          kicker="the choices"
          title="What I fixed, and why"
        >
          <p>
            A handful of decisions did most of the work of keeping this trustworthy. Here they are, with the reason for
            each.
          </p>
          <dl className="stat-grid" style={{ gridTemplateColumns: '1fr' }}>
            {DECISIONS.map((d) => (
              <div key={d.k}>
                <dt>{d.k} &middot; <span style={{ color: 'var(--accent-bright)' }}>{d.v}</span></dt>
                <dd style={{ fontFamily: 'var(--font-text)', fontSize: 'var(--fs-sm)', color: 'var(--fg)' }}>{d.why}</dd>
              </div>
            ))}
          </dl>
        </StoryBeat>

        <StoryBeat id="stack" kicker="the tools" title="What it is built on">
          <p>
            No job queue, no service, no pile of models. The point was a clean answer to one question, so the stack
            stays small.
          </p>
          <ul className="stack-grid">
            {STACK.map((t) => (
              <li key={t.name} className="stack-tool">
                <div className="stack-tool__head">
                  <span className="stack-tool__name">{t.name}</span>
                  <span className="stack-tool__tag">{t.tag}</span>
                </div>
                <p className="stack-tool__plain">{t.plain}</p>
                <p className="stack-tool__tech">{t.tech}</p>
              </li>
            ))}
          </ul>
        </StoryBeat>

        <footer style={{ borderTop: '1px solid var(--line-rule)', paddingTop: 'var(--space-5)', marginTop: 'var(--space-8)' }}>
          <p className="meta" style={{ textTransform: 'none', letterSpacing: 0 }}>
            Data: {SOURCE.corpus} ({SOURCE.cite}), <code>{SOURCE.repo}</code>, {SOURCE.license}. One site,{' '}
            {SETUP.use.toLowerCase()} buildings, electricity only.
          </p>
        </footer>
      </main>
    </>
  )
}
