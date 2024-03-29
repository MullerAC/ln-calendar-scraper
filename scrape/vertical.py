#from bs4 import BeautifulSoup
from datetime import date
#from dateutil.parser import parse
#import requests
from time import perf_counter
#from urllib.parse import urljoin

def scrape(start_date = date.today(), verbose=0): # todo
    '''
    Vertical may be renamed Kodansha Books.
    The new website has a calendar,
    but no way to differenciate between light novels and other books.
    Might also be scraped from Random Penguin House.
    to try: https://kodansha.us/books/browse/?sort=newest&filter_category%5B0%5D=fiction_literature
    To be completed later.
    Returns empty list:
    []
    '''
    start_time = perf_counter()
    if verbose > 1:
        print('Starting scraping for Vertical.')
    result = []

    if verbose > 0:
        print(f'{len(result)} releases found for Vertical, completed in {perf_counter()-start_time} seconds.')
    return result