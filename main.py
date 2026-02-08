#!/usr/bin/env python3
"""
YARS - Yet Another Reddit Scraper
Main CLI interface for running the scraper with JSON input files
"""

import argparse
import json
import sys
from yars import YARS
from config import ScraperInput
from utils import save_to_json


def main():
    parser = argparse.ArgumentParser(
        description='YARS - Yet Another Reddit Scraper (Apify-compatible)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with JSON input file
  python main.py --input input.json --output results.json

  # Run with inline JSON
  python main.py --json '{"searches": ["Python"], "maxItems": 10}'

  # Quick search
  python main.py --search "Python programming" --limit 10

  # Scrape URL
  python main.py --url "https://www.reddit.com/r/Python/" --limit 5

For more information, see README.md
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '-i', '--input',
        help='Path to JSON input file (Apify-style configuration)'
    )
    input_group.add_argument(
        '-j', '--json',
        help='Inline JSON configuration string'
    )
    input_group.add_argument(
        '-s', '--search',
        help='Quick search keyword'
    )
    input_group.add_argument(
        '-u', '--url',
        help='Single Reddit URL to scrape'
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output',
        default='output.json',
        help='Output JSON file path (default: output.json)'
    )
    
    # Quick options (for --search and --url)
    parser.add_argument(
        '-l', '--limit',
        type=int,
        default=10,
        help='Max items to scrape (default: 10)'
    )
    
    parser.add_argument(
        '--skip-comments',
        action='store_true',
        help='Skip comment extraction (faster)'
    )
    
    parser.add_argument(
        '--sort',
        choices=['relevance', 'hot', 'top', 'new', 'comments'],
        default='relevance',
        help='Sort method (default: relevance)'
    )
    
    parser.add_argument(
        '--time',
        choices=['hour', 'day', 'week', 'month', 'year', 'all'],
        default='all',
        help='Time filter (default: all)'
    )
    
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    # Build configuration based on input type
    try:
        if args.input:
            # Load from file
            print(f"📄 Loading configuration from: {args.input}")
            config = ScraperInput.from_json_file(args.input)
            
        elif args.json:
            # Parse inline JSON
            print("📝 Parsing inline JSON configuration")
            config = ScraperInput.from_json(args.json)
            
        elif args.search:
            # Quick search mode
            print(f"🔍 Quick search mode: '{args.search}'")
            config = ScraperInput(
                searches=[args.search],
                max_items=args.limit,
                skip_comments=args.skip_comments,
                sort=args.sort,
                time_filter=args.time,
                debug_mode=args.debug
            )
            
        elif args.url:
            # Quick URL mode
            print(f"🔗 Quick URL mode: {args.url}")
            config = ScraperInput(
                start_urls=[args.url],
                max_items=args.limit,
                max_post_count=args.limit,
                skip_comments=args.skip_comments,
                debug_mode=args.debug
            )
        
        # Override debug mode if specified
        if args.debug:
            config.debug_mode = True
        
        # Display configuration summary
        print("\n" + "="*60)
        print("Configuration Summary:")
        print("="*60)
        if config.start_urls:
            print(f"  URLs to scrape: {len(config.start_urls)}")
        if config.searches:
            print(f"  Search terms: {len(config.searches)}")
        print(f"  Max items: {config.max_items}")
        print(f"  Skip comments: {config.skip_comments}")
        print(f"  Debug mode: {config.debug_mode}")
        print("="*60 + "\n")
        
        # Run scraper
        print("🚀 Starting scraper...\n")
        scraper = YARS(config=config)
        results = scraper.run()
        
        # Display results summary
        print("\n" + "="*60)
        print("✅ Scraping Complete!")
        print("="*60)
        print(f"  Total items scraped: {len(results)}")
        
        # Count by type
        by_type = {}
        for item in results:
            dtype = item.get('dataType', 'unknown')
            by_type[dtype] = by_type.get(dtype, 0) + 1
        
        if by_type:
            print("\n  Items by type:")
            for dtype, count in sorted(by_type.items()):
                print(f"    - {dtype}: {count}")
        
        # Save results
        print(f"\n💾 Saving results to: {args.output}")
        save_to_json(results, args.output)
        
        print("\n" + "="*60)
        print(f"✨ Done! Results saved to {args.output}")
        print("="*60)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {e}", file=sys.stderr)
        return 1
        
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON - {e}", file=sys.stderr)
        return 1
        
    except ValueError as e:
        print(f"❌ Error: Invalid configuration - {e}", file=sys.stderr)
        return 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user", file=sys.stderr)
        return 130
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
