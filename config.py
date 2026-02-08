"""
Input configuration for Reddit Scraper
Handles all input parameters similar to Apify's Reddit Scraper
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import json


@dataclass
class ProxyConfig:
    """Proxy configuration"""
    use_proxy: bool = False
    proxy_urls: Optional[List[str]] = None
    
    def to_dict(self):
        return {
            'use_proxy': self.use_proxy,
            'proxy_urls': self.proxy_urls
        }


@dataclass
class ScraperInput:
    """
    Main input configuration for Reddit Scraper
    Compatible with Apify-style input format
    """
    
    # URLs to scrape
    start_urls: List[str] = field(default_factory=list)
    
    # Search parameters
    searches: List[str] = field(default_factory=list)
    search_community_name: Optional[str] = None
    
    # Search type filters
    search_posts: bool = True
    search_comments: bool = False
    search_communities: bool = False
    search_users: bool = False
    
    # Global limits
    max_items: int = 100
    max_post_count: int = 50
    max_comments: int = 20
    max_communities_count: int = 10
    max_user_count: int = 10
    
    # Skip options
    skip_comments: bool = False
    skip_user_posts: bool = False
    skip_community: bool = False
    
    # Search and filter options
    sort: str = "relevance"  # relevance, hot, top, new, comments
    time_filter: str = "all"  # hour, day, week, month, year, all
    post_date_limit: Optional[str] = None  # ISO date string
    
    # Content filters
    include_nsfw: bool = False
    
    # Advanced options
    debug_mode: bool = False
    scroll_timeout: int = 40
    ignore_start_urls: bool = False
    
    # Proxy configuration
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    
    def __post_init__(self):
        """Validate input parameters"""
        self._validate()
    
    def _validate(self):
        """Validate input parameters"""
        # Validate sort options
        valid_sorts = ["relevance", "hot", "top", "new", "comments"]
        if self.sort not in valid_sorts:
            raise ValueError(f"sort must be one of {valid_sorts}, got '{self.sort}'")
        
        # Validate time filters
        valid_times = ["hour", "day", "week", "month", "year", "all"]
        if self.time_filter not in valid_times:
            raise ValueError(f"time_filter must be one of {valid_times}, got '{self.time_filter}'")
        
        # Ensure at least one search type is enabled if searches are provided
        if self.searches and not any([
            self.search_posts, 
            self.search_comments, 
            self.search_communities, 
            self.search_users
        ]):
            raise ValueError("At least one search type must be enabled when using searches")
        
        # Ensure either start_urls or searches is provided
        if not self.start_urls and not self.searches:
            raise ValueError("Either start_urls or searches must be provided")
        
        # Validate max limits are positive
        if self.max_items <= 0:
            raise ValueError("max_items must be greater than 0")
        if self.max_post_count <= 0:
            raise ValueError("max_post_count must be greater than 0")
        if self.max_comments < 0:
            raise ValueError("max_comments must be non-negative")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScraperInput':
        """Create ScraperInput from dictionary"""
        # Handle proxy configuration
        proxy_data = data.get('proxy', {})
        proxy = ProxyConfig(
            use_proxy=proxy_data.get('use_proxy', False),
            proxy_urls=proxy_data.get('proxy_urls')
        )
        
        # Map common alternate field names
        start_urls = data.get('start_urls', data.get('startUrls', []))
        if isinstance(start_urls, str):
            start_urls = [start_urls]
        
        searches = data.get('searches', data.get('search_term', []))
        if isinstance(searches, str):
            searches = [searches]
        
        return cls(
            start_urls=start_urls,
            searches=searches,
            search_community_name=data.get('search_community_name', data.get('searchCommunityName')),
            search_posts=data.get('search_posts', data.get('searchPosts', True)),
            search_comments=data.get('search_comments', data.get('searchComments', False)),
            search_communities=data.get('search_communities', data.get('searchCommunities', False)),
            search_users=data.get('search_users', data.get('searchUsers', False)),
            max_items=data.get('max_items', data.get('maxItems', 100)),
            max_post_count=data.get('max_post_count', data.get('maxPostCount', 50)),
            max_comments=data.get('max_comments', data.get('maxComments', 20)),
            max_communities_count=data.get('max_communities_count', data.get('maxCommunitiesCount', 10)),
            max_user_count=data.get('max_user_count', data.get('maxUserCount', 10)),
            skip_comments=data.get('skip_comments', data.get('skipComments', False)),
            skip_user_posts=data.get('skip_user_posts', data.get('skipUserPosts', False)),
            skip_community=data.get('skip_community', data.get('skipCommunity', False)),
            sort=data.get('sort', 'relevance'),
            time_filter=data.get('time_filter', data.get('time', 'all')),
            post_date_limit=data.get('post_date_limit', data.get('postDateLimit')),
            include_nsfw=data.get('include_nsfw', data.get('includeNSFW', False)),
            debug_mode=data.get('debug_mode', data.get('debugMode', False)),
            scroll_timeout=data.get('scroll_timeout', data.get('scrollTimeout', 40)),
            ignore_start_urls=data.get('ignore_start_urls', data.get('ignoreStartUrls', False)),
            proxy=proxy
        )
    
    @classmethod
    def from_json(cls, json_string: str) -> 'ScraperInput':
        """Create ScraperInput from JSON string"""
        data = json.loads(json_string)
        return cls.from_dict(data)
    
    @classmethod
    def from_json_file(cls, file_path: str) -> 'ScraperInput':
        """Create ScraperInput from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'start_urls': self.start_urls,
            'searches': self.searches,
            'search_community_name': self.search_community_name,
            'search_posts': self.search_posts,
            'search_comments': self.search_comments,
            'search_communities': self.search_communities,
            'search_users': self.search_users,
            'max_items': self.max_items,
            'max_post_count': self.max_post_count,
            'max_comments': self.max_comments,
            'max_communities_count': self.max_communities_count,
            'max_user_count': self.max_user_count,
            'skip_comments': self.skip_comments,
            'skip_user_posts': self.skip_user_posts,
            'skip_community': self.skip_community,
            'sort': self.sort,
            'time_filter': self.time_filter,
            'post_date_limit': self.post_date_limit,
            'include_nsfw': self.include_nsfw,
            'debug_mode': self.debug_mode,
            'scroll_timeout': self.scroll_timeout,
            'ignore_start_urls': self.ignore_start_urls,
            'proxy': self.proxy.to_dict()
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)
