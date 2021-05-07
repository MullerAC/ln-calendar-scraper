"""
To Do:
- complete volume scraping
- have full calendar scrape method call calendar scraping inside itself
- test with old dates
"""

from bs4 import BeautifulSoup
from datetime import date
from dateutil.parser import parse
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import perf_counter, sleep
from urllib.parse import urljoin
from utils import get_format

def scrape(start_date = date.today()): # todo: testing with old dates, optimize sleep values
    '''
    Square Enix calendar does not have items in base html,
    Selenium will need to be used.
    Also has no light novel releases currently,
    and so can't be tested right now.
    To be completed later.
    Returns empty list:
    []
    '''
    
    start_time = perf_counter()
    if verbose > 1:
        print('Starting scraping for Square Enix.')
    result = []
    url = 'https://squareenixmangaandbooks.square-enix-games.com/en-us/release-calendar'
    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument('headless')
    driver_options.add_argument('log-level=2')
    driver = webdriver.Chrome(options=driver_options)
    driver.get(url)
    next_month = start_date

    while True:
        if verbose > 2:
            print(f'Scraping calendar for {next_month.strptime('%B %Y')}.')
        try:
            driver.find_element_by_xpath(f"//*[contains(text(), '{next_month.strftime('%B %Y')}')]").click()
        except NoSuchElementException:
            break
        # sleep(1.0)
        soup = BeautifulSoup(driver.execute_script('return document.body.innerHTML'), 'html.parser')

        links = []
        for item in soup.find_all('a', style='text-decoration: none;'):
            links.append(urljoin(url, item["href"]))

        for link in links:

            driver.get(link)
            # sleep(1.0)
            soup = BeautifulSoup(driver.execute_script('return document.body.innerHTML'), 'html.parser')

            title_split = soup.find('div', class_='book-title').get_text(strip=True).split(', Volume ')
            title = title_split[0]
            volume = title_split[1] if len(title_split)>1 else '1'

            synopsis = soup.find('div', class_='synopsis')
            if synopsis is None:
                continue
            details = synopsis.find_all('div', recursive=False)
            if 'Novel' not in synopsis.get_text():# and 'Novel' not in synopsis[4].get_text():
                continue

            release_date = parse(synopsis[2].get_text(strip=True).replace('release date:', '')).date()
            if release_date < start_date:
                continue

            format_text = soup.find('div', class_='format-options').get_text()
            format_type = get_format(format_text)

            release = {'date': release_date,
                       'title': title,
                       'volume': volume,
                       'publisher': 'Square Enix',
                       'store_link': link,
                       'format': format_type}
            result.append(release)
        
        m = next_month.month+1 if next_month.month<12 else 1
        y = next_month.year+1 if next_month.month==1 else next_month.year
        next_month = next_month.replace(y, m)
    
    if verbose > 0:
        print(f'{len(result)} releases found for Square Enix, completed in {perf_counter()-start_time} seconds.')
    return result

def series(url=None, start_date=date.min):
    '''
    Square Enix has no series web pages.
    Returns an empty list:
    []
    '''

    result = []
    
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

    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument('headless')
    driver_options.add_argument('log-level=2')
    driver = webdriver.Chrome(options=driver_options)
    driver.get(url)
    soup = BeautifulSoup(driver.execute_script('return document.body.innerHTML'), 'html.parser')

    title_split = soup.find('h1', {'class':'title'}).get_text(strip=True).split(' Vol. ')
    title = title_split[0]
    volume = title_split[-1] if len(volume_split)>1 else '1'
    release_date = parse(item.find('section', {'class':'details'}).find('div', {'class':'infobox'}).find('strong').get_text(strip=True)).date()
    format_text = soup.find('div', class_='format-options').get_text()
    format_type = get_format(format_text)

    
    result = {'date': release_date,
              'title': title,
              'volume': volume,
              'publisher': 'Square Enix',
              'store_link': url,
              'format': format_type}
    return result