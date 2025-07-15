import os
import json
import re
from dotenv import load_dotenv
from twitter_tool import TwitterScraper
from db_utils import TweetDBHandler

# ==== Load environment variables ====
load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
MONGODB_URI = os.getenv("MONGO_URI")

if not BEARER_TOKEN or not MONGODB_URI:
    raise ValueError("Missing required environment variables in .env file.")

def main():
    scraper = TwitterScraper(bearer_token=BEARER_TOKEN)
    db_handler = TweetDBHandler(uri=MONGODB_URI)

    search_term = input("🔍 Enter search term: ").strip()
    tweets = scraper.search_term_mentions(term=search_term, max_total=500)

    # Save to JSON
    safe_term = re.sub(r'\W+', '_', search_term.strip().lower())
    filename = f"{safe_term}_twitter.json"
    tweet_dicts = [tweet.model_dump() for tweet in tweets]

    with open(filename, "w") as f:
        json.dump(tweet_dicts, f, indent=2)
    print(f"\n✅ Saved {len(tweets)} tweets to {filename}")

    # Save to MongoDB
    db_handler.store_tweets(tweets, term=search_term)
    print(f"✅ Stored {len(tweets)} tweets in MongoDB.")

if __name__ == "__main__":
    main()
