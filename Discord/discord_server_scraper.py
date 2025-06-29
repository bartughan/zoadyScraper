import argparse
import xlsxwriter
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


def parse_args():
    parser = argparse.ArgumentParser(description='Discord Server Scraper (discordservers.com, Selenium)')
    parser.add_argument('--keyword', required=True, help='Keyword to search in server name or description')
    parser.add_argument('--max-loads', type=int, default=5, help='How many times to click Load More Servers')
    parser.add_argument('--min-members', type=int, default=-1, help='Minimum member count (-1 for no limit)')
    parser.add_argument('--max-members', type=int, default=-1, help='Maximum member count (-1 for no limit)')
    parser.add_argument('--output', required=True, help='Output Excel file path (.xlsx)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    return parser.parse_args()

def scrape_discordservers(keyword, max_loads=5, min_members=-1, max_members=-1, debug=False):
    url = f'https://discordservers.com/search/{keyword}'
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(3)
    for i in range(max_loads):
        try:
            load_more = driver.find_element(By.XPATH, "//button[contains(., 'Load More Servers')]")
            driver.execute_script("arguments[0].scrollIntoView();", load_more)
            time.sleep(1)
            load_more.click()
            if debug:
                print(f"Clicked Load More Servers ({i+1}/{max_loads})")
            time.sleep(2.5)
        except (NoSuchElementException, ElementClickInterceptedException):
            if debug:
                print("No more 'Load More Servers' button found or not clickable.")
            break
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    server_cards = soup.find_all('article', attrs={'role': 'region', 'aria-label': 'server name'})
    if not server_cards:
        print('Hiç sunucu bulunamadı!')
        driver.quit()
        return []
    servers = []
    for idx, card in enumerate(server_cards, 1):
        name_tag = card.find('p', itemprop='name')
        name = name_tag.get_text(strip=True) if name_tag else ''
        desc_tag = card.find('div', itemprop='headline')
        desc = desc_tag.get_text(strip=True) if desc_tag else ''
        member_tag = card.find('span', class_='pl-2')
        members = member_tag.get_text(strip=True) if member_tag else ''
        try:
            members_int = int(''.join(filter(str.isdigit, members)))
        except Exception:
            members_int = 0
        # Min/max filtrelemesi
        if min_members != -1 and members_int < min_members:
            continue
        if max_members != -1 and members_int > max_members:
            continue
        parent_a = card.find_parent('a')
        link = ''
        if parent_a and parent_a.has_attr('href'):
            if parent_a['href'].startswith('http'):
                link = parent_a['href']
            else:
                link = 'https://discordservers.com' + parent_a['href']
        print(f"[{idx}] Ad: {name}\nAçıklama: {desc}\nÜye: {members}\nLink: {link}\n")
        servers.append({
            'Name': name,
            'Description': desc,
            'Members': members,
            'Link': link
        })
    driver.quit()
    return servers

def write_excel_with_links(rows, output_xlsx):
    fieldnames = ['Name', 'Description', 'Members', 'Link']
    workbook = xlsxwriter.Workbook(output_xlsx)
    worksheet = workbook.add_worksheet()
    for col, name in enumerate(fieldnames):
        worksheet.write(0, col, name)
    for row_idx, row in enumerate(rows, 1):
        for col, key in enumerate(fieldnames):
            if key == 'Link' and row.get('Link'):
                worksheet.write_url(row_idx, col, row['Link'], string=row['Link'])
            else:
                worksheet.write(row_idx, col, row.get(key, ''))
    workbook.close()

def main():
    args = parse_args()
    servers = scrape_discordservers(
        keyword=args.keyword,
        max_loads=args.max_loads,
        min_members=args.min_members,
        max_members=args.max_members,
        debug=args.debug
    )
    if servers:
        write_excel_with_links(servers, args.output)
        print(f'Successfully wrote {len(servers)} servers to {args.output}')

if __name__ == '__main__':
    main() 