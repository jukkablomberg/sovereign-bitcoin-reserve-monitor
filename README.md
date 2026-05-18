# Sovereign Bitcoin Reserve Monitor

> A live, open-sourced record of every sovereign state's Bitcoin holdings — tiered, sourced, and rendered.

**Live dashboard:** [`monitoringroom.com/sovereign-bitcoin`](https://monitoringroom.com/sovereign-bitcoin)
**Companion publication:** [Finnish Sovereign Bitcoin Whitepaper](https://github.com/jukkablomberg/sovereign-bitcoin-reserve-monitor) (publishing 23 May 2026)
**Maintainer:** [Jukka Blomberg](https://www.linkedin.com/in/jukkablomberg/)
**License:** MIT

---

## Why this exists

The sovereign Bitcoin map has stratified faster than any institutional reporting can keep up with. The US formalized a Strategic Bitcoin Reserve in March 2026; Brazil's Congress is debating a 1M-BTC bill (RESBit); Pakistan announced its own reserve; El Salvador continues to accumulate; Bhutan has materially divested. The Monitor exists to give policymakers, journalists, family offices, and researchers a single canonical reference for "where is the sovereign Bitcoin map today."

The methodology is public. The data is public. The scrapers are public. The rendered dashboard at [`monitoringroom.com/sovereign-bitcoin`](https://monitoringroom.com/sovereign-bitcoin) is a brand product, but the data layer is this repo. **Fork, deploy, extend — the only requirement is primary-source citations per [`methodology.md`](./methodology.md) §5.**

This is the third repo in the **Open-Source Consultancy** line, after [`corporate-bitcoin-treasury-memo`](https://github.com/jukkablomberg/corporate-bitcoin-treasury-memo) and the in-flight MiCA rule pack. Methodology in public; engagements stay private.

---

## What's in this repo

```
.
├── methodology.md             # The "Sovereign Monitor whitepaper" — v0.1.0
├── data/
│   ├── schema.json            # JSON Schema (Draft 2020-12) for the data
│   ├── sovereigns.json        # Canonical holdings dataset
│   └── events.json            # Timeline of material sovereign-BTC events
├── scripts/
│   └── update.py              # Daily refresh script (price + derived fields)
├── .github/workflows/
│   └── update.yml             # Daily scheduled refresh (02:00 UTC)
├── README.md                  # This file
└── LICENSE                    # MIT
```

The **rendered dashboard** lives at [`monitoringroom.com/sovereign-bitcoin`](https://monitoringroom.com/sovereign-bitcoin), deployed via the separate (private) [`jukkablomberg/monitoring`](https://github.com/jukkablomberg/monitoring) repo which auto-publishes to Vercel. The dashboard fetches data directly from this repo's `data/` directory via the GitHub raw URL, so the website and the data update independently. See `DEPLOY.md` for the full setup.

---

## Quickstart

### View locally

```bash
git clone https://github.com/jukkablomberg/sovereign-bitcoin-reserve-monitor.git
cd sovereign-bitcoin-reserve-monitor
python3 -m http.server 8000
# Open http://localhost:8000/web/ — the page reads ../data/sovereigns.json and ../data/events.json.
# Serving from the repo root (not from web/) is required so the relative data path resolves.
```

Once the repo is pushed to GitHub, the dashboard automatically falls back to
`https://raw.githubusercontent.com/jukkablomberg/sovereign-bitcoin-reserve-monitor/main/data/sovereigns.json`,
so it works from any static host (Vercel, Cloudflare Pages, Netlify, etc.) without further configuration.

### Refresh prices and derived fields

```bash
python3 scripts/update.py
```

The script fetches BTC/USD and BTC/EUR from CoinGecko's free public endpoint, recomputes tier, USD value, EUR value, and percent-of-supply, then writes `data/sovereigns.json` atomically. **It does not auto-scrape holdings** — those edits are deliberate, primary-source-cited, and made by hand or via PR.

### Add or correct a sovereign

1. Open `data/sovereigns.json`.
2. Add a new entry following the schema in `data/schema.json`. Every entry needs at least one primary or secondary source (see methodology §5).
3. Run `python3 scripts/update.py` to recompute tier and derived values.
4. Commit with a message that names the primary source, e.g., `add NO holdings (Norges Bank disclosure 2026-Q2)`.
5. Open a PR. CI will validate the schema.

---

## Methodology in 60 seconds

- **Status** — explicit policy taxonomy: `strategic_reserve`, `seized_held`, `announced_not_yet_held`, `legislation_proposed`, `exploring`, `divested`, `no_position`.
- **Tier** — computed from current verified holdings (Tier 1 ≥ 100k BTC … Tier 5 = 0 BTC).
- **Source-graded** — every entry cites at least one source labeled `primary` or `secondary`. We do not use unverified Twitter posts or aggregator-of-aggregator references as primary.
- **Refresh** — daily (price + derived fields) via scheduled GitHub Action. Holdings edits are event-driven and manual.

Full methodology: [`methodology.md`](./methodology.md).

---

## Roadmap

- **v0.1 (May 2026, this repo)** — initial schema, ~11 sovereigns seeded, static dashboard, daily price refresh.
- **v0.2 (June 2026)** — sub-sovereign extension (US states, Swiss cantons). PR-driven coverage expansion to ~25 sovereigns.
- **v0.3 (Q3 2026)** — agent-readable endpoint via x402 (Coinbase x402 / AWS Bedrock AgentCore). Same data, agent-callable.
- **v0.4 (Q4 2026)** — historical time-series view (BTC holdings by sovereign over time).

---

## Contributing

PRs welcome. Please:

1. Cite at least one primary source per change (see methodology §5).
2. Run `python3 scripts/update.py` before committing so derived fields stay current.
3. Keep entries concise — the `framework` field is for one or two sentences, not a full policy paragraph.

For corrections to existing data, please open an issue first describing the source and the proposed change.

---

## License

[MIT](./LICENSE). Use freely. Attribution appreciated but not required.

If the Monitor is useful to your work — institutional research, policy analysis, family-office allocation work, or journalism — consider subscribing to the [weekly Sovereign Bitcoin Reserve briefing](https://monitoringroom.com/sovereign-bitcoin#capture). One email per week, Tuesday mornings, written by the maintainer.
