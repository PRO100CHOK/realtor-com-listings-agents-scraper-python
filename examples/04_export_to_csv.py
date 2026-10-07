"""Rental shortlist to CSV with pandas: dog-friendly 2-bed rentals under budget.

`listingType: for_rent` switches the search to rentals; `listPrice` is then the
monthly rent. Pet policy comes back as `petsDogs` / `petsCats`.

Actor: https://apify.com/pro100chok/realtor-com-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python
"""
import os

import pandas as pd
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/realtor-com-scraper").call(run_input={
    "scrapeType": "search",
    "location": ["Minneapolis, MN"],
    "listingType": "for_rent",
    "bedsMin": 2,
    "priceMax": 2600,
    "includeMarketStats": False,
    "includePermits": False,
    "maxItems": 150,
})

df = pd.DataFrame(client.dataset(run["defaultDatasetId"]).list_items().items)
if df.empty:
    raise SystemExit("No rentals returned - try a wider price range.")

cols = ["addressLine", "city", "postalCode", "listPrice", "beds", "baths", "sqft",
        "petsDogs", "petsCats", "listDate", "officeName", "officePhone", "url"]
df = df[[c for c in cols if c in df.columns]]

if "petsDogs" in df.columns:
    df = df[df["petsDogs"].fillna(False).astype(bool)]
if "sqft" in df.columns:
    df["rentPerSqft"] = (df["listPrice"] / df["sqft"]).round(2)
    df = df.sort_values("rentPerSqft")

df.to_csv("output.csv", index=False)
df.to_json("output.json", orient="records", indent=2)
print(f"{len(df)} dog-friendly rentals saved to output.csv")
print(df.head(10).to_string(index=False))
