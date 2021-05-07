"""
To Do:
- test with old dates
"""

from bs4 import BeautifulSoup
from datetime import date
from dateutil.parser import parse
import requests
from time import perf_counter
from urllib.parse import urljoin

def scrape(start_date=date.min, verbose=0):
    '''
    Sol Press only lists digital releases on their calendar.
    May need to revisit if they add physicals.
    No releases are currently scheduled, will need to test later.
    Returns a list of dictionaries:
    [{'date':datetime.date, 'title':string, 'volume':string, 'publisher':'Sol Press', 'store_link':string, 'format':'Digital'}]
    '''

    start_time = perf_counter()
    if verbose > 1:
        print('Starting scraping for Sol Press.')
    result = []
    url = 'https://solpress.co/light-novels'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    for item in soup.find_all('section', class_='details'):
        title_tag = item.find('a')
        title_split = title_tag.get_text(strip=True).replace(' (light novel)', '').split(' Vol. ')
        title = title_split[0]
        volume = title_split[1].split(':')[0] if len(title_split)>1 else '1'
        link = urljoin(url, title_tag['href'])

        release_date_text = item.find('section', class_='secondary-details').find_all('strong')[-1].get_text(strip=True)
        if 'To be announced' in release_date_text[0]:
            continue
        release_date = parse(release_date_text).date()
        if release_date < start_date:
            break

        release = {'date': release_date,
                   'title': title,
                   'volume': volume,
                   'publisher': 'Sol Press',
                   'store_link': link,
                   'format': 'Digital'}
        result.append(release)

    if verbose > 0:
        print(f'{len(result)} releases found for Sol Press, completed in {perf_counter()-start_time} seconds.')
    return result

def series(url, start_date=date.min):
    '''
    Takes in a target date and a valid series url
    (ex: https://solpress.co/series/751/chivalry-of-a-failed-knight)
    and scrapes the site for needed information for releases after start_date.
    Sol Press only lists digital releases on their calendar;
    may need to revisit if they add physicals.
    Returns a list of dictionaries:
    [{'date':datetime.date, 'title':string, 'volume':string, 'publisher':'Sol Press', 'store_link':string, 'format':'Digital'}]
    '''

    result = []
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    title = soup.find('h1', {'class':'title'}).get_text(strip=True)

    for item in soup.find_all('a', {'class':'no-animation'}):

        link = urljoin(url, item['href'])
        volume_split = item.find('span', {'class':'work_title'}).get_text(strip=True).split(' Vol. ')
        volume = volume_split[-1] if len(volume_split)>1 else '1'
        release_date = parse(item.find('span', {'class':'release_date'}).get_text(strip=True)).date()

        release = {'date': release_date,
                   'title': title,
                   'volume': volume,
                   'publisher': 'Sol Press',
                   'store_link': link,
                   'format': 'Digital'}
        if release_date >= start_date:
            result.append(release)
    
    return result

def volume(url):
    '''
    Takes in a valid volume url
    (ex: https://solpress.co/product/884/chivalry-of-a-failed-knight-vol-5)
    and scrapes the site for needed information.
    Sol Press only lists digital releases on their calendar;
    may need to revisit if they add physicals.
    Returns a dictionaru:
    {'date':datetime.date, 'title':string, 'volume':string, 'publisher':'Sol Press', 'store_link':string, 'format':'Digital'}
    '''

    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    title_split = soup.find('h1', {'class':'title'}).get_text(strip=True).split(' Vol. ')
    title = title_split[0]
    volume = title_split[-1] if len(volume_split)>1 else '1'
    release_date = parse(item.find('section', {'class':'details'}).find('div', {'class':'infobox'}).find('strong').get_text(strip=True)).date()

    
    result = {'date': release_date,
              'title': title,
              'volume': volume,
              'publisher': 'Sol Press',
              'store_link': url,
              'format': 'Digital'}
    return result