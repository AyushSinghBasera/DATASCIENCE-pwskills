from pydantic import BaseModel
from typing import List

class TweetData(BaseModel):
    username: str
    display_name: str
    tweet_id: str
    text: str
    created_at: str
    like_count: int
    retweet_count: int
    reply_count: int
    scraped_at: str
