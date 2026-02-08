# Next Steps - Deployment Checklist

## ✅ What's Already Done

- ✅ Anti-detection features implemented (Options A & B)
- ✅ curl_cffi TLS fingerprinting active
- ✅ Browser headers, cookies, delays configured
- ✅ Smart retry with exponential backoff
- ✅ old.reddit.com fallback for search
- ✅ Tests passed (7/7 - 100%)
- ✅ Documentation updated
- ✅ Deploy script created

## 🚀 What You Need to Do

### 1. Test Locally (Optional but Recommended)

```bash
# Run the test suite
python3 test_improvements.py

# Test a real search
python3 main.py --search "Python AI" --limit 5 --debug

# Test subreddit scraping
python3 main.py --url "https://www.reddit.com/r/MachineLearning/" --limit 5
```

Expected: No 403 errors, clean results.

---

### 2. Deploy to Apify

**Option A: Using the deploy script**
```bash
./deploy.sh
```

**Option B: Manual deployment**
```bash
apify push
```

This will:
- Upload all files to Apify
- Build Docker image with curl_cffi
- Deploy as Actor version 1.0.10 (or next available)

---

### 3. Test on Apify Platform

1. Go to: https://console.apify.com/actors/tm7cbjgzrOQaRmPzV

2. Wait for build to complete (2-3 minutes)

3. Click **Start** and use this test input:

```json
{
  "startUrls": [
    "https://www.reddit.com/r/Python/"
  ],
  "searches": [
    "artificial intelligence",
    "machine learning"
  ],
  "searchPosts": true,
  "searchCommunities": true,
  "maxItems": 20,
  "maxPostCount": 10,
  "skipComments": true,
  "proxy": {
    "useApifyProxy": true,
    "apifyProxyGroups": ["RESIDENTIAL"]
  },
  "debugMode": true
}
```

4. Monitor the logs for:
   - ✅ "Session initialized (Status: 200)"
   - ✅ "Response status: 200" (not 403!)
   - ✅ "Modern Reddit blocked, trying old.reddit.com..." (if needed)
   - ✅ Results being pushed to dataset

5. Check **Dataset** tab - should have ~20 items

---

### 4. Verify No 403 Errors

In the Actor logs, search for "403" - there should be **zero or very few** occurrences.

**Before upgrade:**
```
❌ BLOCKED: https://www.reddit.com/search.json - Anti-bot detection
❌ BLOCKED: https://www.reddit.com/search.json - Anti-bot detection
❌ BLOCKED: https://www.reddit.com/search.json - Anti-bot detection
```

**After upgrade:**
```
✅ Response status: 200
✅ Response received with 10 children
✅ Modern Reddit blocked, trying old.reddit.com...
✅ Response status: 200 (on fallback)
```

---

## 📊 Success Criteria

| Metric | Target | How to Check |
|--------|--------|--------------|
| Build Success | ✅ Pass | Build completes without errors |
| Session Init | ✅ 200 | Log shows "Session initialized (Status: 200)" |
| Search Success | ✅ >90% | Most searches return 200, not 403 |
| Results Returned | ✅ >0 | Dataset has items |
| 403 Error Rate | ✅ <10% | Very few "BLOCKED" messages in logs |

---

## 🐛 If Something Goes Wrong

### Build Fails with "curl_cffi not found"
```bash
# Check requirements.txt has:
cat requirements.txt | grep curl_cffi

# Should show:
# curl_cffi>=0.5.10
```

### Still Getting 403s on Apify
1. **Check proxy is enabled:**
   - Input JSON must have `"useApifyProxy": true`
   - Use `"RESIDENTIAL"` proxy group (not datacenter)

2. **Try country restriction:**
   ```json
   "proxy": {
     "useApifyProxy": true,
     "apifyProxyGroups": ["RESIDENTIAL"],
     "apifyProxyCountry": "US"
   }
   ```

3. **Check Actor logs:**
   - Look for "Session initialized" - should be 200
   - Look for "Using curl_cffi" message
   - If modern Reddit fails, should see "trying old.reddit.com"

### Tests Failing Locally
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Try just curl_cffi
pip install curl-cffi

# Run one test
python3 -c "from curl_cffi import requests; print(requests.get('https://www.reddit.com/').status_code)"
# Should print: 200
```

---

## 📈 Monitor After Deployment

### First 24 Hours
- Run Actor 5-10 times with different inputs
- Check logs for 403 patterns
- Monitor success rate in Runs history

### First Week
- Schedule regular runs
- Track error rates
- Adjust proxy settings if needed

---

## 🎯 Performance Expectations

### Before Upgrade
- Search: 20% success (80% blocked with 403)
- Speed: Fast but unreliable
- Subreddits: 100% success ✅

### After Upgrade
- Search: 90-100% success 🎉
- Speed: Slightly slower (1.5-3s delays) but more reliable
- Subreddits: 100% success ✅

**Trade-off:** Slightly slower but WAY more reliable!

---

## 📚 Reference Documentation

- **IMPROVEMENTS.md** - Technical details of all changes
- **UPGRADE_SUMMARY.md** - Overview of what was upgraded
- **PROJECT_STATUS.md** - Updated project status
- **test_improvements.py** - Local testing

---

## 🎉 You're Ready!

Everything is implemented and tested. Just run:

```bash
./deploy.sh
```

Then test on Apify with residential proxies!

**Expected Result:** 0% 403 errors on search endpoints! 🚀
