# Apify Actor - YARS Reddit Scraper

This directory contains the Apify Actor configuration for YARS.

## Quick Start on Apify

1. Push this repository to GitHub
2. Create new Actor on [Apify Console](https://console.apify.com/)
3. Connect your GitHub repository
4. Deploy the Actor

## Local Testing

You can test the Actor locally before deploying:

```bash
# Install Apify CLI
npm install -g apify-cli

# Initialize (if needed)
apify init

# Run locally
apify run
```

## Input Configuration

The Actor accepts the same configuration as the standalone version, but through Apify's input interface:

- `startUrls` - Reddit URLs to scrape
- `searches` - Keywords to search for
- `maxItems` - Total items to scrape
- `skipComments` - Fast mode without comments
- `sort` - Sort method (relevance, hot, top, new)
- `time` - Time filter (hour, day, week, month, year, all)
- And many more...

See `.actor/input_schema.json` for the complete schema.

## Output

Results are saved to Apify dataset in the same format as the standalone version:

```json
{
  "dataType": "post",
  "title": "Post title",
  "username": "author",
  "upVotes": 1234,
  "createdAt": "2026-02-05T10:00:00Z"
  ...
}
```

## Features

✅ Apify Proxy integration (optional)
✅ Dataset storage
✅ Scheduled runs
✅ Web UI configuration
✅ Monitoring & alerts
✅ API access

## Pricing on Apify

- Free tier: $5 worth of platform credits per month
- Starter plan: $49/month for regular scraping
- See [Apify Pricing](https://apify.com/pricing) for details

## Support

For Actor-specific issues, please check:
- Apify documentation: https://docs.apify.com/
- Actor console logs
- Input/Output schemas
