"""
To Do:
- scrape physicals from Right Stuf Anime
- remove selenium use once site works properly again
"""

from bs4 import BeautifulSoup
from datetime import date
from dateutil.parser import parse
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import perf_counter, sleep
from urllib.parse import urljoin

def scrape(start_date=date.min, verbose=0):
    '''
    J-Novel Club's website is currently in flux;
    the calendar page often fails to load correctly.
    Uses Selenium to load page correctly through homepage.
    This will be removed when the site works correctly again.
    It also does not currently have physical releases listed, only digital.
    Returns a list of dictionaries:
    [{'date':datetime.date, 'title':string, 'volume':string, 'publisher':'J-Novel Club', 'publisher_link':string, 'format':'Digital'}]
    '''

    start_time = perf_counter()
    if verbose > 1:
        print('Starting scraping for J-Novel Club.')
    result = []
    """
    month = start_date.month
    year = start_date.year
    url = f'https://j-novel.club/calendar?year={year}&month={month}&type=novel&rel=digital'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    """

    # This section is temporary, as the calendar doesn't load correctly by entering the url
    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument('headless')
    driver_options.add_argument('log-level=2')
    driver = webdriver.Chrome(options=driver_options)
    url = 'https://j-novel.club/'
    driver.get(url)
    sleep(0.5)
    driver.find_element_by_xpath('/html/body/div/div/div[1]/div[1]/div[2]/a[3]').click()
    sleep(0.5)
    driver.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div[3]/div/div[5]/div[2]').click()
    sleep(0.5)
    driver.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div[3]/div/div[7]/div[2]').click()
    sleep(0.5)
    driver.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div[4]/div/div[1]/div[2]').click()
    sleep(0.5)
    soup = BeautifulSoup(driver.execute_script('return document.body.innerHTML'), 'html.parser')
 
    calendar = soup.find('div', class_='f1owoso1')
    while 'Nothing to see here!' not in calendar.find('h2').get_text():

        release_date = parse(calendar.find('span', class_='f182sjpl').get_text(strip=True)).date()
        if verbose > 2:
            print(f'Scraping calendar for {release_date.strptime('%B %Y')}.')

        for item in calendar.find_all('div', recursive=False):
            if item.has_attr('class') and 'ffukg03' in item['class']:
                release_date = release_date.replace(day=int(item.find('h2').find(text=True, recursive=False).strip()[:-2]))
            elif item.has_attr('class') and 'fhkbwa' in item['class']:
                if release_date < start_date:
                    continue
                for item_release in item.find_all('a', class_='link f122npxj block'):
                    link = urljoin(url, item_release['href'])
                    volume_tag = item_release.find('span', class_='fpcytuh')
                    if volume_tag is None:
                        volume = 'tbd'
                    else:
                        volume = volume_tag.get_text().split()[-1]
                    soup = BeautifulSoup(requests.get(link).text, 'html.parser')
                    title_tag = soup.find('div', class_='fl45o3o')
                    title = title_tag.get_text(strip=True)
                    link = 'https://j-novel.club/series/' + title_tag['id'] + link[link.rfind('#'):]
                    
                    release = {'date': release_date,
                               'title': title,
                               'volume': volume,
                               'publisher': 'J-Novel Club',
                               'store_link': link,
                               'format': 'Digital'}
                    result.append(release)
            else:
                continue

        """
        year = year + 1 if month == 12 else year
        month = 1 if month == 12 else month + 1
        url = f'https://j-novel.club/calendar?year={year}&month={month}&type=novel&rel=digital'
        soup = BeautifulSoup(BeautifulSoup(requests.get(url).text, 'html.parser')
        """
        driver.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div[4]/div/div[1]/div[2]').click()
        sleep(0.5)
        soup = BeautifulSoup(driver.execute_script('return document.body.innerHTML'), 'html.parser')
        calendar = soup.find('div', class_='f1owoso1')
    
    if verbose > 0:
        print(f'{len(result)} release(s) found for J-Novel Club, completed in {perf_counter()-start_time} seconds.')
    return result

def series(url, start_date=date.min):
    '''
    Takes in a valid J-Novel Club series link
    (ex: https://j-novel.club/series/mapping-the-trash-tier-skill-that-got-me-into-a-top-tier-party)
    and datetime.date object.
    Scrapes from the bottom up,
    stopping when coming across a volume with a date before start_date.
    J-Novel Club has only digital releases on the site for now.
    Returns a list of dictionaries:
    [{'date':datetime.date, 'title':string, 'volume':string, 'publisher':'J-Novel Club', 'publisher_link':string, 'format':'Digital'}]
    '''

    result = []
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    title = soup.find('div', {'class':'ffukg03 header large fl45o3o'}).get_text(strip=True)

    items = soup.find('div', {'class':'f1k2es0r'}).find_all('div', {'class':'f1k2es0r'})
    items.reverse()

    for item in items:
        volume_tag = item.find('a')
        volume = volume_tag.get_text(strip=True)
        link = url + volume_tag['href']
        release_date = parse(soup.find('div', {'class':'f1i3amjc'}).find('div', {'class':'f1oyfch5 text'}).get_text(strip=True)).date()

        if release_date < start_date:
            break

        release = {'date': release_date,
                   'title': title,
                   'volume': volume,
                   'publisher': 'J-Novel Club',
                   'store_link': link,
                   'format': 'Digital'}
        result.append(release)

    return result

def volume(url):
    '''
    Takes in a valid J-Novel Club volume link
    (ex: https://j-novel.club/series/mapping-the-trash-tier-skill-that-got-me-into-a-top-tier-party#volume-2)
    and scrapes all relevant data from there.
    J-Novel Club has only digital releases on the site for now.
    Returns a list of dictionaries:
    [{'date':datetime.date, 'title':string, 'volume':string, 'publisher':'J-Novel Club', 'publisher_link':string, 'format':'Digital'}]
    '''

    result = []
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    title = soup.find('div', {'class':'ffukg03 header large fl45o3o'}).get_text(strip=True)

    volume_href = '#' + url.split('#')[-1]
    volume_div = soup.find('a', {'href':volume_href}).parent.parent.parent.parent.parent

    volume_tag = volume_div.find('a')
    volume = volume_tag.get_text(strip=True)
    link = url + volume_tag['href']
    release_date = parse(volume_div.find('div', {'class':'f1i3amjc'}).find('div', {'class':'f1oyfch5 text'}).get_text(strip=True)).date()

    release = {'date': release_date,
               'title': title,
               'volume': volume,
               'publisher': 'J-Novel Club',
               'store_link': url,
               'format': 'Digital'}
    return result