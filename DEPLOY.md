# 🚀 Deployment Guide - YARS Apify Actor

This guide walks you through deploying YARS as an Apify Actor.

## 📋 Prerequisites

1. **Apify Account**: Sign up at https://apify.com (free tier available)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Apify CLI** (optional, for local testing):
   ```bash
   npm install -g apify-cli
   apify login
   ```

## 🎯 Deployment Methods

### Method 1: Deploy via GitHub (Recommended)

This is the easiest method and enables automatic updates.

#### Step 1: Push to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit: YARS Reddit Scraper"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/yars-reddit-scraper.git
git push -u origin main
```

#### Step 2: Connect to Apify

1. Log in to [Apify Console](https://console.apify.com/)
2. Go to **Actors** → **Create new**
3. Select **Import from GitHub**
4. Connect your GitHub account (if not already connected)
5. Select your repository: `YOUR_USERNAME/yars-reddit-scraper`
6. Choose branch: `main`
7. Click **Create**

#### Step 3: Build & Run

1. Apify will automatically:
   - Detect the Dockerfile
   - Read `.actor/actor.json` for configuration
   - Build the Docker image
   - Deploy the Actor

2. Once built, you can:
   - Click **Start** to run the Actor
   - Use the input form (auto-generated from `input_schema.json`)
   - View results in the **Dataset** tab

### Method 2: Deploy via Apify CLI

For developers who prefer command-line deployment.

#### Step 1: Install Apify CLI

```bash
npm install -g apify-cli
apify login
```

#### Step 2: Initialize Actor

```bash
cd /path/to/your/scraper
apify init
```

When prompted:
- Actor name: `yars-reddit-scraper`
- Template: Choose **Skip** (we already have the files)

#### Step 3: Deploy

```bash
# Build and push to Apify
apify push

# Run the Actor
apify run
```

### Method 3: Manual Zip Upload

For quick testing without Git/GitHub.

#### Step 1: Create Zip File

```bash
cd /home/priyanshu.galani/Desktop/scraper/reddit
zip -r yars-actor.zip . -x "venv/*" "__pycache__/*" "*.pyc" "test_*.json" "*.jpg"
```

#### Step 2: Upload to Apify

1. Go to [Apify Console](https://console.apify.com/)
2. **Actors** → **Create new** → **Import from ZIP**
3. Upload `yars-actor.zip`
4. Wait for build to complete
5. Run the Actor

## 🔧 Configuration on Apify

### Input Configuration

The Actor accepts inputs via the Apify web UI form. All parameters from `input_schema.json`:

**Basic Options:**
- Start URLs (array of Reddit URLs)
- Searches (array of search terms)
- Max Items, Posts, Comments, Communities, Users

**Filtering:**
- Sort by: relevance, hot, new, top, comments
- Time filter: hour, day, week, month, year, all

**Advanced:**
- Skip options (comments, communities, users)
- Proxy configuration
- Debug mode

### Storage & Datasets

Results are automatically saved to:
- **Default dataset**: All scraped items
- **Key-value store**: Actor metadata

Access via:
```python
# Apify SDK automatically handles this
await Actor.push_data(items)  # Saves to dataset
```

### Scheduled Runs

Set up automatic scraping:

1. Go to your Actor → **Schedule**
2. Click **Create new schedule**
3. Configure:
   - Name: "Daily Python posts"
   - Cron expression: `0 9 * * *` (9 AM daily)
   - Input JSON with your searches
4. Save

### Webhooks

Get notified when runs complete:

1. Actor → **Webhooks** → **Add webhook**
2. Events: `ACTOR.RUN.SUCCEEDED`, `ACTOR.RUN.FAILED`
3. Webhook URL: Your endpoint
4. Apify will POST run results to your URL

## 🧪 Testing

### Local Testing (without Apify platform)

```bash
python3 test_actor.py
```

This simulates the Actor environment locally.

### Apify Local Testing (with Apify CLI)

```bash
# Install dependencies
apify install

# Run locally with Apify environment
apify run

# Run with specific input
apify run --input='{"searches": ["Python"], "maxItems": 10}'
```

### Testing on Apify Platform

1. Go to your Actor page
2. Click **Start**
3. Fill input form or paste JSON
4. Click **Start** again
5. Monitor logs in real-time
6. Check **Dataset** tab for results

## 📊 Monitoring & Logs

### View Logs

- **Real-time**: Click on running Actor → **Log** tab
- **Historical**: Actor → **Runs** → Select run → **Log**

### Check Results

- **Dataset**: Actor → **Runs** → Select run → **Dataset**
- **API Access**: 
  ```bash
  curl https://api.apify.com/v2/datasets/DATASET_ID/items
  ```

### Download Results

From Apify Console:
- Dataset → **Export** → Choose format (JSON, CSV, Excel, etc.)

## 💰 Cost Optimization

### Free Tier Limits
- **Compute**: 5 hours/month free
- **Storage**: 1 GB dataset storage
- **Proxies**: Limited free proxies

### Tips to Save Compute Units
1. Use `maxItems`, `maxPostCount` limits
2. Skip unnecessary data (`skipComments: true`)
3. Use shorter time filters (`time: "day"`)
4. Run during off-peak hours
5. Set appropriate `maxConcurrency`

## 🔐 Proxy Configuration

### Using Apify Proxies

In input JSON:
```json
{
  "proxyConfiguration": {
    "useApifyProxy": true,
    "apifyProxyGroups": ["RESIDENTIAL"]
  }
}
```

Proxy groups:
- `RESIDENTIAL`: Best for Reddit (more expensive)
- `DATACENTER`: Faster, cheaper (may be blocked)

### Using Custom Proxies

```json
{
  "proxyConfiguration": {
    "useApifyProxy": false,
    "proxyUrls": [
      "http://user:pass@proxy1.com:8080",
      "http://user:pass@proxy2.com:8080"
    ]
  }
}
```

## 🐛 Troubleshooting

### Build Failures

**Error**: `Could not find requirements.txt`
- Ensure `requirements.txt` is in repository root

**Error**: `Python version mismatch`
- Check Dockerfile uses `python:3.11-slim`

### Runtime Errors

**Error**: `Actor.init() called before Actor.main()`
- Ensure `__main__.py` uses proper async pattern

**Error**: `Reddit API rate limit`
- Add delays between requests
- Use Apify proxies
- Reduce `maxItems`

### No Results

Check:
1. Input JSON is valid
2. Search terms have results on Reddit
3. Time filter isn't too restrictive
4. Logs for error messages

## 📚 Next Steps

After successful deployment:

1. **Integrate with your app**: Use Apify API
   ```python
   from apify_client import ApifyClient
   
   client = ApifyClient('YOUR_API_TOKEN')
   run = client.actor('YOUR_USERNAME/yars-reddit-scraper').call(
       run_input={'searches': ['Python'], 'maxItems': 100}
   )
   items = client.dataset(run['defaultDatasetId']).list_items().items
   ```

2. **Set up webhooks** for real-time notifications

3. **Schedule regular runs** for monitoring subreddits

4. **Export to external services** (Google Sheets, databases, etc.)

## 🆘 Support

- **Apify Docs**: https://docs.apify.com
- **Apify Discord**: https://discord.com/invite/jyEM2PRvMU
- **GitHub Issues**: Open an issue in your repository

## 📝 Version History

- **v1.0.0** - Initial release with search, URL scraping, Apify integration
- Future: Pagination, advanced filters, comment search

---

**Ready to deploy? Follow Method 1 above and you'll be scraping Reddit in minutes! 🎉**
