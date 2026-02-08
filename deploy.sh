#!/bin/bash
# Quick Deploy Script for YARS with Anti-Detection + Proxy Rotation
# Pushes updated scraper to Apify

echo "=================================="
echo "YARS Deployment Script"
echo "Anti-Detection v2.1 + Proxy Rotation"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "yars.py" ]; then
    echo "❌ Error: yars.py not found. Run this from the project root."
    exit 1
fi

# Check if apify CLI is installed
if ! command -v apify &> /dev/null; then
    echo "❌ Apify CLI not installed. Install with: npm install -g apify-cli"
    exit 1
fi

echo ""
echo "📦 Checking dependencies..."
cat requirements.txt
echo ""

echo "✅ Files to deploy:"
echo "  - yars.py (with curl_cffi + anti-detection + proxy rotation)"
echo "  - config.py"
echo "  - utils.py"
echo "  - src.py (Apify entry point with proxy rotation)"
echo "  - requirements.txt (with curl_cffi)"
echo "  - Dockerfile"
echo ""

read -p "🚀 Ready to deploy to Apify? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "📤 Pushing to Apify..."
    apify push
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Deployment successful!"
        echo ""
        echo "🔗 Next steps:"
        echo "  1. Go to: https://console.apify.com/actors/tm7cbjgzrOQaRmPzV"
        echo "  2. Wait for build to complete"
        echo "  3. Test with:"
        echo "     - startUrls: ['https://www.reddit.com/r/Python/']"
        echo "     - searches: ['AI', 'machine learning']"
        echo "     - proxy: { useApifyProxy: true, apifyProxyGroups: ['RESIDENTIAL'] }"
        echo "  4. Check for 403 errors in logs (should be 0!)"
        echo ""
    else
        echo ""
        echo "❌ Deployment failed. Check errors above."
        exit 1
    fi
else
    echo ""
    echo "⏸️  Deployment cancelled."
    exit 0
fi
