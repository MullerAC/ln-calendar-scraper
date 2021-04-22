from bs4 import BeautifulSoup
from datetime import date, datetime
import requests
from urllib.parse import urljoin

def book_walker(date):
    
    result = []
    url = 'https://global.bookwalker.jp/'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    for series in soup.find('p', text='Exclusive Light Novels').parent.find_all('a'):
        result.extend(book_walker_series(urljoin(url, series['href']), date))
    
    return result
    
def book_walker_series(url, date):
    
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
        title_text = title_tag.get_text(strip=True).split(' Volume ')
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