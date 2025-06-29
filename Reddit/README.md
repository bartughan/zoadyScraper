# Reddit Subreddit Scraper

This command-line tool scrapes subreddits from Reddit using the Reddit API, with filters for keyword, subscriber count, and latest post age. Results are saved to a CSV file.

## Features
- Filter subreddits by keyword in title or description
- Filter by minimum and maximum subscriber count
- Filter by age of the latest post
- Output results to a CSV file

## Setup
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Get Reddit API credentials:**
   - Go to https://www.reddit.com/prefs/apps
   - Click "create another app"
   - Set type to "script"
   - Fill in name, description, and redirect URI (can be http://localhost:8080)
   - Save and copy your client ID and client secret
3. **First run:**
   - The tool will prompt you for your credentials and store them in `reddit_config.json` for future use.

## Usage
```bash
python main.py --keyword KEYWORD --min-subs MIN --max-subs MAX --max-age-days DAYS --output OUTPUT.csv
```
- `--keyword`: Keyword to search in subreddit title or description (required)
- `--min-subs`: Minimum subscriber count (default: -1 for no limit)
- `--max-subs`: Maximum subscriber count (default: -1 for no limit)
- `--max-age-days`: Maximum age in days for the latest post (default: -1 for no limit)
- `--output`: Output CSV file path (required)

**Example:**
```bash
python main.py --keyword gaming --min-subs 10000 --max-subs 1000000 --max-age-days 7 --output gaming_subs.csv
``` 