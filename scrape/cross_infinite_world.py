"""
TO DO:
- 
"""

from bs4 import BeautifulSoup
from datetime import date
#from dateutil.parser import parse
import requests
from time import perf_counter
#from urllib.parse import urljoin

def scrape(start_date=date.min, verbose=0): # todo
    '''
    Cross Infinite World has no calendar on their website.
    Physical and digital releases only available on Amazon.
    To be completed later.
    Returns empty list:
    []
    '''
    
    start_time = perf_counter()
    if verbose > 1:
        print('Starting scraping for Cross Infinite World.')
    result = []

    if verbose > 0:
        print(f'{len(result)} release(s) found for Cross Infinite World, completed in {perf_counter()-start_time} seconds.')
    return result

def series(url, start_date=date.min):
    '''
    Takes in a series url
    (ex: http://www.crossinfworld.com/Reincarnated-as-the-Last-of-My-Kind.html).
    To be completed later.
    Returns empty list:
    []
    '''

    result = []

    return result

def volume(url):
    '''
    Takes in a volume url
    (ex: http://www.crossinfworld.com/Reincarnated-as-the-Last-of-My-Kind.html).
    To be completed later.
    Returns empty dictionary:
    {}
    '''

    result = {}
    return result
