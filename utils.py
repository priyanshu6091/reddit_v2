import json
import requests
from datetime import datetime


def display_results(data, title="Results"):
    """
    Display results in a formatted JSON structure
    
    Args:
        data: Data to display (dict or list)
        title: Title for the output
    """
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("=" * 80 + "\n")


def download_image(url, output_path=None):
    """
    Download an image from a URL
    
    Args:
        url: Image URL
        output_path: Path to save the image (if None, uses timestamp)
    
    Returns:
        Path to downloaded image or None if failed
    """
    if not url or url in ['self', 'default', 'nsfw']:
        print(f"Invalid or no image URL: {url}")
        return None
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Generate filename if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = url.split('.')[-1].split('?')[0]
            if extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                extension = 'jpg'
            output_path = f"image_{timestamp}.{extension}"
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Downloaded image: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"✗ Failed to download image from {url}: {e}")
        return None


def save_to_json(data, filename):
    """
    Save data to a JSON file
    
    Args:
        data: Data to save
        filename: Output filename
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved data to {filename}")
    except Exception as e:
        print(f"✗ Failed to save to {filename}: {e}")


def format_timestamp(timestamp):
    """
    Convert Unix timestamp to readable date
    
    Args:
        timestamp: Unix timestamp
    
    Returns:
        Formatted date string
    """
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
