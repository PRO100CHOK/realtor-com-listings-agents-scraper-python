"""Realtor.com underpriced-listing screen + agent shortlist.

Use case: an investor or buyer's agent wants the for-sale homes in a few ZIP
codes that are listed BELOW their own ZIP's median price per square foot, plus
a shortlist of the most active, best-rated local agents to call about them.

  Step 1 - pull for-sale listings for each ZIP with market stats switched on,
           so every record carries `neighborhoodMedianPricePerSqft`.
  Step 2 - keep the listings priced at least DISCOUNT below that median.
  Step 3 - pull agents for the same city and rank them by homes sold in the
           last 12 months and by Realtor.com star rating.

Writes output.json / output.csv (the underpriced listings) and agents.csv.

Run:
    pip install -r requirements.txt
    cp .env.example .env
    python main.py

Actor: https://apify.com/pro100chok/realtor-com-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

from apify_client import ApifyClient
from apify_client.errors import ApifyApiError
from dotenv import load_dotenv

ACTOR_ID = "pro100chok/realtor-com-scraper"
ZIPS = ["78745", "78748", "78744"]      # south Austin, TX
CITY = "Austin, TX"                      # where to look for agents
DISCOUNT = 0.10                          # 10% under the ZIP median $/sqft
LISTINGS_PER_ZIP = 150
AGENTS = 60

LISTING_COLUMNS = [
    "postalCode", "addressLine", "listPrice", "sqft", "pricePerSqft",
    "neighborhoodMedianPricePerSqft", "discountPct", "beds", "baths",
    "yearBuilt", "daysOnMarket", "isPriceReduced", "agentName", "agentPhone",
    "officeName", "url",
]
AGENT_COLUMNS = [
    "agentName", "brokerName", "agentPhone", "agentEmail", "soldLastYearCount",
    "forSaleListingsCount", "realtorRating", "realtorReviewCount",
    "yearsExperienceLabel", "agentProfileUrl",
]


def price_per_sqft(rec: dict) -> float | None:
    if rec.get("pricePerSqft"):
        return float(rec["pricePerSqft"])
    if rec.get("listPrice") and rec.get("sqft"):
        return rec["listPrice"] / rec["sqft"]
    return None


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    load_dotenv()
    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        sys.exit("APIFY_API_TOKEN missing - copy .env.example to .env first.")

    client = ApifyClient(token)
    out = Path(__file__).parent

    # Step 1: for-sale listings with ZIP medians attached
    print(f"Step 1/3 - for-sale listings in {', '.join(ZIPS)}")
    try:
        run = client.actor(ACTOR_ID).call(
            run_input={
                "scrapeType": "search",
                "location": ZIPS,
                "listingType": "for_sale",
                "propertyType": ["single_family", "townhome", "condo"],
                "bedsMin": 2,
                "includeMarketStats": True,
                "includePermits": False,
                "maxItems": LISTINGS_PER_ZIP * len(ZIPS),
            },
            timeout_secs=1800,
        )
    except ApifyApiError as exc:
        sys.exit(f"Search step failed: {exc}")

    listings = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    print(f"  {len(listings)} listings collected")

    # Step 2: keep what is priced under its own ZIP median
    underpriced = []
    for rec in listings:
        ppsf = price_per_sqft(rec)
        median = rec.get("neighborhoodMedianPricePerSqft")
        if not ppsf or not median:
            continue
        discount = 1 - ppsf / median
        if discount >= DISCOUNT:
            rec["discountPct"] = round(discount * 100, 1)
            underpriced.append(rec)
    underpriced.sort(key=lambda r: -r["discountPct"])

    print(f"\nStep 2/3 - {len(underpriced)} listings at least "
          f"{int(DISCOUNT * 100)}% under their ZIP median $/sqft")
    for r in underpriced[:12]:
        print(f"  -{r['discountPct']:>5}%  {r.get('postalCode')}  "
              f"${r.get('listPrice') or 0:>9,}  {r.get('sqft') or '-':>5} sqft  "
              f"{r.get('daysOnMarket') or '-':>4} DOM  {r.get('addressLine')}")

    (out / "output.json").write_text(
        json.dumps(underpriced, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(out / "output.csv", underpriced, LISTING_COLUMNS)

    # Step 3: the local agents worth calling
    print(f"\nStep 3/3 - top agents in {CITY}")
    try:
        agent_run = client.actor(ACTOR_ID).call(
            run_input={
                "scrapeType": "agents",
                "location": [CITY],
                "includeAgentProfile": True,
                "includeReviews": False,
                "maxItems": AGENTS,
            },
            timeout_secs=1800,
        )
    except ApifyApiError as exc:
        print(f"  agents step failed: {exc}")
        return 0

    agents = list(client.dataset(agent_run["defaultDatasetId"]).iterate_items())
    agents.sort(key=lambda a: (-(a.get("soldLastYearCount") or 0),
                               -(a.get("realtorRating") or 0)))
    write_csv(out / "agents.csv", agents, AGENT_COLUMNS)

    for a in agents[:10]:
        print(f"  {a.get('soldLastYearCount') or 0:>4} sold/12mo  "
              f"{a.get('realtorRating') or '-':>4} stars  "
              f"{(a.get('agentName') or '-')[:28]:<28}  {a.get('brokerName') or ''}")

    print("\nSaved output.json, output.csv and agents.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
