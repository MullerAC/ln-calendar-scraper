from bs4 import BeautifulSoup
from datetime import date, datetime
from dateutil.parser import parse
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import perf_counter, sleep
from urllib.parse import urljoin

def book_walker(date = date.today()):
    """
    Finds all series listed under "Exclusive Light Novels" to get all sreies published by Book Walker.
    Runs all links through book_walker_series() and combines all results and returns them.
    Returns a list of dictionaries:
    [{'date', 'title', 'volume', 'publisher':'Book Walker', 'store_link', 'format':'Digital'}]
    """
    
    result = []
    url = 'https://global.bookwalker.jp/'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    for series in soup.find('p', text='Exclusive Light Novels').parent.find_all('a'):
        result.extend(book_walker_series(urljoin(url, series['href']), date))
    
    return result
    
def book_walker_series(url, date = date.today()):
    """
    Takes a valid Book Walker series link (ex: https://global.bookwalker.jp/series/135449/the-ryuos-work-is-never-done/)
    and date in the future.
    Sorts volumes by date and save information until it comes across a date before the given date.
    Returns a list of dictionaries:
    [{'date', 'title', 'volume', 'publisher':'Book Walker', 'store_link', 'format':'Digital'}]
    """
    
    result = []
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    for item in soup.find_all('li', class_='o-tile'):
        
        date_tag = item.find('div', class_='a-tile-release-date')
        if date_tag is None:
            break
        release_date = parse(date_tag.get_text(strip=True).replace('.', ' ')).date()
        release_date = release_date.replace(year=date.year+(release_date.month<date.month))
        if release_date < date:
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
                   'store_link': link,
                   'format': 'Digital'}
        result.append(release)
    
    return result

def cross_infinite_world(date = date.today()): # todo
    '''
    Cross Infinite World has no calendar on their website.
    Physical and digital releases only available on Amazon.
    To be completed later.
    Returns empty list:
    []
    '''
    
    result = []
    return result

def dark_horse(date = date.today()):
    """
    Dark Horse has no calendar or way to search for only light novels (the also release many other types of books).
    Runs a search for Vampire Hunter D (Dark Horse's only active license) and searches that page for upcoming releases.
    Returns a list of dictionaries:
    [{'date', 'title', 'volume', 'publisher':'Book Walker', 'store_link', 'format':'Digital'}]
    """
    
    result = []
    url = f'https://www.darkhorse.com/Search/Browse/"vampire+hunter+d"---Books---{date.strftime("%B+%Y")}-December+2099/Ppydwkt8'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    for item in soup.find_all('div', class_='list_item'):
        href = item.find('a')['href']
        result.append(dark_horse_volume(urljoin(url, href), date))
    
    return result

def dark_horse_volume(url, date = date.today()): # need to double check on format
    """
    Dark Horse calendar does not have all information on it,
    need to check individual volume pages to get release date.
    Returns a dictionaries:
    {'date', 'title', 'volume', 'publisher':'Dark Horse', 'store_link', 'format':'Physical & Digital'}
    """
    
    result = []
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    title_text = soup.find('h2', class_='title').get_text(strip=True).split(':')[0]
    if ' Volume ' in title_text:
        title_text_split = title_text.split(' Volume ')
        title = title_text_split[0]
        volume = title_text_split[1].split(':')[0]
    else:
        title = title_text
        volume = '1'
    
    details = soup.find('div', class_='product-meta').find_all('dd')
    release_date = parse(details[0].get_text(strip=True)).date()
    # format_type = details[1].get_text(strip=True)
    
    return {'date': release_date,
            'title': title,
            'volume': volume,
            'publisher': 'Dark Horse',
            'store_link': url,
            'format': 'Physical & Digital'}

def j_novel_club(date = date.today()): # todo
    '''
    J-Novel Club's website is currently in flux;
    the calendar page often fails to load correctly.
    It also does not currently have physical releases listed, only digital.
    To be completed later.
    Returns empty list:
    []
    '''

    # This section is temporary, as the calendar doesn't load correctly by entering the url
    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument('headless')
    driver_options.add_argument('log-level=2')
    driver = webdriver.Chrome(options=driver_options)
    url = 'https://j-novel.club/'
    driver.get(url) # open driver to calendar url
    sleep(0.5)
    driver.find_element_by_xpath('/html/body/div/div/div[1]/div[1]/div[2]/a[3]').click() # go to calendar, using url messes up html
    sleep(0.5)
    driver.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div[3]/div/div[5]/div[2]').click() # show only full digital ebook releases
    sleep(0.5)
    driver.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div[3]/div/div[7]/div[2]').click() # show only novels
    sleep(0.5)
    driver.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div[4]/div/div[1]/div[2]').click()
    sleep(0.5)
    soup = BeautifulSoup(driver.execute_script('return document.body.innerHTML'), 'html.parser')

    result = []
    """
    month = date.month
    year = date.year
    url = f'https://j-novel.club/calendar?year={year}&month={month}&type=novel&rel=digital'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    """
 
    calendar = soup.find('div', class_='f1owoso1')
    while 'Nothing to see here!' not in calendar.find('h2').get_text():
        release_date = datetime.strptime(calendar.find('span', class_='f182sjpl').get_text(strip=True), '%B%Y').date()
        for item in calendar.find_all('div', recursive=False):
            if item.has_attr('class') and 'ffukg03' in item['class']:#item is a date
                release_date = release_date.replace(day=int(item.find('h2').find(text=True, recursive=False).strip()[:-2]))
            elif item.has_attr('class') and 'fhkbwa' in item['class']:#item is a release
                if release_date < date:
                    continue#skips item if it is before target date
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
                    
                    release = {'date': release_date, 'title': title, 'lndb_link': 'N/A', 'volume': volume, 'publisher': 'J-Novel Club', 'store_link': link, 'format': 'Digital'}
                    result.append(release)
            else:#item is a header, footer, empty date, or something else
                continue
        """year = year + 1 if month == 12 else year
        month = 1 if month == 12 else month + 1
        driver.get(f'https://j-novel.club/calendar?year={year}&month={month}&type=novel&rel=digital')#open driver to calendar url"""
        driver.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div[4]/div/div[1]/div[2]').click()
        sleep(0.5)
        soup = BeautifulSoup(driver.execute_script('return document.body.innerHTML'), 'html.parser')
        calendar = soup.find('div', class_='f1owoso1')
    #print(f'{len(result)} releases found for J-Novel Club (beta/digital), completed at {perf_counter()-start_time}')
    return result

