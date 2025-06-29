import argparse
import requests
from bs4 import BeautifulSoup
import xlsxwriter
from Reddit.subreddit_scraper import fetch_all_subreddits, filter_subreddit, get_subreddit_data

def get_online_users_requests(subreddit_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        resp = requests.get(subreddit_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for span in soup.find_all('span'):
                if 'online' in span.text.lower():
                    faceplate = span.find('faceplate-number')
                    if faceplate and faceplate.has_attr('number'):
                        print(f"[requests] {subreddit_url} -> {faceplate['number']}")
                        return faceplate['number']
            for faceplate in soup.find_all('faceplate-number'):
                parent = faceplate.find_parent('span')
                if parent and 'online' in parent.text.lower():
                    print(f"[requests] {subreddit_url} -> {faceplate.get('number')}")
                    return faceplate.get('number')
        return ''
    except Exception as e:
        print(f"Error for {subreddit_url}: {e}")
        return ''

def parse_args():
    parser = argparse.ArgumentParser(description='Reddit Subreddit Scraper')
    parser.add_argument('--keyword', required=True, help='Keyword to search in subreddit title or description')
    parser.add_argument('--min-subs', type=int, default=-1, help='Minimum subscriber count (-1 for no limit)')
    parser.add_argument('--max-subs', type=int, default=-1, help='Maximum subscriber count (-1 for no limit)')
    parser.add_argument('--max-age-days', type=int, default=-1, help='Maximum age in days for the latest post (-1 for no limit)')
    parser.add_argument('--output', required=True, help='Output Excel file path (.xlsx)')
    parser.add_argument('--search-limit', type=int, default=-1, help='Maximum number of subreddits to process (-1 for no limit)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    return parser.parse_args()

def main():
    args = parse_args()
    checked = 0
    print('Starting subreddit search...')
    fieldnames = ['Title', 'Total Users', 'Online Users', 'Online Ratio', 'Description', 'Link', 'Kurallar']
    rows = []
    for sub in fetch_all_subreddits(debug=args.debug):
        checked += 1
        if args.search_limit != -1 and checked > args.search_limit:
            print(f'Reached search limit of {args.search_limit}. Stopping.')
            break
        if args.debug:
            print(f'Checking subreddit: {sub.display_name}')
        if filter_subreddit(sub, args.keyword, args.min_subs, args.max_subs, args.max_age_days, debug=args.debug):
            if args.debug:
                print(f'  -> PASSED: {sub.display_name}')
            row = get_subreddit_data(sub, debug=args.debug)
            online_users = get_online_users_requests(row['Link'])
            row['Online Users'] = online_users
            try:
                total = int(row['Total Users'])
                online = int(online_users) if online_users else 0
                ratio = f"{(online/total*100):.2f}%" if total > 0 else ''
            except Exception:
                ratio = ''
            row['Online Ratio'] = ratio
            row.pop('Active Users', None)
            rows.append(row)
        elif args.debug:
            print(f'  -> FAILED: {sub.display_name}')
    # Write to Excel
    workbook = xlsxwriter.Workbook(args.output)
    worksheet = workbook.add_worksheet()
    # Write header
    for col, name in enumerate(fieldnames):
        worksheet.write(0, col, name)
    # Write data
    for row_idx, row in enumerate(rows, 1):
        for col, key in enumerate(fieldnames):
            if key == 'Link' and row.get('Link'):
                worksheet.write_url(row_idx, col, row['Link'], string=row['Link'])
            else:
                worksheet.write(row_idx, col, row.get(key, ''))
    workbook.close()
    print(f'Successfully wrote subreddits to {args.output}')

if __name__ == '__main__':
    main() 