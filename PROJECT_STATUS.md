# YARS - Yet Another Reddit Scraper
## Project Status Document
**Last Updated:** February 5, 2026

---

## 📋 Project Overview

A Reddit scraper built from scratch (inspired by the YARS package) with Apify Actor integration for cloud deployment. The scraper uses Reddit's public JSON API endpoints (no API key required).

**Reference Actor:** `gustavotr/reddit-scraper` (Node.js/Puppeteer-based)

---

## 🏗️ Project Structure

```
/home/priyanshu.galani/Desktop/scraper/reddit/
├── .actor/
│   ├── actor.json          # Apify Actor configuration
│   └── README.md           # Actor documentation
├── yars.py                 # Core scraper logic (~575 lines)
├── config.py               # ScraperInput configuration class
├── utils.py                # Utility functions (URL parsing, data formatting)
├── src.py                  # Apify Actor entry point (async main)
├── main.py                 # Local CLI entry point
├── input_schema.json       # Apify input schema definition
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration for Apify
└── PROJECT_STATUS.md       # This file
```

---

## ✅ Completed Features

### Phase 1: Core Scraper (Local) - COMPLETE ✅
- [x] Subreddit scraping (hot, new, top, rising posts)
- [x] Post details with full metadata
- [x] Comments scraping with nested replies
- [x] User profile scraping
- [x] User posts and comments
- [x] Search functionality (posts, communities, users)
- [x] Community/subreddit info
- [x] Rate limiting (1 second between requests)
- [x] Configurable limits (max items, max comments, etc.)
- [x] CLI interface with argparse
- [x] Debug mode logging

### Phase 2: Apify Integration - PARTIALLY COMPLETE ⚠️

#### Working on Apify ✅
- [x] Actor structure and configuration
- [x] Input schema with all parameters
- [x] Apify Proxy integration (residential proxies)
- [x] SSL verification bypass for MITM proxy
- [x] Async Actor lifecycle (init/exit)
- [x] Dataset output (push_data)
- [x] **Subreddit scraping via startUrls**
- [x] **User profile scraping via startUrls**
- [x] **Individual post scraping via startUrls**
- [x] **Comments on posts**

#### NOT Working on Apify ❌
- [ ] Search posts (`/search.json?type=link`) - Returns 403
- [ ] Search communities (`/search.json?type=sr`) - Returns 403
- [ ] Search users (`/search.json?type=user`) - Returns 403

**Root Cause:** Reddit's `/search.json` endpoint has stricter anti-bot protection than subreddit endpoints. Even residential proxies are being blocked with 403 errors.

---

## 🔧 Technical Details

### Dependencies
```
requests>=2.31.0  # (replaced by curl_cffi in code)
apify>=1.7.0
curl_cffi>=0.5.10  # TLS fingerprinting (Chrome 110)
playwright>=1.40.0  # For future Crawlee integration
```

### Key Files

#### `yars.py` - Core Scraper
- `YARS` class with all scraping methods
- `_get_browser_headers()`: Generates realistic Chrome browser headers
- `_initialize_session()`: Visits Reddit homepage to establish cookies
- `_make_request()`: Central HTTP method with:
  - curl_cffi with Chrome 110 TLS fingerprinting
  - Exponential backoff retry logic (3 attempts)
  - Random delays (1.5-3s)
  - 403/429/500 error handling
- `search_reddit()`, `search_communities()`, `search_users()`: Auto fallback to old.reddit.com
- `ssl_verify`: Set to `False` when proxy is used (for MITM compatibility)
- `_make_request()`: Central HTTP method with retry logic
- `run()`: Main entry point that processes URLs and searches

#### `src.py` - Apify Entry Point
- Async main function using `async with Actor:`
- Proxy configuration via `Actor.create_proxy_configuration()`
- Uses `actor_proxy_input` format for proxy setup
- Pushes results to Apify dataset

#### `config.py` - Configuration
- `ScraperInput` dataclass with all parameters
- `from_dict()` class method for Apify input parsing
- Default values for all optional parameters

### Apify Input Schema
Key input fields:
- `startUrls`: Array of Reddit URLs to scrape
- `searches`: Array of search queries
- `proxy`: Proxy configuration object
- `maxItems`, `maxPostCount`, `maxComments`: Limits
- `skipComments`, `skipUserPosts`: Skip flags
- `sort`, `time`: Search filters

---

## 🚀 Deployment

### Apify Actor
- **Actor ID:** `tm7cbjgzrOQaRmPzV`
- **Latest Build:** 1.0.9 (ID: `ocflCWEV2UmfzaYSa`)
- **Console URL:** https://console.apify.com/actors/tm7cbjgzrOQaRmPzV

