# Realtor.com Listings & Agents Scraper — Python Example

> Pull Realtor.com for-sale, rental, sold, pending and coming-soon listings, full property records and real-estate agents with ratings and reviews into Python — no Realtor.com API key, no login, no browser.

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-blue)](https://apify.com/pro100chok/realtor-com-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A ready-to-run Python project built on the [Realtor.com Scraper API actor on Apify](https://apify.com/pro100chok/realtor-com-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python). Clone it, add a token, and you have listings, property details and agent contacts flowing into JSON, CSV, pandas or Google Sheets in a few minutes.

## What this does

Realtor.com does not sell bulk access to its listing data. The developer APIs that exist are aimed at brokerages and MLS partners, and none of them hand you "every pending home in this ZIP" as a spreadsheet. This actor fills that gap as an unofficial Realtor.com API: you send a location or a listing URL, it returns structured records with the same data a visitor sees on the site — plus a few layers the site spreads across several pages.

One actor, three modes, chosen with `scrapeType`:

| `scrapeType` | You send | You get back |
|---|---|---|
| `search` | Cities, ZIPs, "City, ST", addresses or realtor.com search URLs | One record per listing — for sale, for rent, sold, pending or coming soon |
| `propertyDetail` | Listing URLs or numeric property IDs | The complete property record: tax and price history, schools, AVM estimates, risk scores, mortgage breakdown, all photos |
| `agents` | Cities, ZIPs or "City, ST" | Agents with phone, email, brokerage, sales production, star rating and client review text |

The scraping itself — residential proxy rotation, retries with a fresh fingerprint per attempt, pagination — runs on Apify. Your Python code only sends input and reads a dataset.

## Use cases

- **Underpriced-listing screens** — compare each home's price per sqft with its ZIP median (`neighborhoodMedianPricePerSqft`) and surface the outliers. That is what `main.py` does.
- **Comparable sales for a CMA** — `listingType: "sold"` plus `soldWithinDays` gives recent comps; turn on `includeDetails` for full price and tax history.
- **Agent recruiting and referral lists** — rank agents by `soldLastYearCount`, star rating and review count, with direct phone and email.
- **New-inventory alerts** — `listedWithinDays: 1` on a daily schedule catches listings the day they appear.
- **Pending and coming-soon tracking** — watch what goes under contract and what is about to list, before the general market reacts.
- **Rental market analysis** — `for_rent` listings with rent, unit mix and pet policy for underwriting a buy-and-hold deal.
- **Climate and insurance due diligence** — detail records carry flood, wildfire, heat, wind and air-quality scores with the FEMA flood zone.
- **Renovation history checks** — in covered metros each property gets its building permit history from city open data.

## Requirements

- Python **3.10+**
- A free [Apify account](https://console.apify.com/sign-up) — the free plan includes $5 of monthly credit
- **No** Realtor.com account, API key or proxy subscription

## Quick start

```bash
git clone https://github.com/pro100chok/realtor-com-listings-agents-scraper-python.git
cd realtor-com-listings-agents-scraper-python
pip install -r requirements.txt
cp .env.example .env
# paste your APIFY_API_TOKEN into .env
python main.py
```

`main.py` scans three south-Austin ZIP codes, keeps every for-sale home listed at least 10% below its ZIP's median price per square foot, then pulls the most active agents in Austin and ranks them by homes sold in the last 12 months. Results land in `output.json`, `output.csv` and `agents.csv`.

## How it works

1. `ApifyClient(token).actor("pro100chok/realtor-com-scraper").call(run_input=...)` starts a run and waits for it to finish.
2. The actor resolves each location, pages through results and applies your filters (beds, baths, price, sqft, lot size, year built, property type, listing age, sold window).
3. Optional enrichments run per record: `includeMarketStats` attaches ZIP, city and county medians; `includePermits` adds permit history; `includeDetails` upgrades a search card to the full detail record; `includeAgentProfile` and `includeReviews` deepen agent records.
4. Records stream into the run's default dataset. Read them with `client.dataset(run["defaultDatasetId"]).iterate_items()` or export the dataset as CSV/Excel straight from the Apify console.

Market medians are fetched once per ZIP and reused, so a search of 300 homes in one ZIP does not cost 300 extra lookups.

## Example output

A trimmed search record with market stats switched on:

```json
{
  "propertyId": "8742315520",
  "url": "https://www.realtor.com/realestateandhomes-detail/...",
  "status": "for_sale",
  "addressLine": "6612 Bluff Springs Rd",
  "city": "Austin",
  "stateCode": "TX",
  "postalCode": "78744",
  "listPrice": 379000,
  "pricePerSqft": 231,
  "beds": 3,
  "baths": 2,
  "sqft": 1641,
  "yearBuilt": 2004,
  "propertyType": "single_family",
  "daysOnMarket": 18,
  "isPriceReduced": true,
  "agentName": "Jane Example",
  "agentPhone": "512-555-0148",
  "officeName": "Example Realty Group",
  "neighborhoodMedianListPrice": 415000,
  "neighborhoodMedianPricePerSqft": 262,
  "neighborhoodMedianDaysOnMarket": 47
}
```

An agent record carries `agentName`, `agentEmail`, `agentPhone`, `brokerName`, `officeName`, `agentProfileUrl`, `realtorRating`, `realtorReviewCount`, `soldLastYearCount`, `forSaleListingsCount`, `forSalePriceMin`/`forSalePriceMax`, `yearsExperienceLabel`, `languages`, `servedAreas`, and — when public reviews exist — a `reviews` list with text, customer type and date.

## Input parameters

| Field | Type | Notes |
|---|---|---|
| `scrapeType` | string | `search` (default), `propertyDetail`, `agents` |
| `location` | array | Search and Agents modes: cities, ZIPs, "City, ST", addresses, realtor.com search URLs |
| `propertyUrls` | array | Property details mode: listing URLs or numeric property IDs |
| `listingType` | string | `for_sale`, `for_rent`, `sold`, `pending`, `coming_soon` |
| `propertyType` | array | `single_family`, `condo`, `townhome`, `multi_family`, `duplex_triplex`, `farm`, `land`, `mobile`, `apartment` |
| `bedsMin` / `bedsMax` / `bathsMin` | integer | Room filters |
| `priceMin` / `priceMax` | integer | USD; monthly rent for rentals |
| `sqftMin` / `sqftMax` / `lotSqftMin` | integer | Building and lot size |
| `yearBuiltMin` / `yearBuiltMax` | integer | Construction year range |
| `soldWithinDays` | integer | Sold searches only |
| `listedWithinDays` | integer | For-sale and rental searches only |
| `includeDetails` | boolean | Search: enrich each listing with the full detail record |
| `includeMarketStats` | boolean | ZIP/city/county medians (default on) |
| `includePermits` | boolean | Building permits in covered metros (default on) |
| `includeAgentProfile` / `includeReviews` | boolean | Agents: profile and client reviews (default on) |
| `maxItems` | integer | Records per run (default 100) |
| `maxRetries` | integer | Retries per blocked request (default 6) |
| `proxyConfiguration` | object | Defaults to Apify US residential |

## More examples

| File | What it shows |
|---|---|
| [`examples/01_basic_usage.py`](examples/01_basic_usage.py) | 25 for-sale homes in Raleigh, printed one line each |
| [`examples/02_sold_comps_report.py`](examples/02_sold_comps_report.py) | Sold comps in a Denver ZIP and a median $/sqft valuation |
| [`examples/03_agent_reviews.py`](examples/03_agent_reviews.py) | Scottsdale agents with ratings, sales count and review quotes |
| [`examples/04_export_to_csv.py`](examples/04_export_to_csv.py) | Dog-friendly Minneapolis rentals filtered in pandas, saved to CSV |
| [`examples/05_export_to_google_sheets.py`](examples/05_export_to_google_sheets.py) | Daily new-listing feed appended to a Google Sheet, de-duplicated |

## Ready-made tasks

Prefer clicking to coding? These saved configurations run the same actor from the Apify console:

- [Search Realtor.com listings in any location](https://apify.com/pro100chok/realtor-search-homes-for-sale?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python)
- [Pull recently sold comparables](https://apify.com/pro100chok/realtor-recently-sold-comps?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python)
- [Find Realtor.com agents with ratings and reviews](https://apify.com/pro100chok/realtor-agent-leads-with-reviews?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python)
- [Get property details, taxes and building permits](https://apify.com/pro100chok/realtor-property-details-and-permits?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python)
- [Export rentals for a whole market](https://apify.com/pro100chok/realtor-rental-market-listings?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python)
- [Catch new listings every day](https://apify.com/pro100chok/realtor-new-listings-daily-alert?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python)

## Pricing

Pay per result, proxies included. Current store prices per 1,000 records:

| Event | Free plan | Bronze | Gold and above |
|---|---|---|---|
| Property listing (search) | $4.00 | $1.50 | $1.30 |
| Property with full details | $5.00 | $4.00 | $3.50 |
| Real-estate agent | $5.00 | $3.00 | $3.00 |

Cap spend with `maxItems`, or set a maximum charge on the run in the Apify console.

## FAQ

**Is there an official Realtor.com API I could use instead?**
Not for this. Realtor.com's partner integrations are for listing syndication and lead delivery, not bulk export of search results, sold comps or agent directories. The [Realtor.com Scraper actor](https://apify.com/pro100chok/realtor-com-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python) reads the public site and returns it as data.

**How do I get pending or coming-soon homes?**
Set `listingType` to `pending` (contingent and pending listings) or `coming_soon`. Both work with the usual location and size filters.

**Where do agent reviews come from?**
Every agent includes Realtor.com's own `realtorRating` and `realtorReviewCount`. With `includeReviews` on, agents who publish client reviews publicly are matched and enriched with the full review text and satisfaction scores. Agents without public reviews still return contacts, brokerage and production numbers.

**Which cities have building permits?**
Major US metros that publish permit open data — Austin, New York City, Los Angeles, Chicago, San Francisco, Seattle, San Diego, Dallas, Denver, Washington DC, Boston and others. Elsewhere the field is simply absent.

**Why are some fields empty?**
Realtor.com does not publish every attribute for every home. Agent email, HOA fee or year built may be missing on the source page; the actor returns what exists rather than guessing.

**Can I run it on a schedule?**
Yes — create a schedule in the Apify console, or run `examples/05_export_to_google_sheets.py` from cron. Saved tasks (see above) can be scheduled directly.

## Related actors

- [Zillow Scraper API — listings, Zestimate and agents](https://apify.com/pro100chok/zillow-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python) — cross-check Realtor.com prices against Zestimates.
- [Apartments.com Scraper — rentals, prices and reviews](https://apify.com/pro100chok/apartments-scraper-usage?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python) — deeper multifamily rental data.
- [Idealista Scraper API — Spain and Italy](https://apify.com/pro100chok/idealista-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python) — the same workflow for Southern European property.
- [ImmobilienScout24 Scraper](https://apify.com/pro100chok/immobilienscout24-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python) — German listings with agent phones and emails.
- [Google Maps Scraper API — emails, reviews and leads](https://apify.com/pro100chok/google-maps-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python) — brokerages, inspectors and contractors around a market.

## License

MIT — see [LICENSE](LICENSE).

---

Built by [pro100chok](https://apify.com/pro100chok/realtor-com-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python). Not affiliated with Realtor.com or Move, Inc.
