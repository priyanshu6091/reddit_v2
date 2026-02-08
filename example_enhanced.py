"""
Example usage of enhanced YARS Reddit Scraper with Apify-style configuration
Demonstrates the new input system with batch processing and limits
"""

from yars import YARS
from config import ScraperInput
from utils import display_results, save_to_json
import json


def example_1_basic_search():
    """Example 1: Basic search with multiple keywords"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Multiple keyword search with limits")
    print("="*80)
    
    config = ScraperInput(
        searches=["Python programming", "machine learning"],
        search_posts=True,
        max_items=10,
        max_post_count=5,
        max_comments=3,
        sort="top",
        time_filter="week",
        debug_mode=True
    )
    
    scraper = YARS(config=config)
    results = scraper.run()
    
    print(f"\n✓ Scraped {len(results)} items")
    save_to_json(results, "example1_search_results.json")


def example_2_multiple_urls():
    """Example 2: Scrape multiple URLs (posts and subreddits)"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Multiple URLs with different types")
    print("="*80)
    
    config = ScraperInput(
        start_urls=[
            "https://www.reddit.com/r/Python/",
            "https://www.reddit.com/r/learnprogramming/comments/1frb5ib/what_single_health_test_or_practice_has/",
            "https://www.reddit.com/user/spez"
        ],
        max_items=20,
        max_post_count=5,
        max_comments=5,
        skip_comments=False,
        debug_mode=True
    )
    
    scraper = YARS(config=config)
    results = scraper.run()
    
    print(f"\n✓ Scraped {len(results)} items")
    
    # Group by data type
    by_type = {}
    for item in results:
        dtype = item.get('dataType', 'unknown')
        by_type[dtype] = by_type.get(dtype, 0) + 1
    
    print("\nResults by type:")
    for dtype, count in by_type.items():
        print(f"  - {dtype}: {count}")
    
    save_to_json(results, "example2_url_results.json")


def example_3_community_search():
    """Example 3: Search within specific community"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Search within specific community")
    print("="*80)
    
    config = ScraperInput(
        searches=["tutorial"],
        search_community_name="Python",
        search_posts=True,
        max_items=10,
        max_post_count=10,
        sort="top",
        time_filter="month",
        skip_comments=True,  # Skip comments for faster scraping
        debug_mode=True
    )
    
    scraper = YARS(config=config)
    results = scraper.run()
    
    print(f"\n✓ Scraped {len(results)} items from r/Python")
    
    # Display titles only
    print("\nPost titles:")
    for i, item in enumerate(results[:5], 1):
        print(f"  {i}. {item.get('title', 'N/A')}")
    
    save_to_json(results, "example3_community_search.json")


def example_4_search_communities_users():
    """Example 4: Search for communities and users"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Search for communities and users")
    print("="*80)
    
    config = ScraperInput(
        searches=["technology"],
        search_posts=False,
        search_communities=True,
        search_users=True,
        max_communities_count=5,
        max_user_count=5,
        max_items=20,
        debug_mode=True
    )
    
    scraper = YARS(config=config)
    results = scraper.run()
    
    print(f"\n✓ Scraped {len(results)} items")
    
    # Separate communities and users
    communities = [r for r in results if r.get('dataType') == 'community']
    users = [r for r in results if r.get('dataType') == 'user']
    
    print(f"\nCommunities found: {len(communities)}")
    for comm in communities[:3]:
        print(f"  - {comm.get('title')} ({comm.get('numberOfMembers', 0)} members)")
    
    print(f"\nUsers found: {len(users)}")
    for user in users[:3]:
        print(f"  - {user.get('username')} (Karma: {user.get('postKarma', 0)})")
    
    save_to_json(results, "example4_communities_users.json")


def example_5_apify_style_json():
    """Example 5: Load configuration from JSON (Apify-style)"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Load config from JSON file (Apify-style)")
    print("="*80)
    
    # Create sample input JSON
    input_json = {
        "maxItems": 15,
        "maxPostCount": 10,
        "maxComments": 5,
        "searches": ["artificial intelligence"],
        "searchPosts": True,
        "sort": "hot",
        "time": "week",
        "includeNSFW": False,
        "debugMode": True
    }
    
    # Save sample input
    with open("sample_input.json", "w") as f:
        json.dump(input_json, f, indent=2)
    
    print("Created sample_input.json:")
    print(json.dumps(input_json, indent=2))
    
    # Load and run
    config = ScraperInput.from_json_file("sample_input.json")
    scraper = YARS(config=config)
    results = scraper.run()
    
    print(f"\n✓ Scraped {len(results)} items using JSON config")
    save_to_json(results, "example5_json_config_results.json")


def example_6_skip_options():
    """Example 6: Using skip options for faster scraping"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Fast scraping with skip options")
    print("="*80)
    
    config = ScraperInput(
        start_urls=[
            "https://www.reddit.com/r/Python/",
            "https://www.reddit.com/user/reddit"
        ],
        max_items=10,
        max_post_count=5,
        skip_comments=True,  # Skip all comments
        skip_user_posts=True,  # Only get user profile, not posts
        debug_mode=True
    )
    
    scraper = YARS(config=config)
    results = scraper.run()
    
    print(f"\n✓ Scraped {len(results)} items (fast mode)")
    save_to_json(results, "example6_skip_options.json")


def main():
    """Run all examples"""
    print("\n" + "🚀 "*40)
    print("YARS ENHANCED - Apify-Style Reddit Scraper Examples")
    print("🚀 "*40)
    
    try:
        # Run examples one by one
        example_1_basic_search()
        example_2_multiple_urls()
        example_3_community_search()
        example_4_search_communities_users()
        example_5_apify_style_json()
        example_6_skip_options()
        
        print("\n" + "="*80)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\nGenerated files:")
        print("  - example1_search_results.json")
        print("  - example2_url_results.json")
        print("  - example3_community_search.json")
        print("  - example4_communities_users.json")
        print("  - example5_json_config_results.json")
        print("  - example6_skip_options.json")
        print("  - sample_input.json (input template)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
