"""Sold-comps report for one ZIP: what homes like yours actually sold for.

Pulls homes sold in the last 120 days with `listingType: sold` and
`soldWithinDays`, narrows to a size band, and prints the median sold price per
square foot - the number a CMA starts from. `includeDetails` adds the full price
and tax history to each comp.

Actor: https://apify.com/pro100chok/realtor-com-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python
"""
import os
from statistics import median

from apify_client import ApifyClient
from dotenv import load_dotenv

ZIP = "80211"          # Highland / Sunnyside, Denver
SUBJECT_SQFT = 1600    # the home you are pricing

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/realtor-com-scraper").call(run_input={
    "scrapeType": "search",
    "location": [ZIP],
    "listingType": "sold",
    "soldWithinDays": 120,
    "propertyType": ["single_family"],
    "sqftMin": int(SUBJECT_SQFT * 0.8),
    "sqftMax": int(SUBJECT_SQFT * 1.2),
    "includeDetails": True,
    "includePermits": False,
    "maxItems": 40,
})

comps = []
for h in client.dataset(run["defaultDatasetId"]).iterate_items():
    price = h.get("lastSoldPrice") or h.get("listPrice")
    if not price or not h.get("sqft"):
        continue
    comps.append((price / h["sqft"], price, h))

for ppsf, price, h in sorted(comps, key=lambda c: c[0]):
    print(f"${ppsf:>6.0f}/sqft  ${price:>9,}  sold {h.get('lastSoldDate') or '-':<10}  "
          f"{h.get('sqft')} sqft  built {h.get('yearBuilt') or '-'}  {h.get('addressLine')}")

if comps:
    mid = median(c[0] for c in comps)
    print(f"\n{len(comps)} comps - median ${mid:,.0f}/sqft "
          f"-> about ${mid * SUBJECT_SQFT:,.0f} for a {SUBJECT_SQFT} sqft home")
