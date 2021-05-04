from bs4 import BeautifulSoup
from datetime import date
from dateutil.parser import parse
import requests
from time import perf_counter
from urllib.parse import urljoin

def scrape(date = date.today(), verbose=0): # todo: split physical and digital scraping, split out calender generl scraping from those two, cell them both in main scrape function; create series & volume scrapers
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
            if release_date < date:
                continue
                
            title_tag = cells[1].find('a')
            title_split = title_tag.get_text(strip=True).replace(' (Light Novel)', '').replace(' (Novel)', '').split(' Vol. ')
            title = title_split[0]
            volume = title_split[-1] if len(title_split)>1 else '1 [End]'
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