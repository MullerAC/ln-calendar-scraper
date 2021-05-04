from bs4 import BeautifulSoup
from datetime import date
from dateutil.parser import parse
import requests
from time import perf_counter
from urllib.parse import urljoin

def scrape(start_date = date.today()), verbose=0: # todo: use next_month variable (as in square_enix()) to make a verbose level 2 for each month scraped
    '''
    Viz calendar has a different page for each month,
    easily accessed by by putting the year and month into the url.
    Returns a list of dictionaries:
    [{'date', 'title', 'volume', 'publisher':'Sol Press', 'store_link', 'format':'Digital'}]
    '''

    start_time = perf_counter()
    if verbose > 1:
        print('Starting scraping for Viz Media.')
    result = []
    url = 'https://www.viz.com/calendar/'
    m, y = start_date.month, start_date.year
    soup = BeautifulSoup(requests.get(url + f'{y}/{m}').text, 'html.parser')

    while soup.find('table', class_='product-table') is not None:
        for item in soup.find_all('tr'):
            cells = item.find_all('td')

            if cells[2].get_text(strip=True) != 'Novel':
                continue

            title_text = cells[3].get_text(strip=True).split(', Vol. ')
            title = title_text[0]
            volume = title_text[-1] if len(title_text)>1 else '1'

            link_end = cells[3].find('a')['href']
            link_end = link_end[:link_end.rfind('/')]
            link = urljoin(url, link_end)

            release_date = parse(cells[4].get_text(strip=True)).date()
            if release_date < start_date:
                continue

            soup = BeautifulSoup(requests.get(link).text, 'html.parser')
            format_text = soup.find('div', class_='type-rg type-md--md weight-bold').get_text(strip=True)
            if ('Paperback' in format_text) or ('Hardcover' in format_text):
                if 'Digital' in format_text:
                    format_type = 'Physical & Digital'
                else:
                    format_type = 'Physical'
            elif 'Digital' in format_text:
                    format_type = 'Digital'
            else:
                format_type = 'Other'

            release = {'date': release_date, 'title': title, 'volume': volume, 'publisher': 'Viz Media', 'store_link': link, 'format': format_type}
            result.append(release)
        
        m = m+1 if m<12 else 1
        y = y+1 if m==1 else y
        soup = BeautifulSoup(requests.get(url + f'{y}/{m}').text, 'html.parser')

    if verbose > 0:
        print(f'{len(result)} releases found for Viz Media, completed in {perf_counter()-start_time} seconds.')
    return result