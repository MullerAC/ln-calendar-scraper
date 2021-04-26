from bs4 import BeautifulSoup
from datetime import date, datetime
from dateutil.parser import parse
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

def dark_horse_volume(url, date = date.today()):
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
    
    result = []
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
    Square Enix calendar does not load well,
    Selenium will need to be used.
    Also has no light novel releases currently,
    and so can't be tested right now.
    To be completed later.
    Returns empty list:
    []
    '''
    
    result = []
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
                    format_type = 'Physical & Digital'
            else:
                format_type = 'Other'

            release = {'date': release_date, 'title': title, 'volume': volume, 'publisher': 'Viz Media', 'store_link': link, 'format': format_type}
            result.append(release)
        
        m = m+1 if m<12 else 1
        y = y+1 if m==1 else y
        soup = BeautifulSoup(requests.get(url + f'{y}/{m}').text, 'html.parser')

    return result