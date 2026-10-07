"""Realtor.com agents in a city with star ratings and real client review text.

`scrapeType: agents` returns agents for a location. `includeReviews` matches
each agent to their public client reviews (text, customer type, date) and
`includeAgentProfile` adds bio, years of experience, languages and areas.

Actor: https://apify.com/pro100chok/realtor-com-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python
"""
import os

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/realtor-com-scraper").call(run_input={
    "scrapeType": "agents",
    "location": ["Scottsdale, AZ"],
    "includeAgentProfile": True,
    "includeReviews": True,
    "maxItems": 30,
})

agents = list(client.dataset(run["defaultDatasetId"]).iterate_items())
agents.sort(key=lambda a: -(a.get("realtorReviewCount") or 0))

for a in agents[:15]:
    print(f"\n{a.get('agentName')} - {a.get('brokerName') or a.get('officeName') or ''}")
    print(f"  {a.get('realtorRating') or '-'} stars, {a.get('realtorReviewCount') or 0} reviews | "
          f"{a.get('soldLastYearCount') or 0} sold in 12 mo | "
          f"{a.get('yearsExperienceLabel') or 'experience n/a'} | {a.get('agentPhone') or ''}")
    if a.get("languages"):
        print(f"  languages: {a['languages']}")
    for rv in (a.get("reviews") or [])[:2]:
        text = (rv.get("text") or "")[:160]
        print(f"  \"{text}\" - {rv.get('customerType') or 'client'}, {rv.get('date') or ''}")
