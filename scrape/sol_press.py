from bs4 import BeautifulSoup
from datetime import date
from dateutil.parser import parse
import requests
from time import perf_counter
from urllib.parse import urljoin

def scrape(start_date=date.today(), verbose=0): # todo: test with old dates, create series & volume scraping
    '''
    Sol Press only lists digital releases on their calendar.
    May need to revisit if they add physicals.
    No releases are currently scheduled, will need to test later.
    Returns a list of dictionaries:
    [{'date', 'title', 'volume', 'publisher':'Sol Press', 'store_link', 'format':'Digital'}]
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