#from bs4 import BeautifulSoup
from datetime import date
#from dateutil.parser import parse
#import requests
from time import perf_counter
#from urllib.parse import urljoin

def scrape(start_date = date.today(), verbose=0): # todo
    '''
    Tentai calendar is very oddly arranged,
    and contains much unuseful information.
    To be completed later.
    Returns empty list:
    []
    '''
    start_time = perf_counter()
    if verbose > 1:
        print('Starting scraping for Tentai Books.')
    result = []

    if verbose > 0:
        print(f'{len(result)} releases found for Tentai Books, completed in {perf_counter()-start_time} seconds.')
    return result