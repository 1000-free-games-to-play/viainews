import feedparser
import json
import time
from datetime import datetime
import re

# --- AI DATABASE CONFIGURATION ---
# Laser-targeted queries to separate highly technical research from mainstream industry news.
FEEDS = {
    "top_stories": ["https://news.google.com/rss/search?q=artificial+intelligence+OR+AI+news+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "models": ["https://news.google.com/rss/search?q=LLM+OR+OpenAI+OR+Anthropic+OR+Google+DeepMind+OR+foundation+model+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "tools": ["https://news.google.com/rss/search?q=AI+tool+OR+AI+app+OR+ChatGPT+OR+Claude+OR+developer+API+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "industries": ["https://news.google.com/rss/search?q=AI+in+healthcare+OR+AI+in+finance+OR+enterprise+AI+OR+AI+manufacturing+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "research": [
        "https://news.google.com/rss/search?q=machine+learning+paper+OR+AI+research+breakthrough+when:1d&hl=en-US&gl=US&ceid=US:en",
        "https://www.reddit.com/r/MachineLearning/top/.rss?t=day"
    ],
    "policy": ["https://news.google.com/rss/search?q=AI+regulation+OR+AI+policy+OR+AI+lawsuit+OR+copyright+OR+AI+safety+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "business": ["https://news.google.com/rss/search?q=AI+startup+funding+OR+venture+capital+AI+OR+AI+market+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "creative": [
        "https://news.google.com/rss/search?q=generative+AI+art+OR+Midjourney+OR+AI+video+Sora+when:1d&hl=en-US&gl=US&ceid=US:en",
        "https://www.reddit.com/r/StableDiffusion/top/.rss?t=day"
    ],
    "hardware": ["https://news.google.com/rss/search?q=AI+chips+OR+Nvidia+GPU+OR+AI+data+center+compute+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "community": [
        "https://www.reddit.com/r/LocalLLaMA/top/.rss?t=day",
        "https://www.reddit.com/r/singularity/top/.rss?t=day",
        "https://www.reddit.com/r/artificial/top/.rss?t=day"
    ],
    "global": ["https://news.google.com/rss/search?q=AI+Europe+OR+AI+China+OR+global+artificial+intelligence+when:1d&hl=en-US&gl=US&ceid=US:en"]
}

def fetch_feed_data(feed_urls, category_name):
    items = []
    for url in feed_urls:
        print(f"Scraping {category_name}: {url}")
        feed = feedparser.parse(url)
        
        for entry in feed.entries[:15]: 
            # Determine Source dynamically
            source_name = "AI db Leo"
            if "reddit.com" in url:
                # Extract subreddit name
                match = re.search(r'r/([^/]+)', url)
                source_name = f"r/{match.group(1)}" if match else "Reddit"
            elif hasattr(entry, 'source') and hasattr(entry.source, 'title'):
                source_name = entry.source.title
            else:
                # Fallback: Google News appends "- Source Name" to titles
                if " - " in entry.title:
                    source_name = entry.title.split(" - ")[-1]
                    entry.title = entry.title.rsplit(" - ", 1)[0] 

            # Parse Timestamp safely
            timestamp = int(time.time())
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                timestamp = int(time.mktime(entry.published_parsed))

            items.append({
                "title": entry.title,
                "link": entry.link,
                "source": source_name,
                "timestamp": timestamp
            })
            
    # Sort newest first and return top 25 per category
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return items[:25]

def main():
    print("Initializing AI db Leo Aggregation...")
    
    output_data = {
        "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data": {}
    }
    
    all_news_pool = []
    for category, urls in FEEDS.items():
        category_items = fetch_feed_data(urls, category)
        output_data["data"][category] = category_items
        all_news_pool.extend(category_items)
        
    # Generate the 'all' category
    all_news_pool.sort(key=lambda x: x["timestamp"], reverse=True)
    
    seen_links = set()
    unique_all = []
    for item in all_news_pool:
        if item["link"] not in seen_links:
            seen_links.add(item["link"])
            unique_all.append(item)
            
    output_data["data"]["all"] = unique_all[:60] 

    # Export Database
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        
    print("Database sync complete. news.json generated successfully.")

if __name__ == "__main__":
    main()
