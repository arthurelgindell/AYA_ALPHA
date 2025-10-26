#!/usr/bin/env python3
"""
Debug Firecrawl data format
"""

from firecrawl import FirecrawlApp
import json

api_key = "fc-b641c64dbb3b4962909c2f8f04c524ba"
app = FirecrawlApp(api_key=api_key)

print("Testing Firecrawl data format...\n")

# Test with a single URL scrape
test_url = "https://www.firecrawl.dev"
print(f"Scraping single URL: {test_url}")

try:
    result = app.scrape(test_url, formats=['markdown'], only_main_content=True)
except Exception as e:
    print(f"Error scraping {test_url}: {e}")
    raise

print(f"\nResult type: {type(result)}")
print(f"Result attributes: {dir(result)}")

if hasattr(result, '__dict__'):
    print(f"\nResult __dict__:")
    for k, v in result.__dict__.items():
        if not k.startswith('_'):
            print(f"  {k}: {type(v)} = {str(v)[:100]}")

print("\n" + "="*80)
print("Testing batch scrape format...\n")

# Test batch scrape with 2 URLs
test_urls = [
    "https://www.firecrawl.dev",
    "https://docs.firecrawl.dev"
]

print(f"Starting batch scrape of {len(test_urls)} URLs...")

try:
    batch_response = app.start_batch_scrape(test_urls, formats=['markdown'], only_main_content=True)
    batch_id = batch_response.get('id') if isinstance(batch_response, dict) else batch_response.id
    print(f"Batch ID: {batch_id}")
except Exception as e:
    print(f"Error starting batch scrape: {e}")
    raise

import time

# Add timeout to prevent infinite loop
max_attempts = 360  # 30 minutes at 5 second intervals (debug script)
attempts = 0

while attempts < max_attempts:
    try:
        status = app.get_batch_scrape_status(batch_id)
        state = status.status if hasattr(status, 'status') else 'unknown'
    except Exception as e:
        print(f"\nError checking batch status: {e}")
        raise

    print(f"Status: {state} | Attempt: {attempts}/{max_attempts}")

    if state == 'completed':
        print(f"\nStatus type: {type(status)}")
        print(f"Status attributes: {[a for a in dir(status) if not a.startswith('_')]}")

        if hasattr(status, 'data'):
            data = status.data
            print(f"\nData type: {type(data)}")
            print(f"Data length: {len(data)}")

            if len(data) > 0:
                print(f"\nFirst item type: {type(data[0])}")
                print(f"First item attributes: {[a for a in dir(data[0]) if not a.startswith('_')]}")

                if hasattr(data[0], '__dict__'):
                    print(f"\nFirst item __dict__:")
                    for k, v in data[0].__dict__.items():
                        if not k.startswith('_'):
                            val_str = str(v)[:200] if not isinstance(v, (dict, list)) else f"{type(v)}"
                            print(f"  {k}: {type(v).__name__} = {val_str}")
        break
    elif state in ['failed', 'cancelled']:
        print(f"Batch {state}")
        break

    time.sleep(5)
    attempts += 1

if attempts >= max_attempts:
    print(f"\n⚠️  Timeout: Batch scrape did not complete within {max_attempts * 5} seconds")
