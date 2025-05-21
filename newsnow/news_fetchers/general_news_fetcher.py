import feedparser
from dateutil import parser as date_parser
import time
import json
import os

RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "http://mf.reuters.com/mf/rss/TopNews", # Updated Reuters feed URL
]

MAX_ARTICLES_PER_FEED = 10

def fetch_general_news():
    """
    Fetches news items from a list of RSS feeds.

    Returns:
        list: A list of dictionaries, where each dictionary represents a news item.
              Returns an empty list if fetching or parsing fails for all feeds.
    """
    all_news_items = []
    # serial_number assignment will be done after collecting all items

    for feed_url in RSS_FEEDS:
        try:
            print(f"Fetching news from: {feed_url}")
            # Add a small delay to be polite to the servers
            time.sleep(1)
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                print(f"Warning: Malformed feed or error parsing {feed_url}. Bozo exception: {feed.bozo_exception}")
                # Continue to the next feed if this one is malformed
                # but still try to process entries if any were parsed
            
            if feed.status != 200 and feed.status != 301 and feed.status != 302 : # Handle common redirect codes
                 print(f"Warning: HTTP status {feed.status} for feed {feed_url}")
                 # Optionally, you could skip this feed entirely if the status is critical
                 # continue 

            processed_articles_count = 0
            for entry in feed.entries:
                if processed_articles_count >= MAX_ARTICLES_PER_FEED:
                    break
                try:
                    title = entry.get("title", "N/A")
                    link = entry.get("link", "N/A")
                    
                    published_date_str = entry.get("published") or entry.get("updated")
                    if published_date_str:
                        try:
                            published_datetime = date_parser.parse(published_date_str)
                            formatted_date = published_datetime.strftime("%Y-%m-%d %H:%M")
                        except (ValueError, TypeError) as e:
                            print(f"Could not parse date '{published_date_str}' for article '{title}': {e}")
                            formatted_date = "N/A"
                    else:
                        formatted_date = "N/A"

                    summary = entry.get("summary") or entry.get("description", "N/A")

                    news_item = {
                        "title": title,
                        "link": link,
                        "published_date": formatted_date,
                        "summary": summary,
                        # Serial number will be assigned later
                    }
                    all_news_items.append(news_item)
                    processed_articles_count += 1
                except Exception as e:
                    print(f"Error processing entry '{entry.get('title', 'Unknown title')}' from {feed_url}: {e}")
            print(f"Fetched {processed_articles_count} articles from {feed_url}")

        except Exception as e:
            print(f"Error fetching or parsing feed {feed_url}: {e}")
            # Continue to the next feed
            continue
    
    # Assign serial numbers
    for i, item in enumerate(all_news_items):
        item["serial_no"] = i + 1

    return all_news_items

def save_news_to_json(news_items, filepath):
    """
    Saves the list of news items to a JSON file.

    Args:
        news_items (list): The list of news item dictionaries to save.
        filepath (str): The path to the JSON file where news should be saved.
    """
    try:
        # Ensure the directory exists
        output_dir = os.path.dirname(filepath)
        if output_dir: # Check if output_dir is not empty (i.e., not saving in current dir)
            os.makedirs(output_dir, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(news_items, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved news to {filepath}")
    except IOError as e:
        print(f"Failed to save news to {filepath}. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while saving news to {filepath}: {e}")

if __name__ == '__main__':
    print("Fetching general news for standalone script run...")
    news_items = fetch_general_news()

    if news_items:
        print(f"Fetched {len(news_items)} news items.")
        # Determine path relative to this script file for standalone execution
        # newsnow/news_fetchers/general_news_fetcher.py -> newsnow/data/general_news.json
        script_dir = os.path.dirname(__file__)
        output_filepath = os.path.join(script_dir, '..', 'data', 'general_news.json')
        save_news_to_json(news_items, output_filepath)
    else:
        print("No news items fetched to save.")
