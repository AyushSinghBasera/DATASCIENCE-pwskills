from pymongo import MongoClient
from typing import List
import re
from pydantic_models import TweetData

class TweetDBHandler:
    def __init__(self, uri: str, db_name: str = "twitter_db", collection_name: str = "tweets"):
        self.client = MongoClient(uri)
        self.collection = self.client[db_name][collection_name]

    def store_tweets(self, tweets: List[TweetData], term: str):
        term_safe = re.sub(r'\W+', '_', term.strip().lower())
        for tweet in tweets:
            data = tweet.model_dump()
            data["search_term"] = term_safe
            self.collection.insert_one(data)
