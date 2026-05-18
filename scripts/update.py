#!/usr/bin/env python3
"""
Sovereign Bitcoin Reserve Monitor — daily refresh script.

Responsibility:
    1. Fetch current BTC/USD and BTC/EUR price from CoinGecko (free public endpoint).
    2. Re-read data/sovereigns.json (hand-curated holdings — do NOT auto-scrape).
    3. Recompute tier, derived USD/EUR values, and percent-of-supply.
    4. Stamp a new generated_at timestamp.
    5. Write data/sovereigns.json back atomically.

Run locally:
    python3 scripts/update.py

Run in CI:
    See .github/workflows/update.yml (scheduled daily 02:00 UTC).

Methodology: see methodology.md §6. This script automates ONLY computed fields.
All holdings_btc figures must be edited by hand against primary sources.
"""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "sovereigns.json"
METHODOLOGY_VERSION = "v0.1.0"

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin&vs_currencies=usd,eur"
)

# Approximate circulating supply mid-2026. Updated occasionally; ~656 BTC/day issued.
DEFAULT_TOTAL_SUPPLY = 19_850_000


def fetch_btc_price() -> tuple[float, float]:
    """Return (usd, eur) BTC price from CoinGecko. Falls back to last known values on failure."""
    try:
        req = urllib.request.Request(
            COINGECKO_URL,
            headers={"User-Agent": "sovereign-btc-monitor/0.1 (+https://github.com/jukkablomberg/sovereign-bitcoin-reserve-monitor)"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read())
        usd = float(payload["bitcoin"]["usd"])
        eur = float(payload["bitcoin"]["eur"])
        return usd, eur
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] CoinGecko fetch failed ({exc}); using last-known prices from file.", file=sys.stderr)
        return None, None


def compute_tier(holdings_btc: int) -> int:
    if holdings_btc >= 100_000:
        return 1
    if holdings_btc >= 5_000:
        return 2
    if holdings_btc >= 100:
        return 3
    if holdings_btc >= 1:
        return 4
    return 5


def main() -> int:
    if not DATA_FILE.exists():
        print(f"[error] {DATA_FILE} not found", file=sys.stderr)
        return 1

    with DATA_FILE.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    usd, eur = fetch_btc_price()
    if usd is None:
        usd = float(data.get("meta", {}).get("btc_price_usd") or 0)
        eur = float(data.get("meta", {}).get("btc_price_eur") or 0)
        if usd == 0:
            print("[error] no fallback prices in existing data; aborting.", file=sys.stderr)
            return 2

    data["meta"]["btc_price_usd"] = round(usd, 2)
    data["meta"]["btc_price_eur"] = round(eur, 2)
    data["meta"]["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data["meta"]["methodology_version"] = METHODOLOGY_VERSION
    if "total_btc_supply" not in data["meta"]:
        data["meta"]["total_btc_supply"] = DEFAULT_TOTAL_SUPPLY

    total_supply = float(data["meta"]["total_btc_supply"])
    for entry in data["sovereigns"]:
        holdings = int(entry.get("holdings_btc", 0))
        entry["tier"] = compute_tier(holdings)
        # Derived (read-only) fields for the dashboard. Computed at every refresh.
        entry["_derived"] = {
            "usd_value": round(holdings * usd, 2),
            "eur_value": round(holdings * eur, 2),
            "pct_of_supply": round(100 * holdings / total_supply, 4) if total_supply else 0,
        }

    tmp_path = DATA_FILE.with_suffix(".json.tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp_path, DATA_FILE)

    n = len(data["sovereigns"])
    total = sum(int(s.get("holdings_btc", 0)) for s in data["sovereigns"])
    print(
        f"[ok] wrote {DATA_FILE.relative_to(REPO_ROOT)} — "
        f"{n} sovereigns, total {total:,} BTC, BTC/USD {usd:,.0f}, BTC/EUR {eur:,.0f}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
