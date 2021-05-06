"""
TO DO:
- amazon scraping calendar
- amazon scraping series (find all volumes then volume scrape)
- amazon scraping volumes
- OPB series scraping (find all volumes then volume scrape)
- OPB volume scraping
- find OPB link from amazon title
"""

from bs4 import BeautifulSoup
from datetime import date
#from dateutil.parser import parse
import requests
from time import perf_counter
#from urllib.parse import urljoin

def scrape(start_date=date.min, verbose=0):
    '''
    One Peace has no calendar on their website.
    Physical and digital releases only available on Amazon.
    To be completed later.
    Returns empty list:
    []
    '''
    
    start_time = perf_counter()
    if verbose > 1:
        print('Starting scraping for One Peace Books.')
    result = []

    if verbose > 0:
        print(f'{len(result)} releases found for One Peace Books, completed in {perf_counter()-start_time} seconds.')
    return result

def series(url, start_date=date.min):
    '''
    Takes in a series url
    (ex: https://www.onepeacebooks.com/jt/ShieldHeroLNV.html.
    To be completed later.
    Returns empty list:
    []
    '''

    result = []
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    return result

def volume(url, volume='1'):
    '''
    One Peace Books has no volume pages or links.
    Takes in url for series and volume number as string.
    Finda volume on series page and gets needed data.
    To be completed later.
    Returns empty dictionary:
    {}
    '''

    result = {}
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    return result