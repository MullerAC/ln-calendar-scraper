"""
To Do:
- split up physical and digital calendar scraping?
"""

from bs4 import BeautifulSoup
from datetime import date
from dateutil.parser import parse
import requests
from time import perf_counter
from urllib.parse import urljoin

def scrape(start_date=date.min, verbose=0):
    '''
    Seven Seas has two calendars:
    one for physical, and one for digital.
    Both are in the same format, but need to be scraped seperately.
    Returns a list of dictionaries:
    [{'date', 'title', 'volume', 'publisher':'Seven Seas', 'store_link', 'format'}]
    '''
    
    start_time = perf_counter()
    if verbose > 1:
        print('Starting scraping for Seven Seas.')
    result = []
    urls = [('https://sevenseasentertainment.com/digital/', 'Digital'), ('https://sevenseasentertainment.com/release-dates/', 'Physical')]
    
    for url, format_type in urls:
        if verbose > 2:
            print('Scraping {format_type} calendar.}')
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        
        for item in soup.find_all('tr', id='volumes'):
            cells = item.find_all('td')
            
            release_date = parse(cells[0].get_text(strip=True)).date()
            if release_date < start_date:
                continue
                
            title_tag = cells[1].find('a')
            title_split = title_tag.get_text(strip=True).replace(' (Light Novel)', '').replace(' (Novel)', '').split(' Vol. ')
            title = title_split[0]
            volume = title_split[-1] if len(title_split)>1 else '1'
            link = urljoin(url, title_tag['href'])
                
            if 'Novel' not in cells[2].get_text():
                continue
            
            release = {'date': release_date,
                       'title': title,
                       'volume': volume,
                       'publisher': 'Seven Seas',
                       'store_link': link,
                       'format': format_type}
            result.append(release)
    
    if verbose > 0:
        print(f'{len(result)} releases found for Seven Seas, completed in {perf_counter()-start_time} seconds.')
    return result

def series(url, start_date=date.min):
    """
    Takes a valid Seven Seas series link
    (ex: https://sevenseasentertainment.com/series/mushoku-tensei-jobless-reincarnation-light-novel/)
    and datetime.date object.
    Scrapes from the bottom up,
    stopping when coming across a volume with a date before start_date.
    Returns a list of dictionaries:
    [{'date':datetime.date, 'title':string, 'volume':string, 'publisher':'Seven Seas', 'publisher_link':string, 'format':string}]
    """
    
    result = []
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    title = soup.find('h2', {'class':'topper'}).find('span').next_sibling.get_text(strip=True).replace(' (Light Novel)', '').replace(' (Novel)', '')

    items = soup.find_all('div', {'class':'series-volume'})
    items.reverse()

    for item in items:
        volume_tag = item.find('h3')
        volume_split = volume_tag.get_text(strip=True).split(' Vol. ')
        volume = title_split[-1] if len(title_split)>1 else '1'
        link = volume_tag.find('a')['href']
        release_date_physical = parse(soup.find('b', {'text':'Release Date'}).next_sibling.get_text().replace(':', '').strip()).date()
        early_digital_tag = parse(soup.find('b', {'text':'Early Digital:'})

        if release_date_physical < start_date and (early_digital_tag is None or release_date_digital < start_date):
            break

        release_physical = {'date': release_date_physical,
                           'title': title,
                           'volume': volume,
                           'publisher': 'Seven Seas',
                           'store_link': link,
                           'format': 'Physical'}

        if early_digital_tag is not None:
            release_date_digital = early_digital_tag.next_sibling.get_text().strip()).date()
            release_digital = {'date': release_date_digital,
                               'title': title,
                               'volume': volume,
                               'publisher': 'Seven Seas',
                               'store_link': link,
                               'format': 'Digital'}

        if release_date_physical > start_date:
            result.append(release_physical)
        if early_digital_tag is not None and release_date_digital > start_date:
            result.append(release_digital)

    return result

def volume(url):
    """
    Takes a valid Book Walker series link
    (ex: https://sevenseasentertainment.com/books/mushoku-tensei-jobless-reincarnation-light-novel-vol-2/)
    and scrapes all relavent information.
    Returns a list of dictionaries:
    [{'date':datetime.date, 'title':string, 'volume':string, 'publisher':'Seven Seas'', 'publisher_link':string, 'format':'Physical'},
     {'date':datetime.date, 'title':string, 'volume':string, 'publisher':'Seven Seas'', 'publisher_link':string, 'format':'Digital'}]
    """

    result = []
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    title_text = soup.find('h2', {'class':'topper'}).find('span').next_sibling.get_text(strip=True).replace(' (Light Novel)', '').replace(' (Novel)', '').split(' Vol. ')
    title = title_split[0]
    volume = title_split[-1] if len(title_split)>1 else '1'

    release_date_physical = parse(soup.find('b', {'text':'Release Date:'}).next_sibling.get_text().strip()).date()
    early_digital_tag = parse(soup.find('b', {'text':'Early Digital:'})

    release_physical =  {'date': release_date_physical,
                 'title': title,
                 'volume': volume,
                 'publisher': 'Seven Seas',
                 'publisher_link': url,
                 'format': 'Physical'}
    result.append(release_physical)

    if early_digital_tag is not None:
        release_date_digital = early_digital_tag.next_sibling.get_text().strip()).date()
        release_digital = {'date': release_date_digital,
                           'title': title,
                           'volume': volume,
                           'publisher': 'Seven Seas',
                           'store_link': url,
                           'format': 'Digital'}
        result.append(release_digital)
        
    return result