import praw
from Reddit.config import get_credentials

def get_reddit_client():
    creds = get_credentials()
    reddit = praw.Reddit(
        client_id=creds['client_id'],
        client_secret=creds['client_secret'],
        user_agent=creds['user_agent']
    )
    return reddit 