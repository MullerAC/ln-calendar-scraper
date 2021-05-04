from bs4 import BeautifulSoup
from datetime import date
from dateutil.parser import parse
import requests
from time import perf_counter
from urllib.parse import urljoin

def scrape(start_date=date.today(), verbose=0):
    """
    Dark Horse has no calendar or way to search for only light novels (the also release many other types of books).
    Runs a search for Vampire Hunter D (Dark Horse's only active license) and searches that page for upcoming releases.
    Returns a list of dictionaries:
    [{'date', 'title', 'volume', 'publisher':'Book Walker', 'store_link', 'format':'Digital'}]
    """
    
    start_time = perf_counter()
    if verbose > 1:
        print('Starting scraping for Dark Horse.')
    result = []
    url = f'https://www.darkhorse.com/Search/Browse/"vampire+hunter+d"---Books---{start_date.strftime("%B+%Y")}-December+2099/Ppydwkt8'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    items = soup.find_all('div', class_='list_item')
    if verbose > 2:
        print(f'Found {len(items)} items.')
    for item in items:
        href = item.find('a')['href']
        result.append(dark_horse_volume(urljoin(url, href), start_date))
    
    if verbose > 0:
        print(f'{len(result)} release(s) found for Dark Horse, completed in {perf_counter()-start_time} seconds.')
    return result

def volume_scrape(url, start_date=date.today()): # todo: need to double check on format, check if release date is before start date
    """
    Dark Horse calendar does not have all information on it,
    need to check individual volume pages to get release date.
    Returns a dictionaries:
    {'date', 'title', 'volume', 'publisher':'Dark Horse', 'store_link', 'format':'Physical & Digital'}
    """
    
    result = []
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    title_text = soup.find('h2', class_='title').get_text(strip=True).split(':')[0]
    if ' Volume ' in title_text:
        title_text_split = title_text.split(' Volume ')
        title = title_text_split[0]
        volume = title_text_split[1].split(':')[0]
    else:
        title = title_text
        volume = '1'
    
    details = soup.find('div', class_='product-meta').find_all('dd')
    release_date = parse(details[0].get_text(strip=True)).date()
    # format_type = details[1].get_text(strip=True)
    
    release = {'date': release_date,
               'title': title,
               'volume': volume,
               'publisher': 'Dark Horse',
               'store_link': url,
               'format': 'Physical & Digital'}
    return release