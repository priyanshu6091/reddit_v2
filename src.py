"""
YARS - Yet Another Reddit Scraper (Apify Actor)
Main entry point for Apify platform
"""

from apify import Actor
from config import ScraperInput
from yars import YARS
import asyncio


async def main():
    """
    Main Actor function for Apify platform
    """
    async with Actor:
        # Get input from Apify platform
        actor_input = await Actor.get_input() or {}
        
        Actor.log.info(f"Starting YARS Reddit Scraper with input: {actor_input}")
        
        try:
            # Convert startUrls from Apify format to simple list
            start_urls = []
            if 'startUrls' in actor_input and actor_input['startUrls']:
                start_urls = [item['url'] if isinstance(item, dict) else item 
                             for item in actor_input['startUrls']]
            
            # Map Apify proxy config
            proxy_config = actor_input.get('proxy', {})
            use_apify_proxy = proxy_config.get('useApifyProxy', False)
            
            # Create configuration
            config = ScraperInput.from_dict({
                'start_urls': start_urls,
                'searches': actor_input.get('searches', []),
                'search_community_name': actor_input.get('searchCommunityName'),
                'search_posts': actor_input.get('searchPosts', True),
                'search_comments': actor_input.get('searchComments', False),
                'search_communities': actor_input.get('searchCommunities', False),
                'search_users': actor_input.get('searchUsers', False),
                'max_items': actor_input.get('maxItems', 100),
                'max_post_count': actor_input.get('maxPostCount', 50),
                'max_comments': actor_input.get('maxComments', 20),
                'max_communities_count': actor_input.get('maxCommunitiesCount', 10),
                'max_user_count': actor_input.get('maxUserCount', 10),
                'skip_comments': actor_input.get('skipComments', False),
                'skip_user_posts': actor_input.get('skipUserPosts', False),
                'sort': actor_input.get('sort', 'relevance'),
                'time_filter': actor_input.get('time', 'all'),
                'include_nsfw': actor_input.get('includeNSFW', False),
                'debug_mode': actor_input.get('debugMode', False)
            })
            
            Actor.log.info(f"Configuration created:")
            Actor.log.info(f"  - Start URLs: {len(config.start_urls)}")
            Actor.log.info(f"  - Searches: {len(config.searches)}")
            Actor.log.info(f"  - Max Items: {config.max_items}")
            Actor.log.info(f"  - Skip Comments: {config.skip_comments}")
            
            # Configure proxy if using Apify proxy
            proxy_configuration = None
            if use_apify_proxy:
                Actor.log.info("Configuring Apify Proxy...")
                # Get Apify proxy URL
                proxy_groups = proxy_config.get('apifyProxyGroups', [])
                proxy_country = proxy_config.get('apifyProxyCountry')
                
                # Build proxy configuration using actor_proxy_input (recommended approach)
                try:
                    proxy_configuration = await Actor.create_proxy_configuration(
                        actor_proxy_input={
                            'useApifyProxy': True,
                            'apifyProxyGroups': proxy_groups if proxy_groups else None,
                            'apifyProxyCountry': proxy_country
                        }
                    )
                    
                    if proxy_configuration is not None:
                        # Test proxy by getting one URL
                        test_proxy = await proxy_configuration.new_url()
                        if isinstance(test_proxy, str):
                            # Mask password in log
                            masked_url = test_proxy.split('@')[1] if '@' in test_proxy else test_proxy
                            Actor.log.info(f"✅ Apify Proxy rotation enabled: ...@{masked_url}")
                            Actor.log.info(f"   Proxy will rotate for each request")
                        else:
                            Actor.log.error(f"Proxy URL is not a string: {type(test_proxy)}")
                            proxy_configuration = None
                    else:
                        Actor.log.warning("Proxy configuration returned None")
                except Exception as e:
                    Actor.log.warning(f"Failed to configure proxy: {e}")
                    import traceback
                    Actor.log.warning(f"Traceback: {traceback.format_exc()}")
                    Actor.log.info("Continuing without proxy...")
            
            # Initialize scraper with proxy configuration for rotation
            scraper = YARS(config=config, proxy_configuration=proxy_configuration)
            
            # Run the scraper
            Actor.log.info("Starting Reddit scraping...")
            
            if not config.start_urls and not config.searches:
                Actor.log.warning("⚠️ No start URLs or searches provided!")
                results = []
            else:
                Actor.log.info(f"Processing {len(config.start_urls)} URLs and {len(config.searches)} searches...")
                results = scraper.run()
            
            Actor.log.info(f"Scraping completed. Total items: {len(results)}")
            
            # Count by type
            type_counts = {}
            for item in results:
                dtype = item.get('dataType', 'unknown')
                type_counts[dtype] = type_counts.get(dtype, 0) + 1
            
            Actor.log.info("Results by type:")
            for dtype, count in type_counts.items():
                Actor.log.info(f"  - {dtype}: {count}")
            
            # Push results to Apify dataset
            Actor.log.info("Pushing results to dataset...")
            await Actor.push_data(results)
            
            Actor.log.info("✅ Actor finished successfully!")
            
        except ValueError as e:
            Actor.log.error(f"Configuration error: {e}")
            raise
            
        except Exception as e:
            Actor.log.error(f"Unexpected error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
