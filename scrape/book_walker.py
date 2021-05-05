from bs4 import BeautifulSoup
from datetime import date
from dateutil.parser import parse
import requests
from time import perf_counter
from urllib.parse import urljoin

def scrape(start_date=date.min, verbose=0):
    """
    Finds all series listed under "Exclusive Light Novels" to get all sreies published by Book Walker.
    Runs all links through book_walker_series() and combines all results and returns them.
    Returns a list of dictionaries:
    [{'date', 'title', 'volume', 'publisher':'Book Walker', 'publisher_link', 'format':'Digital'}]
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
        series_results = series(urljoin(url, series['href']), start_date)
        if verbose > 2:
            print(f'{len(series_results)} found for "{series.get_text(strip=True)}".')
        result.extend(series_results)
    
    if verbose > 0:
        print(f'{len(result)} release(s) found for Book Walker, completed in {perf_counter()-start_time} seconds.')
    return result
    
def series(url, start_date=date.min):
    """
    Takes a valid Book Walker series link
    (ex: https://global.bookwalker.jp/series/135449/the-ryuos-work-is-never-done/)
    and datetime.date object.
    Sorts volumes by date and save information until it comes across a date before the given date.
    Returns a list of dictionaries:
    [{'date':datetime.date, 'title':string, 'volume':string, 'publisher':'Book Walker', 'publisher_link':string, 'format':'Digital'}]
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
                   'publisher_link': link,
                   'format': 'Digital'}
        result.append(release)
    
    return result

def volume(url):
    """
    Takes a valid Book Walker series link
    (ex: https://global.bookwalker.jp/de33fea597-f52a-4db8-8bee-d0c2339e6557/the-ryuos-work-is-never-done-vol-11/)
    and scrapes all relavent information.
    Returns a dictionary:
    {'date':datetime.date, 'title':string, 'volume':string, 'publisher':string, 'publisher_link':string, 'format':'Digital'}
    """

    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    title_text = soup.find('h1', {'itemprop':'name'}).get_text(strip=True).split(', Vol.')
    title = title_text[0].strip()
    volume = title_text[1].split('-')[0].strip()

    release_date = parse(soup.find('span', {'itemprop':'productionDate'}).get_text(strip=True).split(' (')[0]).date()
    publisher = soup.find('span', {'itemprop':'brand'}).get_text(strip=True)

    result =  {'date': release_date,
               'title': title,
               'volume': volume,
               'publisher': publisher,
               'publisher_link': url,
               'format': 'Digital'}
    return result
