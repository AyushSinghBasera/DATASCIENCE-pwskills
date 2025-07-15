import tweepy
import time
from typing import List
from datetime import datetime, timezone
from pydantic_models import TweetData

class TwitterScraper:
    def __init__(self, bearer_token: str):
        self.client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)

    def search_term_mentions(self, term: str, max_total: int = 50) -> List[TweetData]:
        query = f'"{term}" -is:retweet lang:en'
        tweets_collected = []
        next_token = None

        while len(tweets_collected) < max_total:
            remaining = max_total - len(tweets_collected)
            fetch_count = min(100, remaining)

            try:
                response = self.client.search_recent_tweets(
                    query=query,
                    tweet_fields=["created_at", "public_metrics"],
                    expansions="author_id",
                    user_fields=["username", "name"],
                    max_results=fetch_count,
                    next_token=next_token
                )
            except tweepy.TooManyRequests:
                print("⚠️ Rate limit exceeded. Sleeping for 60 seconds...")
                time.sleep(60)
                continue
            except Exception as e:
                print(f"❌ Error fetching tweets: {e}")
                break

            if not response.data:
                break

            tweets_collected.extend(self._format_tweets(response))
            next_token = response.meta.get("next_token")
            if not next_token:
                break

        return tweets_collected

    def _format_tweets(self, response) -> List[TweetData]:
        if not response or not response.data:
            return []

        users = {u.id: u for u in response.includes.get("users", [])} if hasattr(response, "includes") else {}
        formatted = []

        for tweet in response.data:
            user_info = users.get(tweet.author_id) if hasattr(tweet, "author_id") else None
            formatted.append(TweetData(
                username=user_info.username if user_info else "unknown",
                display_name=user_info.name if user_info else "unknown",
                tweet_id=str(tweet.id),
                text=tweet.text,
                created_at=str(tweet.created_at),
                like_count=tweet.public_metrics.get("like_count", 0),
                retweet_count=tweet.public_metrics.get("retweet_count", 0),
                reply_count=tweet.public_metrics.get("reply_count", 0),
                scraped_at=datetime.now(timezone.utc).isoformat()
            ))
        return formatted
