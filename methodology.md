# Sovereign Bitcoin Reserve Monitor — Methodology

**Authored by:** Jukka Blomberg
**First published:** 17 May 2026
**Live dashboard:** `monitoringroom.com/sovereign-bitcoin`
**Repo:** `github.com/jukkablomberg/sovereign-bitcoin-reserve-monitor`
**License:** MIT

---

## 1 · Purpose

This document describes the methodology behind the Sovereign Bitcoin Reserve Monitor — a public, machine-readable, openly-sourced record of every sovereign state's Bitcoin holdings, classified by reserve status and tier. The Monitor exists to give policymakers, journalists, family offices, and researchers a single canonical reference for "where is the sovereign Bitcoin map today," and to provide the live data layer behind the *Finnish Sovereign Bitcoin Whitepaper* (publishing 23 May 2026).

The Monitor is **not** an investment recommendation, a legal opinion, or a complete intelligence product. It is a transparency tool. Methodology is open; data is open; the dashboard that renders the data is a separate brand product, but the canonical data lives here.

---

## 2 · Scope

The Monitor tracks Bitcoin held by **sovereign states and their direct instrumentalities** (central banks, treasuries, sovereign wealth funds, state-owned enterprises with explicit treasury mandates). It does **not** track:

- Private companies (MicroStrategy, Tesla, Block, etc.) — covered by Bitcoin Treasuries and BitcoinTreasuries.net's corporate endpoint.
- Sub-national entities (US states, Swiss cantons) — tracked separately in a future "Sub-Sovereign" extension.
- ETF holdings beneficially owned by retail or institutional investors.
- Seized or forfeited assets held by law-enforcement agencies that have not been transferred to treasury (these are tracked in a separate `seizures` field; see §5).

