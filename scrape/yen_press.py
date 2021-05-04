from bs4 import BeautifulSoup
from datetime import date
from dateutil.parser import parse
import requests
from time import perf_counter
from urllib.parse import urljoin

def scrape(start_date = date.today(), verbose=0): # todo: split out volume scraping, add series scraping, find new yen audio label calendar somewhere
    '''
    Yen On calendar has only light novels and a section for each month,
    but releases are not ordered by date within each month.
    Returns a list of dictionaries:
    [{'date', 'title', 'volume', 'publisher':'Yen Press', 'store_link', 'format'}]
    '''

    start_time = perf_counter()
    if verbose > 1:
        print('Starting scraping for Yen Press.')
    result = []
    url = 'https://yenpress.com/yen-on/'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    months = soup.find_all('div', class_='book-shelf-wrap')

    for month in months:
        for item in month.find_all('li'):
            link = urljoin(url, item.find('a')['href'])
            soup = BeautifulSoup(requests.get(link).text, 'html.parser')

            title_text = soup.find('title').get_text(strip=True).split(' | ')[0].replace(' (light novel)', '').split(', Vol. ')
            title = title_text[0]
            volume = title_text[-1] if len(title_text)>1 else '1'
            if title == 'Solo Leveling':
                continue

            release_date = parse(soup.find_all('span', class_='detail-value')[-1].get_text(strip=True)).date()
            if release_date < start_date:
                continue

            format_text = soup.find('div', id='book-format-details').get_text()
            if ('Paperback' in format_text) or ('Hardcover' in format_text):
                if 'Digital' in format_text:
                    format_type = 'Physical & Digital'
                else:
                    format_type = 'Physical'
            elif 'Digital' in format_text:
                    format_type = 'Digital'
            else:
                format_type = 'Other'
            
            release = {'date': release_date, 'title': title, 'volume': volume, 'publisher': 'Yen Press', 'store_link': link, 'format': format_type}
            result.append(release)
    
    if verbose > 0:
        print(f'{len(result)} releases found for Yen Press, completed in {perf_counter()-start_time} seconds.')
    return result