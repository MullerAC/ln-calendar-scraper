from bs4 import BeautifulSoup
from datetime import date, datetime
import requests
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
        release_date = datetime.strptime(date_tag.get_text(strip=True).replace('.', ' '), '%b %d release').date()
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
    
    for volume in soup.find_all('div', class_='list_item'):
        href = volume.find('a')['href']
        result.append(dark_horse_volume(urljoin(url, href), date))
    
    return result

def dark_horse_volume(url, date = date.today()):
    
    result = []
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    title_text = soup.find('h2', class_='title').get_text(strip=True)
    if 'Volume' in title_text:
        title_text_split = title_text.split(' Volume ')
        volume_text = title_text_split[1].split(':')
        title = title_text[0] + ':' + volume_text[1]
        volume = volume_text[0]
    else:
        title = title_text
        volume = '1'
    
    details = soup.find('div', class_='product-meta').find_all('dd')
    release_date = details[0].get_text(strip=True)
    format_type = details[1].get_text(strip=True)
    
    return {'date': release_date,
            'title': title,
            'volume': volume,
            'publisher': 'Dark Horse',
            'store_link': url,
            'format': format_type}

    """
    result = []
    driver.get(f'https://www.darkhorse.com/Search/Browse/"vampire+hunter+d"---Books---{today.strftime("%B+%Y")}-December+9999/Ppydwkt8')#open driver to search url, includes filtering by release date
    try:
        driver.find_element_by_xpath('//*[@id="display_images"]/input[2]').click()#turns "Display Images" off, which shows release dates
    except NoSuchElementException:#"Display Images" button does not appear if the search result is empty
        print(f'Failed to read data or no releases found for Dark Horse, completed at {perf_counter()-start_time}')
        return result
    sleep(sleep_time)
    soup = BeautifulSoup(driver.execute_script('return document.body.innerHTML'), 'html.parser')
    for item in soup.find('table', class_='product_text_items').find_all('tr')[1:]:#iterate through every item on search page, skipping first row of headers
        item_data = item.find_all('td')
        date = datetime.strptime(item_data[1].get_text(strip=True), '%b %d, %Y').date()
        if date < today: continue#skips item if it is before target date
        title_volume_link = item_data[0].find('a')
        title_volume = title_volume_link.get_text(strip=True).replace(' TPB', '').replace(' HC', '').split(' Volume ')
        title = title_volume[0]
        if len(title_volume) > 1:
            volume_subtitle = title_volume[1].split(':')
            volume = volume_subtitle[0]
            if len(volume_subtitle) > 1: title += f':{volume_subtitle[1]}'
        else: volume = '1'
        link = f'https://www.darkhorse.com{title_volume_link["href"]}'
        release = {'date': date, 'title': title, 'lndb_link': '', 'volume': volume, 'publisher': 'Dark Horse', 'store_link': link, 'format': 'Physical & Digital'}
        result.append(release)
    print(f'{len(result)} releases found for Dark Horse, completed at {perf_counter()-start_time}')
    return result
    """