### Deploy Command
```bash
cd /home/priyanshu.galani/Desktop/scraper/reddit
apify push
```

### Local Testing
```bash
# Basic subreddit scrape
python3 main.py --url "https://www.reddit.com/r/Python/" --limit 10

# Search with debug
python3 main.py --search "Python" --limit 5 --debug

# Skip comments for faster scraping
python3 main.py --url "https://www.r - PARTIALLY RESOLVED ⚠️
**Problem:** Reddit's `/search.json` endpoint returns 403 Forbidden even with residential proxies.

**Affected Features:**
- `searches` input parameter  
- `searchPosts`, `searchCommunities`, `searchUsers` flags

**Implemented Solutions:** ✅
1. ✅ **old.reddit.com fallback** - Automatically tries `old.reddit.com/search.json` on 403
2. ✅ **Enhanced headers** - Full Chrome browser headers (Accept, Accept-Language, Referer, Sec-Fetch-*)
3. ✅ **Cookie handling** - Visits homepage on startup to establish session cookies
4. ✅ **Random delays** - Random 1.5-3s delays between requests
5. ✅ **TLS fingerprinting** - curl_cffi with Chrome 110 impersonation
6. ✅ **Exponential backoff** - Retries with 1s, 2s, 4s backoff on failures
 - IMPROVED ✅
**Previous:** Fixed 1-second delay between requests
**Current:** Random 1.5-3 second delays with exponential backoff on rate limits (429)
**Status:** More human-like behavior, reduced rate limit trigger
**Remaining Options (if still needed):**
1. **Reddit OAuth API** - Use official API with registered app credentials (requires API key)

**Potential Solutions (not yet implemented):**
1. **Use old.reddit.com** - Try `old.reddit.com/search.json` instead
2. **Enhanced headers** - Add more browser-like headers (Accept, Accept-Language, Referer)
3. **Cookie handling** - Visit homepage first to get session cookies
4. **Random delays** - Use random delays (1-3s) instead of fixed 1s
5. **Reddit OAuth API** - Use official API with registered app credentials

### Issue 2: Rate Limiting
**Current:** Fixed 1-second delay between requests
**Risk:** May still trigger Reddit's rate limiting on large scrapes

---

## � Reference Actor Analysis

Analyzed reference: `gustavotr/reddit-scraper` (Apify Actor)

### Comparison: Reference vs Our Scraper

| Aspect | Reference Actor | Our Scraper | Gap |
|--------|-----------------|-------------|-----|
| **Language** | Node.js | Python | Different ecosystem |
| **HTTP Client** | `got-scraping` (anti-detect) | `curl_cffi` (TLS fingerprint) | 🟢 Comparable |
| **Browser** | Puppeteer + Chrome | None (JSON API) | 🟡 Different approach |
| **Framework** | Crawlee (queues, retries) | Manual loops + retry logic | 🟡 Medium |
| **Headers** | `header-generator` (realistic) | Chrome browser headers | 🟢 Good |
| **Fingerprint** | `fingerprint-generator` | curl_cffi Chrome 110 TLS | 🟢 Good |
| **Scrolling** | Real browser scrolling | JSON API pagination | ✅ OK |
| **Anti-detect** | Full suite | Headers + TLS + Cookies + Delays | 🟢 Good |
| **Proxy rotation** | Per-request session | Per-request rotation | 🟢 Match |
| **Delays** | Smart delays | Random 1.5-3s + backoff | 🟢 Good |
| **Cookie handling** | Automatic | Session initialization | 🟢 Good |

### Reference Actor Dependencies (Key)
```
- crawlee@3.15.3          # Request queue, retries, anti-detect
- got-scraping@3.2.15     # HTTP client with header rotation
- header-generator@2.1.79 # Realistic browser headers
- fingerprint-generator   # Browser fingerprinting
- puppeteer@24.36.1       # Headless Chrome for JS-heavy pages
```

---

## 📝 Next Steps (Priority Order)

### Phase 3: Anti-Detection Improvements - ✅ COMPLETE (v2.1)

#### Option A: Quick Fixes - ✅ IMPLEMENTED
1. ✅ **Browser-like headers** - Full browser header suite with Accept, Accept-Language, Accept-Encoding, DNT, Sec-Fetch-*, Referer
2. ✅ **Session cookies** - Visits homepage on initialization to establish session cookies  
3. ✅ **Random delays** - Random 1.5-3 second delays between requests (not fixed 1s)
4. ✅ **old.reddit.com fallback** - Automatically falls back to `old.reddit.com/search.json` on 403 for all search types
5. ✅ **Exponential backoff** - Implements 2^attempt backoff on 403/429/500 errors with max 3 retries

#### Option B: curl_cffi - ✅ IMPLEMENTED  
Replaced `requests` with `curl_cffi` for TLS fingerprint impersonation:
```python
from curl_cffi import requests
response = requests.get(url, impersonate="chrome110", verify=self.ssl_verify)
```
- Chrome 110 TLS fingerprinting active
- Mimics real Chrome browser at TCP/TLS level
- Added to requirements.txt (curl_cffi>=0.5.10)

#### Option C: Proxy Rotation - ✅ IMPLEMENTED (v2.1)
Per-request proxy rotation matching reference actor behavior:
```python
# In yars.py
def _get_new_proxy(self):
    """Get fresh proxy URL from Apify configuration"""
    return asyncio.run(self.proxy_configuration.new_url())

