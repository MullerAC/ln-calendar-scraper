"""
To Do:
- .get_format() does not work with digital releases; need to find a way to detect them
- need a way to find new active licenses
"""

from bs4 import BeautifulSoup
from datetime import date
from dateutil.parser import parse
import requests
from time import perf_counter
from urllib.parse import urljoin
from utils import get_format

def scrape(start_date=date.min, verbose=False):
    """
    Dark Horse has no calendar or way to search for only light novels (the also release many other types of books).
    Manually saves all known active licenses and runs them through the .series() method.
    Returns a list of dictionaries:
    [{'date':datetime.date, 'title':string, 'volume':string, 'publisher':'Dark Horse', 'publisher_link':string, 'format':string}]
    """
    
    start_time = perf_counter()
    if verbose: print('Starting scraping for Dark Horse.')

    result = []
    series = ['Vampire Hunter D']

    for title in series:
        series_result = series(title, start_date)
        result.apend(series_result)
    
    if verbose: print(f'{len(result)} release(s) found for Dark Horse, completed in {perf_counter()-start_time} seconds.')
    return result

def series(title, start_date=date.min):
    """
    Takes a Dark Horse series title
    (ex: Vampire Hunter D),
    searches for releases after or on the specified date,
    and scrapes each volume individually for needed information.
    Returns a list of dictionaries:
    [{'date':datetime.date, 'title':string, 'volume':string, 'publisher':'Dark Horse', 'publisher_link':string, 'format':string}]
    """

    result = []
    url = f'https://www.darkhorse.com/Search/Browse/"{title.lower().replace(' ', '+')}"---Books---{start_date.strftime("%B+%Y")}-December+2099/Ppydwkt8'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    items = soup.find_all('div', {'class':'list_item'})
    for item in items:
        url = urljoin(url, item.find('a')['href'])
        result.append(volume(url))
    
    return result

def volume(url):
    """
    Takes in a valid Dark Horse volume url
    (ex: https://www.darkhorse.com/Books/3004-474/Vampire-Hunter-D-Volume-29-Noble-Front-TPB),
    and scrapes all relavent information from the page.
    Returns a dictionary:
    {'date':datetime.date, 'title':string, 'volume':string, 'publisher':'Dark Horse', 'publisher_link':string, 'format':'Physical & Digital'}
    """
    
    result = []
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    title_text = soup.find('h2', {'class':'title'}).get_text(strip=True).split(':')[0].split(' Volume ')
    title = title_text_split[0]
    volume = title_text_split[1] if len(title_text)>1 else '1'
    
    details = soup.find('div', {'class':'product-meta'}).find_all('dd')
    release_date = parse(details[0].get_text(strip=True)).date()
    format_type = get_format(details[1].get_text()) # digital isn't listed under format, so brute forced to physical and digital for now
    
    release = {'date': release_date,
               'title': title,
               'volume': volume,
               'publisher': 'Dark Horse',
               'publisher_link': url,
               'format': 'Physical & Digital'}
    return release