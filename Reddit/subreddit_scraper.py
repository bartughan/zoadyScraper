import time
from datetime import datetime, timezone, timedelta
from Reddit.reddit_client import get_reddit_client


def fetch_all_subreddits(debug=False):
    reddit = get_reddit_client()
    seen = set()
    sources = [
        (reddit.subreddits.popular, 'popular'),
        (reddit.subreddits.new, 'new'),
        (reddit.subreddits.default, 'default'),
        (reddit.subreddits.search, 'search'),
    ]
    for listing, name in sources:
        if debug:
            print(f'Fetching subreddits from: {name}')
        if listing == reddit.subreddits.search:
            queries = ['a', 'e', 'i', 'o', 'u']
            for q in queries:
                if debug:
                    print(f'  Searching with query: {q}')
                for sub in listing(q, limit=None):
                    if sub.display_name not in seen:
                        seen.add(sub.display_name)
                        yield sub
        else:
            for sub in listing(limit=None):
                if sub.display_name not in seen:
                    seen.add(sub.display_name)
                    yield sub

def filter_subreddit(sub, keyword, min_subs, max_subs, max_age_days, debug=False):
    keyword = keyword.lower()
    title = (sub.title or '').lower()
    desc = (sub.public_description or '').lower()
    if keyword not in title and keyword not in desc:
        if debug:
            print(f'    Filtered out by keyword: {sub.display_name}')
        return False
    if min_subs != -1 and sub.subscribers < min_subs:
        if debug:
            print(f'    Filtered out by min_subs: {sub.display_name} ({sub.subscribers})')
        return False
    if max_subs != -1 and sub.subscribers > max_subs:
        if debug:
            print(f'    Filtered out by max_subs: {sub.display_name} ({sub.subscribers})')
        return False
    try:
        posts = list(sub.new(limit=1))
        if not posts:
            if debug:
                print(f'    Filtered out (no posts): {sub.display_name}')
            return False
        latest_post = posts[0]
        post_time = datetime.fromtimestamp(latest_post.created_utc, tz=timezone.utc)
        age_days = (datetime.now(timezone.utc) - post_time).days
        if max_age_days != -1 and age_days > max_age_days:
            if debug:
                print(f'    Filtered out by max_age_days: {sub.display_name} (latest post {age_days} days ago)')
            return False
    except Exception as e:
        if debug:
            print(f'    Exception while checking posts for {sub.display_name}: {e}')
        return False
    return True

def get_subreddit_data(sub, debug=False):
    # Fetch rules (use list(sub.rules) as per PRAW docs)
    rules_text = ''
    try:
        rules = list(sub.rules)
        rules_text = '\n'.join([f"{rule.short_name}: {rule.description}" for rule in rules])
        if debug:
            print(f"    Fetched {len(rules)} rules for {sub.display_name}")
    except Exception as e:
        if debug:
            print(f"    Could not fetch rules for {sub.display_name}: {e}")
        rules_text = ''
    # Calculate active user ratio (use sub.active_user_count if available)
    total = getattr(sub, 'subscribers', 0) or 0
    active = getattr(sub, 'active_user_count', None)
    if active is None:
        # Try accounts_active as fallback
        active = getattr(sub, 'accounts_active', None)
    if active is not None and total > 0:
        ratio = f"{active} ({active/total:.2%})"
    else:
        ratio = ''
    if debug:
        print(f"    Active users for {sub.display_name}: {active}, Total: {total}, Ratio: {ratio}")
    return {
        'Title': sub.display_name,
        'Total Users': total,
        'Active Users': ratio,
        'Description': sub.public_description,
        'Link': f'https://www.reddit.com/r/{sub.display_name}/',
        'Kurallar': rules_text
    } 