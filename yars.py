"""
YARS - Yet Another Reddit Scraper
Enhanced version with Apify-compatible input system and anti-detection features
"""

from curl_cffi import requests
import json
import time
import random
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from config import ScraperInput
import re
import urllib3

# Suppress SSL warnings when using MITM proxy
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class YARS:
    """Yet Another Reddit Scraper - A comprehensive Reddit scraper using public JSON endpoints"""
    
    def __init__(self, config: ScraperInput = None, user_agent: str = None, proxy_url: str = None, proxy_configuration=None):
        """
        Initialize the scraper

        Args:
            config: ScraperInput configuration object
            user_agent: Custom user agent string
            proxy_url: Static proxy URL (deprecated, use proxy_configuration)
            proxy_configuration: Apify ProxyConfiguration object for rotating proxies
        """
        self.config = config or ScraperInput()
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        self.session = requests.Session()
        
        # Set default API headers (will be updated per-request as needed)
        self.session.headers.update(self._get_browser_headers(request_type='api'))

        # Store proxy configuration for rotation
        self.proxy_configuration = proxy_configuration
        self.proxy_url = proxy_url
        
        # Configure proxy if provided
        self.ssl_verify = True  # Default: verify SSL
        if proxy_url or proxy_configuration:
            # Disable SSL verification for MITM proxies (like Apify residential proxy)
            self.ssl_verify = False
            if proxy_configuration:
                self._log("Proxy rotation enabled - will get new proxy per request")
            else:
                self.session.proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                self._log("Static proxy configured - SSL verification disabled for MITM proxy")

        self.base_url = "https://www.reddit.com"

        # Track total items scraped for global limit
        self.total_items_scraped = 0
        self.results = []
        
        # Parse post date limit if provided
        self.post_date_limit_parsed = None
        if self.config.post_date_limit:
            try:
                self.post_date_limit_parsed = datetime.fromisoformat(self.config.post_date_limit.replace('Z', '+00:00'))
                self._log(f"Post date limit set to: {self.post_date_limit_parsed}")
            except (ValueError, AttributeError) as e:
                self._log(f"Warning: Invalid post_date_limit format: {self.config.post_date_limit}")
        
        # Request counter for proxy rotation logging
        self.request_count = 0

        # Initialize session with cookies
        self._initialize_session()

    def _get_browser_headers(self, referer=None, request_type='api'):
        """
        Generate realistic browser headers based on request type
        
        Args:
            referer: Referer URL (defaults to Reddit homepage)
            request_type: Type of request - 'api' for JSON endpoints, 'navigate' for HTML pages
        
        Returns:
            Dictionary of HTTP headers
        """
        # Base headers present in all requests
        headers = {
            'User-Agent': self.user_agent,
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': referer or 'https://www.reddit.com/',
        }
        
        # Request-type-specific headers
        if request_type == 'api':
            # For JSON API requests (like search.json, .json endpoints)
            headers.update({
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Content-Type': 'application/json',
                'Origin': 'https://www.reddit.com',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'X-Requested-With': 'XMLHttpRequest',
            })
        else:
            # For HTML navigation requests
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            })
        
        # Additional Chrome-specific headers (platform information)
        headers.update({
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="110", "Chromium";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        })
        
        return headers

    def _initialize_session(self):
        """Visit homepage to establish session cookies with realistic browsing pattern"""
        try:
            self._log("Initializing session...")
            
            # Get initial proxy if rotation is enabled
            if self.proxy_configuration:
                initial_proxy = self._get_new_proxy()
                if initial_proxy:
                    self.session.proxies = {
                        'http': initial_proxy,
                        'https': initial_proxy
                    }
                    if self.config.debug_mode:
                        masked_proxy = initial_proxy.split('@')[1] if '@' in initial_proxy else initial_proxy
                        self._log(f"Session using proxy: ...@{masked_proxy}")
            
            # First request: Visit homepage (like a real browser)
            homepage_headers = self._get_browser_headers(request_type='navigate')
            response = self.session.get(
                'https://www.reddit.com/',
                headers=homepage_headers,
                timeout=10,
                verify=self.ssl_verify,
                impersonate="chrome110"
            )
            
            # Log cookies received
            if self.config.debug_mode:
                cookie_count = len(self.session.cookies)
                cookie_names = list(self.session.cookies.keys())
                self._log(f"Session cookies received: {cookie_count} cookies")
                self._log(f"Cookie names: {cookie_names}")
            
            # Small delay like a real browser would have
            time.sleep(random.uniform(0.5, 1.5))
            
            self._log(f"Session initialized (Status: {response.status_code})")
            return True
        except Exception as e:
            self._log(f"Warning: Could not initialize session: {e}")
            return False
        
    def _log(self, message: str):
        """Log message (always logs, prefix changes based on debug mode)"""
        prefix = "[YARS]" if not self.config.debug_mode else "[YARS DEBUG]"
        print(f"{prefix} {message}")
    
    def _get_new_proxy(self) -> Optional[str]:
        """Get a new proxy URL from proxy configuration"""
        if not self.proxy_configuration:
            return self.proxy_url
        
        try:
            # Get new proxy URL using asyncio (proxy_configuration.new_url() is async)
            loop = None
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if loop.is_running():
                # Already in async context, create task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.proxy_configuration.new_url())
                    proxy_url = future.result(timeout=5)
            else:
                # Not in async context, safe to use asyncio.run
                proxy_url = loop.run_until_complete(self.proxy_configuration.new_url())
            
            return proxy_url
        except Exception as e:
            self._log(f"Warning: Failed to get new proxy: {e}")
            return self.proxy_url
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to Reddit with retry logic and proxy rotation"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                # Add human-like delay BEFORE making the request (not just after success)
                if attempt > 0:
                    # On retries, use exponential backoff
                    pre_delay = random.uniform(0.5, 1.0) * (2 ** (attempt - 1))
                else:
                    # First attempt: small random delay
                    pre_delay = random.uniform(0.3, 0.8)
                time.sleep(pre_delay)
                
                # Get new proxy for this request (if rotation enabled)
                if self.proxy_configuration:
                    current_proxy = self._get_new_proxy()
                    if current_proxy:
                        self.session.proxies = {
                            'http': current_proxy,
                            'https': current_proxy
                        }
                        self.request_count += 1
                        if self.config.debug_mode:
                            masked_proxy = current_proxy.split('@')[1] if '@' in current_proxy else current_proxy
                            self._log(f"Using proxy #{self.request_count}: ...@{masked_proxy}")
                
                # Get API-specific headers for JSON endpoints
                request_headers = self._get_browser_headers(
                    referer='https://www.reddit.com/search/',
                    request_type='api'
                )
                
                # Log request details in debug mode
                self._log(f"Making request to: {url} (Attempt {attempt + 1}/{max_retries})")
                if params:
                    self._log(f"Parameters: {params}")
                
                if self.config.debug_mode:
                    # Log critical headers
                    critical_headers = ['Origin', 'Content-Type', 'Sec-Fetch-Mode', 'X-Requested-With']
                    header_log = {k: request_headers.get(k) for k in critical_headers if k in request_headers}
                    self._log(f"Request headers: {header_log}")
                    
                    # Check if cookies are present
                    cookie_count = len(self.session.cookies)
                    self._log(f"Sending {cookie_count} cookies with request")

                response = self.session.get(
                    url,
                    headers=request_headers,
                    params=params,
                    timeout=10,
                    verify=self.ssl_verify,
                    impersonate="chrome110"
                )

                self._log(f"Response status: {response.status_code}")

                # Handle different status codes
                if response.status_code == 200:
                    # Random delay between 1.5-3 seconds AFTER successful request
                    delay = random.uniform(1.5, 3.0)
                    time.sleep(delay)

                    json_data = response.json()
                    children_count = len(json_data.get('data', {}).get('children', []))
                    self._log(f"✅ Success! Received {children_count} items")
                    return json_data

                elif response.status_code == 403:
                    self._log(f"❌ BLOCKED: {url} - Anti-bot detection triggered")
                    if self.config.debug_mode:
                        # Log response headers to diagnose blocking
                        self._log(f"Response headers: {dict(response.headers)}")
                    
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # 1s, 2s, 4s exponential backoff
                        self._log(f"Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        self._log(f"Response text: {response.text[:500]}")
                        return None

                elif response.status_code == 429:
                    self._log(f"⏱️ RATE LIMITED: {url} - Slowing down")
                    time.sleep(5)
                    continue

                elif response.status_code == 404:
                    self._log(f"❓ NOT FOUND: {url}")
                    return None

                elif response.status_code >= 500:
                    self._log(f"🔥 SERVER ERROR: {url} - Status {response.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return None

                else:
                    response.raise_for_status()

            except requests.exceptions.RequestException as e:
                self._log(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return None
            except Exception as e:
                self._log(f"Unexpected error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return None

        return None
    
    def _check_global_limit(self) -> bool:
        """Check if global max_items limit has been reached"""
        return self.total_items_scraped >= self.config.max_items
    
    def _add_result(self, item: Dict[str, Any]):
        """Add result and track count"""
        if not self._check_global_limit():
            self.results.append(item)
            self.total_items_scraped += 1
            return True
        return False
    
    def _parse_url_type(self, url: str) -> str:
        """Determine the type of Reddit URL"""
        if '/user/' in url or '/u/' in url:
            return 'user'
        elif '/comments/' in url:
            return 'post'
        elif '/r/' in url:
            return 'subreddit'
        elif '/search' in url:
            return 'search'
        else:
            return 'unknown'
    
    def run(self) -> List[Dict[str, Any]]:
        """
        Main execution method - processes all inputs and returns results
        Compatible with Apify-style workflow
        
        Returns:
            List of all scraped items
        """
        self._log("Starting scraper run...")
        self.results = []
        self.total_items_scraped = 0
        
        # Process start URLs
        if self.config.start_urls and not self.config.ignore_start_urls:
            self._log(f"Processing {len(self.config.start_urls)} start URLs...")
            self._process_start_urls()
        
        # Process searches
        if self.config.searches:
            self._log(f"Processing {len(self.config.searches)} searches...")
            self._process_searches()
        
        self._log(f"Scraping complete. Total items: {len(self.results)}")
        return self.results
    
    def _process_start_urls(self):
        """Process all start URLs"""
        for url in self.config.start_urls:
            if self._check_global_limit():
                self._log("Global max_items limit reached")
                break
            
            self._log(f"Processing URL: {url}")
            url_type = self._parse_url_type(url)
            
            if url_type == 'post':
                self._scrape_url_post(url)
            elif url_type == 'user':
                self._scrape_url_user(url)
            elif url_type == 'subreddit':
                self._scrape_url_subreddit(url)
            elif url_type == 'search':
                self._scrape_url_search(url)
            else:
                self._log(f"Unknown URL type: {url}")
    
    def _process_searches(self):
        """Process all search terms"""
        for search_term in self.config.searches:
            if self._check_global_limit():
                self._log("Global max_items limit reached")
                break
            
            self._log(f"Searching for: {search_term}")
            
            # Search for posts
            if self.config.search_posts:
                posts = self.search_reddit(
                    query=search_term,
                    limit=min(self.config.max_post_count, self.config.max_items - self.total_items_scraped),
                    sort=self.config.sort,
                    time_filter=self.config.time_filter,
                    community=self.config.search_community_name
                )
                for post in posts:
                    if not self._add_result(post):
                        break
            
            # Search for communities
            if self.config.search_communities and not self._check_global_limit():
                communities = self.search_communities(
                    query=search_term,
                    limit=min(self.config.max_communities_count, self.config.max_items - self.total_items_scraped)
                )
                for community in communities:
                    if not self._add_result(community):
                        break
            
            # Search for users
            if self.config.search_users and not self._check_global_limit():
                users = self.search_users(
                    query=search_term,
                    limit=min(self.config.max_user_count, self.config.max_items - self.total_items_scraped)
                )
                for user in users:
                    if not self._add_result(user):
                        break
            
            # Search for comments
            if self.config.search_comments and not self._check_global_limit():
                comments = self.search_comments(
                    query=search_term,
                    limit=min(self.config.max_comments, self.config.max_items - self.total_items_scraped)
                )
                for comment in comments:
                    if not self._add_result(comment):
                        break
    
    def _scrape_url_post(self, url: str):
        """Scrape a single post URL"""
        permalink = url.split('reddit.com')[-1]
        post_details = self.scrape_post_details(permalink, comment_limit=self.config.max_comments)
        if post_details:
            self._add_result(post_details)
    
    def _scrape_url_user(self, url: str):
        """Scrape a user URL"""
        username = url.split('/user/')[-1].split('/')[0].split('?')[0]
        user_data = self.scrape_user_data(
            username=username,
            limit=min(self.config.max_post_count, self.config.max_items - self.total_items_scraped)
        )
        for item in user_data:
            if not self._add_result(item):
                break
    
    def _scrape_url_subreddit(self, url: str):
        """Scrape a subreddit URL"""
        # Extract subreddit name from URL
        match = re.search(r'/r/([^/\?]+)', url)
        if match:
            subreddit = match.group(1)
            
            # Determine category from URL
            category = 'hot'
            if '/new' in url:
                category = 'new'
            elif '/top' in url:
                category = 'top'
            elif '/rising' in url:
                category = 'rising'
            
            posts = self.fetch_subreddit_posts(
                subreddit=subreddit,
                limit=min(self.config.max_post_count, self.config.max_items - self.total_items_scraped),
                category=category,
                time_filter=self.config.time_filter
            )
            for post in posts:
                if not self._add_result(post):
                    break
    
    def _scrape_url_search(self, url: str):
        """Scrape a search URL"""
        # Extract query from URL
        match = re.search(r'[?&]q=([^&]+)', url)
        if match:
            query = match.group(1)
            results = self.search_reddit(
                query=query,
                limit=min(self.config.max_post_count, self.config.max_items - self.total_items_scraped),
                sort=self.config.sort
            )
            for result in results:
                if not self._add_result(result):
                    break
    
    def search_reddit(self, query: str, limit: int = 25, sort: str = "relevance",
                     time_filter: str = "all", community: Optional[str] = None) -> List[Dict]:
        """
        Search Reddit for posts matching the query

        Args:
            query: Search term
            limit: Number of results
            sort: Sort method (relevance, hot, top, new, comments)
            time_filter: Time filter (hour, day, week, month, year, all)
            community: Restrict search to specific community

        Returns:
            List of post dictionaries
        """
        # Auto-set sort to 'new' when post_date_limit is provided
        if self.config.post_date_limit and sort == 'relevance':
            sort = 'new'
            self._log("Auto-setting sort to 'new' for post date filtering")
        
        params = {
            'q': query,
            'limit': min(limit, 100),  # Reddit API limit
            'sort': sort,
            't': time_filter,
            'type': 'link'
        }

        if community:
            params['restrict_sr'] = 'on'
            params['q'] = f"{query} subreddit:{community}"

        if not self.config.include_nsfw:
            params['include_over_18'] = 'off'

        data = self._search_with_fallback('search.json', params)
        if not data:
            return []

        posts = []
        for child in data.get('data', {}).get('children', []):
            post_data = child.get('data', {})
            post = self._format_post(post_data)
            
            # Apply NSFW filter
            if not self.config.include_nsfw and post.get('over18'):
                continue
            
            # Apply date filter
            if not self._passes_date_filter(post):
                continue
            
            posts.append(post)

        return posts[:limit]
    
    def search_communities(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for communities"""
        params = {
            'q': query,
            'limit': min(limit, 100),
            'type': 'sr'
        }

        data = self._search_with_fallback('search.json', params)
        if not data:
            return []

        communities = []
        for child in data.get('data', {}).get('children', []):
            community_data = child.get('data', {})
            community = self._format_community(community_data)
            
            # Apply NSFW filter
            if not self.config.include_nsfw and community.get('over18'):
                continue
            
            communities.append(community)

        return communities[:limit]

    def search_users(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for users"""
        params = {
            'q': query,
            'limit': min(limit, 100),
            'type': 'user'
        }

        data = self._search_with_fallback('search.json', params)
        if not data:
            return []

        users = []
        for child in data.get('data', {}).get('children', []):
            user_data = child.get('data', {})
            users.append(self._format_user_search(user_data))

        return users[:limit]
    
    def search_comments(self, query: str, limit: int = 100, sort: str = None) -> List[Dict]:
        """Search for comments matching a query"""
        params = {
            'q': query,
            'limit': min(limit, 100),
            'type': 'comment',
            'sort': sort or self.config.sort
        }
        
        # Add time filter if specified
        if self.config.time_filter and self.config.time_filter != 'all':
            params['t'] = self.config.time_filter
        
        data = self._search_with_fallback('search.json', params)
        if not data:
            return []
        
        comments = []
        for child in data.get('data', {}).get('children', []):
            comment_data = child.get('data', {})
            comments.append(self._format_comment(comment_data))
        
        return comments[:limit]
    
    def _search_with_fallback(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Execute search with fallback to old.reddit.com if blocked"""
        # Try modern Reddit first
        url = f"{self.base_url}/{endpoint}"
        data = self._make_request(url, params)
        
        # If blocked (403), try old.reddit.com
        if not data:
            self._log("Modern Reddit blocked, trying old.reddit.com...")
            url = f"https://old.reddit.com/{endpoint}"
            data = self._make_request(url, params)
        
        return data
    
    def scrape_post_details(self, permalink: str, comment_limit: int = 100) -> Optional[Dict]:
        """
        Scrape detailed information about a specific post including comments
        
        Args:
            permalink: Post permalink
            comment_limit: Number of comments to fetch
        
        Returns:
            Dictionary containing post details and comments
        """
        url = f"{self.base_url}{permalink}.json"
        params = {'limit': comment_limit}
        
        data = self._make_request(url, params)
        if not data or len(data) < 2:
            return None
        
        # Post data
        post_data = data[0]['data']['children'][0]['data']
        result = self._format_post(post_data)
        
        # Comments
        if not self.config.skip_comments:
            comments_list, _ = self._parse_comments(data[1]['data']['children'], max_comments=comment_limit)
            result['comments'] = comments_list
        else:
            result['comments'] = []
        
        return result
    
    def _parse_comments(self, comment_data: List, max_comments: int = 100, current_count: int = 0) -> tuple:
        """Parse comments from Reddit JSON structure with limit
        
        Returns:
            Tuple of (comments_list, total_count)
        """
        comments = []
        
        for comment in comment_data:
            if current_count >= max_comments:
                break
                
            if comment['kind'] == 't1':  # Comment type
                data = comment['data']
                comment_obj = self._format_comment(data)
                
                # Parse replies recursively
                replies = data.get('replies')
                if replies and not isinstance(replies, str) and current_count < max_comments:
                    reply_list, current_count = self._parse_comments(
                        replies.get('data', {}).get('children', []),
                        max_comments=max_comments,
                        current_count=current_count + 1
                    )
                    comment_obj['replies'] = reply_list
                else:
                    comment_obj['replies'] = []
                
                comments.append(comment_obj)
                current_count += 1
        
        return comments, current_count
    
    def scrape_user_data(self, username: str, limit: int = 25, content_type: str = "overview") -> List[Dict]:
        """
        Fetch recent activity of a Reddit user
        
        Args:
            username: Reddit username
            limit: Number of items to fetch
            content_type: Type of content (overview, submitted, comments)
        
        Returns:
            List of user activities
        """
        if self.config.skip_user_posts:
            # Only get user profile, not posts
            return self._get_user_profile(username)
        
        url = f"{self.base_url}/user/{username}/{content_type}.json"
        params = {'limit': min(limit, 100)}
        
        data = self._make_request(url, params)
        if not data:
            return []
        
        activities = []
        for child in data.get('data', {}).get('children', [])[:limit]:
            item_data = child.get('data', {})
            
            if child.get('kind') == 't3':  # Post
                post = self._format_post(item_data)
                
                # Apply NSFW filter
                if not self.config.include_nsfw and post.get('over18'):
                    continue
                
                # Apply date filter
                if not self._passes_date_filter(post):
                    continue
                
                activities.append(post)
            elif child.get('kind') == 't1':  # Comment
                activities.append(self._format_comment(item_data))
        
        return activities
    
    def _get_user_profile(self, username: str) -> List[Dict]:
        """Get user profile information only"""
        url = f"{self.base_url}/user/{username}/about.json"
        data = self._make_request(url)
        
        if not data:
            return []
        
        user_data = data.get('data', {})
        return [self._format_user(user_data)]
    
    def fetch_subreddit_posts(self, subreddit: str, limit: int = 25, 
                             category: str = "hot", time_filter: str = "all") -> List[Dict]:
        """
        Fetch posts from a specific subreddit
        
        Args:
            subreddit: Name of the subreddit
            limit: Number of posts to fetch
            category: Category of posts (hot, new, top, rising)
            time_filter: Time filter for 'top' category
        
        Returns:
            List of post dictionaries
        """
        # Auto-set category to 'new' when post_date_limit is provided
        if self.config.post_date_limit and category == 'hot':
            category = 'new'
            self._log("Auto-setting category to 'new' for post date filtering")
        
        url = f"{self.base_url}/r/{subreddit}/{category}.json"
        params = {'limit': min(limit, 100)}
        
        if category == "top":
            params['t'] = time_filter
        
        data = self._make_request(url, params)
        if not data:
            return []
        
        posts = []
        for child in data.get('data', {}).get('children', [])[:limit]:
            post_data = child.get('data', {})
            post = self._format_post(post_data)
            
            # Apply NSFW filter
            if not self.config.include_nsfw and post.get('over18'):
                continue
            
            # Apply date filter
            if not self._passes_date_filter(post):
                continue
            
            posts.append(post)
        
        return posts
    
    # Formatting methods for consistent output
    
    def _format_post(self, post_data: Dict) -> Dict:
        """Format post data to Apify-compatible structure"""
        # Extract image URL
        image_url = None
        if post_data.get('post_hint') == 'image':
            image_url = post_data.get('url')
        elif 'preview' in post_data:
            try:
                image_url = post_data['preview']['images'][0]['source']['url'].replace('&amp;', '&')
            except (KeyError, IndexError):
                pass
        
        return {
            'id': post_data.get('name'),
            'parsedId': post_data.get('id'),
            'url': post_data.get('url'),
            'username': post_data.get('author'),
            'title': post_data.get('title'),
            'communityName': f"r/{post_data.get('subreddit')}" if post_data.get('subreddit') else None,
            'parsedCommunityName': post_data.get('subreddit'),
            'body': post_data.get('selftext'),
            'html': post_data.get('selftext_html'),
            'numberOfComments': post_data.get('num_comments', 0),
            'upVotes': post_data.get('score', 0),
            'isVideo': post_data.get('is_video', False),
            'isAd': post_data.get('promoted', False),
            'over18': post_data.get('over_18', False),
            'createdAt': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat() + 'Z',
            'scrapedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'permalink': post_data.get('permalink'),
            'thumbnail_url': post_data.get('thumbnail') if post_data.get('thumbnail') not in ['self', 'default', 'nsfw'] else None,
            'image_url': image_url,
            'dataType': 'post'
        }
    
    def _format_comment(self, comment_data: Dict) -> Dict:
        """Format comment data to Apify-compatible structure"""
        return {
            'id': comment_data.get('name'),
            'parsedId': comment_data.get('id'),
            'url': f"{self.base_url}{comment_data.get('permalink')}" if comment_data.get('permalink') else None,
            'parentId': comment_data.get('parent_id'),
            'username': comment_data.get('author'),
            'category': comment_data.get('subreddit'),
            'communityName': f"r/{comment_data.get('subreddit')}" if comment_data.get('subreddit') else None,
            'body': comment_data.get('body'),
            'html': comment_data.get('body_html'),
            'createdAt': datetime.fromtimestamp(comment_data.get('created_utc', 0)).isoformat() + 'Z',
            'scrapedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'upVotes': comment_data.get('score', 0),
            'numberOfreplies': len(comment_data.get('replies', {}).get('data', {}).get('children', [])) if isinstance(comment_data.get('replies'), dict) else 0,
            'dataType': 'comment'
        }
    
    def _format_community(self, community_data: Dict) -> Dict:
        """Format community data to Apify-compatible structure"""
        return {
            'id': community_data.get('id'),
            'name': community_data.get('name'),
            'title': community_data.get('display_name_prefixed'),
            'headerImage': community_data.get('header_img'),
            'description': community_data.get('public_description'),
            'over18': community_data.get('over18', False),
            'createdAt': datetime.fromtimestamp(community_data.get('created_utc', 0)).isoformat() + 'Z',
            'scrapedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'numberOfMembers': community_data.get('subscribers', 0),
            'url': f"{self.base_url}{community_data.get('url')}" if community_data.get('url') else None,
            'dataType': 'community'
        }
    
    def _format_user(self, user_data: Dict) -> Dict:
        """Format user data to Apify-compatible structure"""
        return {
            'id': user_data.get('id'),
            'url': f"{self.base_url}/user/{user_data.get('name')}",
            'username': user_data.get('name'),
            'userIcon': user_data.get('icon_img', '').split('?')[0] if user_data.get('icon_img') else None,
            'postKarma': user_data.get('link_karma', 0),
            'commentKarma': user_data.get('comment_karma', 0),
            'description': user_data.get('subreddit', {}).get('public_description', '') if isinstance(user_data.get('subreddit'), dict) else '',
            'over18': user_data.get('subreddit', {}).get('over_18', False) if isinstance(user_data.get('subreddit'), dict) else False,
            'createdAt': datetime.fromtimestamp(user_data.get('created_utc', 0)).isoformat() + 'Z',
            'scrapedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'dataType': 'user'
        }
    
    def _format_user_search(self, user_data: Dict) -> Dict:
        """Format user search result"""
        return {
            'id': user_data.get('id'),
            'url': f"{self.base_url}{user_data.get('url')}" if user_data.get('url') else None,
            'username': user_data.get('subreddit', {}).get('display_name_prefixed', '').replace('u/', ''),
            'userIcon': user_data.get('icon_img', '').split('?')[0] if user_data.get('icon_img') else None,
            'postKarma': user_data.get('link_karma', 0),
            'commentKarma': user_data.get('comment_karma', 0),
            'description': user_data.get('subreddit', {}).get('public_description', '') if isinstance(user_data.get('subreddit'), dict) else '',
            'scrapedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'dataType': 'user'
        }
    
    def _passes_date_filter(self, post: Dict) -> bool:
        """Check if post passes the date filter"""
        if not self.post_date_limit_parsed:
            return True
        
        try:
            post_date = datetime.fromisoformat(post.get('createdAt', '').replace('Z', '+00:00'))
            return post_date >= self.post_date_limit_parsed
        except (ValueError, AttributeError):
            return True  # Include post if date parsing fails
