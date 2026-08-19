# PeerSpot Reviews Scraper

Extract verified B2B software reviews, ratings, and user testimonials from PeerSpot.com - the leading platform for enterprise technology decision makers.

## What it Does

This actor scrapes:
- ✅ Product reviews with star ratings (1-5)
- ✅ Reviewer names, titles, and companies
- ✅ Full review text with pros/cons
- ✅ Review publication dates
- ✅ Product comparisons and insights

## Use Cases

- **AI/LLM Integration**: Connect via Apify MCP to Claude, ChatGPT, or any AI agent
- **Market Research**: Analyze competitor products and user sentiment
- **Lead Generation**: Find decision makers reviewing specific software categories
- **Product Intelligence**: Track user feedback on enterprise software products

## Input

| Field | Type | Description |
|-------|------|-------------|
| `searchQuery` | string | Search for products by keyword (e.g., "CRM", "firewall") |
| `categoryUrl` | string | URL of a PeerSpot category page |
| `productUrls` | array | List of specific product review page URLs |
| `maxResults` | integer | Maximum number of reviews to scrape (default: 100) |

## Example Input

```json
{
  "searchQuery": "firewall",
  "maxResults": 50
}
```

Or scrape a specific category:

```json
{
  "categoryUrl": "https://www.peerspot.com/categories/firewalls",
  "maxResults": 100
}
```

## Output

Each review includes:

```json
{
  "productName": "Microsoft Power BI",
  "reviewText": "PeerSpot is a goldmine...",
  "rating": "4",
  "reviewerName": "Brian H.",
  "reviewerTitle": "Principal DevOps Engineer at a large healthcare company",
  "reviewDate": "Jul 20, 2026",
  "sourceUrl": "https://www.peerspot.com/products/microsoft-power-bi-reviews",
  "scrapedAt": "2026-08-19T06:30:00.000Z"
}
```

## Pricing

- $0.005 per review (result)
- $0.05 one-time actor start fee

## Works With

- ✅ Claude via Apify MCP
- ✅ ChatGPT via Apify Integration
- ✅ Any AI agent with Apify connector

## Technical Details

- **No bot protection**: Clean HTML scraping with httpx
- **Fast**: 100 reviews in ~2-3 minutes
- **Reliable**: Built-in retry logic and error handling

## Notes

- PeerSpot has 910,000+ enterprise tech professionals
- All reviews are verified real users within the last 12 months
- Average review length: 600 words

## Support

Issues or questions? Contact the developer via [Apify Console](https://console.apify.com/actors/fervent_bus~peerspot-scraper).
