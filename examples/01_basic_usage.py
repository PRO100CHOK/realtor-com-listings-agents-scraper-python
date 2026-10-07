"""25 Realtor.com homes for sale in one city - the smallest useful call.

`location` accepts a city ("Austin, TX"), a ZIP ("78704"), a full address or
any realtor.com search URL. `listingType` defaults to for_sale.

Actor: https://apify.com/pro100chok/realtor-com-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python
"""
import os

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/realtor-com-scraper").call(run_input={
    "scrapeType": "search",
    "location": ["Raleigh, NC"],
    "listingType": "for_sale",
    "maxItems": 25,
})

for h in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(f"${h.get('listPrice') or 0:>10,}  {h.get('beds') or '-'}bd/{h.get('baths') or '-'}ba  "
          f"{h.get('sqft') or '-':>5} sqft  {h.get('daysOnMarket') or '-':>3} DOM  "
          f"{h.get('addressLine')}, {h.get('city')}")
