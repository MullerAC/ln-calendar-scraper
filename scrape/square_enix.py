from bs4 import BeautifulSoup
from datetime import date
from dateutil.parser import parse
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import perf_counter, sleep
from urllib.parse import urljoin

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
            if ('Paperback' in format_text) or ('Hardcover' in format_text):
                if 'Digital' in format_text:
                    format_type = 'Physical & Digital'
                else:
                    format_type = 'Physical'
            elif 'Digital' in format_text:
                    format_type = 'Digital'
            else:
                format_type = 'Other'

            release = {'date': release_date, 'title': title, 'volume': volume, 'publisher': 'Square Enix', 'store_link': link, 'format': format_type}
            result.append(release)
        
        m = next_month.month+1 if next_month.month<12 else 1
        y = next_month.year+1 if next_month.month==1 else next_month.year
        next_month = next_month.replace(y, m)
    
    if verbose > 0:
        print(f'{len(result)} releases found for Square Enix, completed in {perf_counter()-start_time} seconds.')
    return result