def one_peace(date = date.today()): # todo
    '''
    One Peace has no calendar on their website.
    Physical and digital releases only available on Amazon.
    To be completed later.
    Returns empty list:
    []
    '''
    
    result = []
    return result

def seven_seas(date = date.today()):
    '''
    Seven Seas has two calendars:
    one for physical, and one for digital.
    Both are in the same format, but need to be scraped seperately.
    Returns a list of dictionaries:
    [{'date', 'title', 'volume', 'publisher':'Seven Seas', 'store_link', 'format'}]
    '''
    
    result = []
    urls = [('https://sevenseasentertainment.com/digital/', 'Digital'), ('https://sevenseasentertainment.com/release-dates/', 'Physical')]
    
    for url, format_type in urls:
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        
        for item in soup.find_all('tr', id='volumes'):
            cells = item.find_all('td')
            
            date_tag = cells[0]
            #release_date = datetime.strptime(date_tag.get_text(strip=True), '%Y/%m/%d').date()
            release_date = parse(date_tag.get_text(strip=True)).date()
            if release_date < date:
                continue
                
            title_tag = cells[1].find('a')
            title_split = title_tag.get_text(strip=True).replace(' (Light Novel)', '').replace(' (Novel)', '').split(' Vol. ')
            title = title_split[0]
            volume = title_split[-1] if len(title_split)>1 else '1 [End]'
            link = urljoin(url, title_tag['href'])
                
            format_tag = cells[2]
            if 'Novel' not in format_tag.get_text():
                continue
            
            release = {'date': release_date,
                       'title': title,
                       'volume': volume,
                       'publisher': 'Seven Seas',
                       'store_link': link,
                       'format': format_type}
            result.append(release)
    
    return result

def sol_press(date = date.today()):
    '''
    Sol Press only lists digital releases on their calendar.
    May need to revisit if they add physicals.
    No releases are currently scheduled, will need to test later.
    Returns a list of dictionaries:
    [{'date', 'title', 'volume', 'publisher':'Sol Press', 'store_link', 'format':'Digital'}]
    '''

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
        if release_date < date:
            break

        release = {'date': release_date, 'title': title, 'volume': volume, 'publisher': 'Sol Press', 'store_link': link, 'format': 'Digital'}
        result.append(release)

    return result

def square_enix(date = date.today()): # todo
    '''
    Square Enix calendar does not have items in base html,
    Selenium will need to be used.
    Also has no light novel releases currently,
    and so can't be tested right now.
    To be completed later.
    Returns empty list:
    []
    '''
    
    result = []
    url = 'https://squareenixmangaandbooks.square-enix-games.com/en-us/release-calendar'
    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument('headless')
    driver_options.add_argument('log-level=2')
    driver = webdriver.Chrome(options=driver_options)
    driver.get(url)
    next_month = date

    while True:

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
            if release_date < date:
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
    
    return result

def tentai(date = date.today()): # todo
    '''
    Tentai calendar is very oddly arranged,
    and contains much unuseful information.
    To be completed later.
    Returns empty list:
    []
    '''
    
    result = []
    return result

def vertical(date = date.today()): # todo
    '''
    Vertical may be renames Kodansha Books.
    The new website has a calendar,
    but no way to differenciate between light novels and other books.
    Might also be scraped from Random Penguin House.
    To be completed later.
    Returns empty list:
    []
    '''
    
    result = []
    return result

def viz_media(date = date.today()):
    '''
    Viz calendar has a different page for each month,
    easily accessed by by putting the year and month into the url.
    Returns a list of dictionaries:
    [{'date', 'title', 'volume', 'publisher':'Sol Press', 'store_link', 'format':'Digital'}]
    '''

    result = []
    url = 'https://www.viz.com/calendar/'
    m, y = date.month, date.year
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
            if release_date < date:
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

    return result

def yen_press(date = date.today()):
    '''
    Yen On calendar has only light novels and a section for each month,
    but releases are not ordered by date within each month.
    Returns a list of dictionaries:
    [{'date', 'title', 'volume', 'publisher':'Yen Press', 'store_link', 'format'}]
    '''

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
            if release_date < date:
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
    
    return result