from bs4 import BeautifulSoup
from datetime import date
from dateutil.parser import parse
import requests
from time import perf_counter
from urllib.parse import urljoin

def scrape(start_date=date.today(), verbose=0):
    """
    Finds all series listed under "Exclusive Light Novels" to get all sreies published by Book Walker.
    Runs all links through book_walker_series() and combines all results and returns them.
    Returns a list of dictionaries:
    [{'date', 'title', 'volume', 'publisher':'Book Walker', 'store_link', 'format':'Digital'}]
    """
    
    start_time = perf_counter()
    if verbose > 1:
        print('Starting scraping for Book Walker.')
    result = []
    url = 'https://global.bookwalker.jp/'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    series_list = soup.find('p', text='Exclusive Light Novels').parent.find_all('a')
    if verbose > 1:
        print(f'Found {len(series_list)} series.')
    for series in series_list:
        series_results = book_walker_series(urljoin(url, series['href']), start_date)
        if verbose > 2:
            print(f'{len(series_results)} found for "{series.get_text(strip=True)}".')
        result.extend(series_results)
    
    if verbose > 0:
        print(f'{len(result)} release(s) found for Book Walker, completed in {perf_counter()-start_time} seconds.')
    return result
    
def series_scrape(url, start_date=date.today()):
    """
    Takes a valid Book Walker series link (ex: https://global.bookwalker.jp/series/135449/the-ryuos-work-is-never-done/)
    and date in the future.
    Sorts volumes by date and save information until it comes across a date before the given date.
    Returns a list of dictionaries:
    [{'date', 'title', 'volume', 'publisher':'Book Walker', 'store_link', 'format':'Digital'}]
    """
    
    result = []
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    for item in soup.find_all('li', class_='o-tile'):
        
        date_tag = item.find('div', class_='a-tile-release-date')
        if date_tag is None:
            break
        release_date = parse(date_tag.get_text(strip=True).replace('.', ' ')).date()
        release_date = release_date.replace(year=date.year+(release_date.month<date.month))
        if release_date < start_date:
            break
            
        title_tag = item.find('h2', class_='a-tile-ttl').find('a')
        title_text = title_tag.get_text(strip=True).split(' Volume ').split(', Vol. ')
        title = title_text[0]
        volume = title_text[-1] if len(title_text)>1 else '1'
        link = urljoin(url, title_tag['href'])
        release = {'date': release_date,
                   'title': title,
                   'volume': volume,
                   'publisher': 'Book Walker',
                   'store_link': link,
                   'format': 'Digital'}
        result.append(release)
    
    return result