The Monitor records states that have **0 BTC but have an active legislative process** (e.g., Brazil's RESBit bill, Czech CNB exploration), because the trajectory matters.

---

## 3 · Status taxonomy

Each entry has one canonical `status` field:

| Status | Definition |
|---|---|
| `strategic_reserve` | Held under an explicit strategic-reserve framework (executive order, statute, treasury mandate). Example: US Strategic Bitcoin Reserve, El Salvador, Bhutan. |
| `seized_held` | Held by a state agency as a result of seizure or forfeiture, not transferred to treasury, no public strategic-reserve framework. Example: Finland, Germany (historical), UK. |
| `announced_not_yet_held` | Government has publicly announced creation of a reserve but holdings are not yet publicly verified or are de minimis. Example: Pakistan (2026). |
| `legislation_proposed` | A bill or formal legislative proposal exists in a national legislature but has not yet been enacted. Example: Brazil RESBit (Feb 2026). |
| `exploring` | Central bank or treasury has publicly discussed or studied a reserve but no legislation is filed. Example: Czech CNB (April 2025 governor remarks). |
| `divested` | Previously held but materially reduced or fully sold. Example: Germany (2024 50k BTC sale); Bhutan (April 2026 13k → 3,654 BTC). |
| `no_position` | No verified holdings and no public policy process. Default for non-listed states. |

A state may transition between statuses over time; transitions are recorded in `data/events.json` (the timeline) and reflected in the `status_history` field of `data/sovereigns.json`.

---

## 4 · Tier classification

Tiers are assigned by current verified holdings, **not by status**. A state holding 50,000 seized BTC ranks in the same tier as a state holding 50,000 strategic-reserve BTC, but their `status` field distinguishes the policy intent.

| Tier | Holdings range | Description |
|---|---|---|
| Tier 1 | ≥100,000 BTC | The major holders. US dominates. |
| Tier 2 | 5,000 – 99,999 BTC | Material holders. El Salvador, Bhutan post-divest. |
| Tier 3 | 100 – 4,999 BTC | Small-to-mid holders. Finland is here. |
| Tier 4 | 1 – 99 BTC | De minimis holders. |
| Tier 5 | 0 BTC | No-position, exploring, or legislation-proposed. |

Tier is a rendering concept for the dashboard. It is recomputed from the `holdings_btc` field at every data refresh.

---

## 5 · Data sources

Each `holdings_btc` entry must cite at least one **primary** source and may cite secondary sources. Sources are tracked in the entry's `sources` array and surfaced in the dashboard's tooltip per row.

**Primary sources, in order of preference:**

1. **Official government disclosure** — treasury announcement, central-bank balance sheet, executive order, parliamentary report.
2. **On-chain verification** — addresses publicly attributed to the state via OFAC SDN lists, US Treasury seizure notices, or other government documentation.
3. **National audit office reports** — e.g., US GAO, NAO UK.

**Secondary sources (used when primaries unavailable or for cross-verification):**

1. **BitBo Treasuries** (`bitbo.io/treasuries/<country>`) — well-maintained aggregator with citation trail.
2. **BitcoinTreasuries.net** (`bitcointreasuries.net/governments`) — alternative aggregator.
3. **Chainalysis sovereign reports** — periodic published analysis.
4. **Reputable financial press** (Reuters, FT, Bloomberg, WSJ, Cointelegraph) — used only when reporting a primary source verifiable on the record.

**Sources we explicitly do not use as primary:**

- Twitter/X posts without primary-source attachment.
- Blogs and Substacks (used only as pointers to primary sources).
- Aggregator-of-aggregator sites without their own verification chain.

---

## 6 · Update frequency

The Monitor refreshes via two mechanisms:

1. **Scheduled daily refresh** — `scripts/update.py` runs nightly via GitHub Action (UTC 02:00). The script (a) fetches current BTC price from CoinGecko's free public endpoint, (b) recomputes `usd_value`, `pct_of_supply`, and `tier`, (c) writes a new `data/sovereigns.json`, (d) commits the diff. **No holdings data is automatically scraped**; only price and computed fields are auto-updated, because automated scraping of holdings data from aggregators has high false-positive risk.

2. **Event-driven manual update** — when a primary-source event occurs (treasury announcement, executive order, bill filing, seizure, sale), the maintainer edits `data/sovereigns.json` and `data/events.json` directly and pushes. All such commits are signed and reference the primary source in the commit message.

The methodology favours **verification over recency**. A 14-day-stale holding figure backed by primary-source citation is preferred over a same-day figure from an unverified aggregator.

---

## 7 · Data schema

The canonical schema is in `data/schema.json` (JSON Schema Draft 2020-12). Each sovereign entry contains:

- `country_code` — ISO 3166-1 alpha-2 (e.g., `US`, `FI`, `BR`).
- `country_name` — Display name (e.g., `United States`, `Finland`, `Brazil`).
- `holdings_btc` — Current verified holdings in whole BTC (rounded to nearest integer).
- `status` — One of the values in §3.
- `tier` — Computed from holdings (see §4).
- `framework` — Brief description of the holding framework, if any (e.g., `"Strategic Bitcoin Reserve, established March 2026 via executive framework"`).
- `as_of` — ISO-8601 date of the most recent primary-source confirmation of the holdings figure.
- `sources` — Array of `{label, url, type}` (type ∈ {`primary`, `secondary`}).
- `notes` — Free-text explanatory notes.
- `status_history` — Array of `{status, started_at, ended_at, note}` for state transitions.

Events live in `data/events.json` as `{date, country_code, headline, source, type}` where `type ∈ {announcement, legislation, executive_order, seizure, sale, exploration}`.

---

## 8 · Stratification commentary

The dashboard surfaces a tier-distribution view because the **shape of the sovereign Bitcoin map matters more than the absolute count**. As of mid-2026:

- **Tier 1** is dominated by a single state (US, ~325,000–328,000 BTC under explicit strategic-reserve framework). All other Tier-1-eligible holdings (China seizures, UK seizures) are `seized_held` not `strategic_reserve`, and their continued tier-1 standing depends on whether those states ever formalize them.
- **Tier 2** is occupied by El Salvador (~7,565 BTC, `strategic_reserve`) and Bhutan (~3,654 BTC, `divested` from a peak ~13,000 in 2024–2025 — Bhutan's case is a *monetization* path, not a treasury path, and is a counter-example for any state considering a reserve).
- **Tier 3** holds the operationally interesting set: Finland (90 BTC `seized_held`), Norway (small via wealth-fund exposure, no direct treasury holding), and a long tail.
- **Tier 5** is dominated by `legislation_proposed` (Brazil RESBit) and `exploring` (Czech CNB), which represent the next 18 months of meaningful change in the map.

The Monitor takes no position on whether any state *should* hold Bitcoin. It documents who does.

---

## 9 · Open-source commitment

The methodology, schema, data, and scraper code are all MIT-licensed. The rendered dashboard at `monitoringroom.com/sovereign-bitcoin` is a separate product, but it is built entirely from this open data. Anyone may fork, deploy, or extend the Monitor. Pull requests that add states, correct figures, or improve source citations are welcome with the only requirement being primary-source attribution per §5.

This commitment follows the **Open-Source Consultancy** operating principle: every templatable deliverable lives in public; only the engagement-grade synthesis (private memos, custom briefings, advisory work) is paid. The Sovereign Bitcoin Reserve Monitor is the third repo in this line, after the Corporate Bitcoin Treasury Memo and the in-flight MiCA rule pack.

---

## 10 · Versioning

This document is versioned as `methodology.md` in the repo. Material methodological changes (new statuses, new tier thresholds, scope changes) are captured in a `CHANGELOG.md` and tagged in the repo. Minor edits (wording, formatting) are not versioned separately.

**Methodology version:** v0.1.0 — 17 May 2026.