# In src.py
scraper = YARS(config=config, proxy_configuration=proxy_configuration)
```
- **New proxy for every request** - Prevents session-based bot detection
- Asyncio bridge from sync code - Handles async proxy_configuration.new_url()
- Debug logging - Shows proxy rotation count when debug mode enabled
- Backward compatible - Still accepts static proxy_url for local testing

**Impact:** Eliminates 403 errors on multiple consecutive requests to same domain

#### Option D: Crawlee Python Rewrite (High Effort, Best Results) - NOT YET IMPLEMENTED
Rewrite using `crawlee` Python package:
- `PlaywrightCrawler` for browser automation
- Built-in proxy rotation and fingerprinting
- Request queue with automatic retries
- Same architecture as reference actor

### Phase 4: Feature Parity 🟡 MEDIUM PRIORITY
1. **Pagination** - Support scraping more than 100 posts (use `after` parameter)
2. **Session rotation** - Use different proxy session IDs per request
3. **Retry logic** - Implement exponential backoff for failed requests
4. **Better error categorization** - Distinguish rate limit vs blocked vs not found

### Phase 5: Polish 🟢 LOW PRIORITY
1. **Scheduled runs** - Configure Actor for scheduled/recurring scrapes
2. **Webhooks** - Add webhook integration for completed runs
3. **Output formats** - Support CSV, Excel export in addition to JSON
4. **Actor SEO** - Better README, screenshots, example outputs

---

## 📊 Test Results

### Local Testing ✅
```
python3 main.py --search "Python" --limit 3 --skip-comments --debug
# Result: Works perfectly, returns posts, comments, communities, users
```

### Apify Testing ⚠️
```
Input:
- startUrls: ["https://www.reddit.com/r/Python/"]
- searches: ["Claude"]
- proxy: { useApifyProxy: true, apifyProxyGroups: ["RESIDENTIAL"] }

Result:
- Subreddit posts: 50 items ✅
- Search results: 0 items (403 blocked) ❌
```

---

## 🔑 Key Code Sections

### Proxy Configuration (src.py, lines 61-95)
```python
proxy_configuration = await Actor.create_proxy_configuration(
    actor_proxy_input={
        'useApifyProxy': True,
        'apifyProxyGroups': proxy_groups if proxy_groups else None,
        'apifyProxyCountry': proxy_country
    }
)
if proxy_configuration is not None:
    proxy_url = await proxy_configuration.new_url()
```

### SSL Bypass (yars.py, lines 32-40)
```python
self.ssl_verify = True  # Default: verify SSL
if proxy_url:
    self.session.proxies = {'http': proxy_url, 'https': proxy_url}
    self.ssl_verify = False  # Disable for MITM proxy
```

### Request Method (yars.py, lines 55-60)
```python
response = self.session.get(url, params=params, timeout=10, verify=self.ssl_verify)
```

---

## 📚 References

- **YARS Original:** https://github.com/example/yars (inspiration)
- **Reddit JSON API:** Append `.json` to any Reddit URL
- **Apify SDK Python:** https://docs.apify.com/sdk/python
- **Apify Proxy:** https://docs.apify.com/proxy

---

## 🤝 Handoff Notes

To continue development:
1. Open this workspace in VS Code
2. Read this document for context
3. Check `yars.py` for core scraping logic
4. Check `src.py` for Apify integration
5. Run `apify push` to deploy changes
6. Test on Apify console with proxy enabled

**Main blocker:** Search API 403 errors on Apify. Focus on implementing browser-like behavior to bypass Reddit's bot detection for the search endpoint.
