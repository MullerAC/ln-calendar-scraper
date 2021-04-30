'''
original form this project took
when I first self-taught web scraping
needs to be seriously reworked
hence this repo
'''

from bs4 import BeautifulSoup
from datetime import date, datetime
from operator import itemgetter
from praw import Reddit
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from string import punctuation
from time import perf_counter, sleep
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from nt import link

'''
don't post on main subreddit
don't unsticky post
don't overwrite main wikipage
'''

start_time = perf_counter()
driver_options = webdriver.ChromeOptions()
driver_options.add_argument('headless')
driver_options.add_argument('log-level=2')
driver = webdriver.Chrome(options=driver_options)
driver_secondary = webdriver.Chrome(options=driver_options)
today = date.today()
today = date(today.year + today.month//12, today.month+1 if today.month<12 else 1, 1)#sets target date to beginning of next month
'''
originally declared reddit and subreddit variables here
but it was full of secret credentials
will need to be reworked if adding back Reddit posting part
'''
sleep_time = 1.0#made-up experimental universal sleep constant for slow sites

"""
def main():
    upcoming_releases = []#{date, title, lndb_link, volume, publisher, store_link, format}, all are strings
    print(f'Target date: {today}\nScraping starting at {str(perf_counter()-start_time)}')
    upcoming_releases.extend(book_walker())
    upcoming_releases.extend(cross_infinite_world_digital())
    upcoming_releases.extend(cross_infinite_world_physical())
    upcoming_releases.extend(dark_horse())
    upcoming_releases.extend(j_novel_club_beta())
    #upcoming_releases.extend(j_novel_club_digital())
    upcoming_releases.extend(j_novel_club_physical())
    upcoming_releases.extend(one_peace_digital())
    upcoming_releases.extend(one_peace_physical())
    upcoming_releases.extend(seven_seas())
    upcoming_releases.extend(sol_press_digital())
    upcoming_releases.extend(sol_press_physical())
    upcoming_releases.extend(square_enix())
    upcoming_releases.extend(tentai_digital())
    upcoming_releases.extend(tentai_physical())
    upcoming_releases.extend(vertical_digital())
    upcoming_releases.extend(vertical_physical())
    upcoming_releases.extend(viz_media())
    upcoming_releases.extend(yen_press())
    driver.close()
    driver_secondary.close()
    upcoming_releases = upcoming_releases
    print(f'MAL lookups started at {str(perf_counter()-start_time)}')
    mal_links = {}
    with open('MAL Archive.txt', 'r') as f:
        for line in f:
            link_data = line.strip().split('|')
            mal_links[link_data[0]] = link_data[1]
    for release in upcoming_releases:
        release['lndb_link'] = mal_links.get(release['title'].replace('\u2019', "'").translate(str.maketrans("", "", punctuation)).casefold(), 'N/A').strip()
    print(f'MAL lookups completed at {str(perf_counter()-start_time)}')
    create_content(upcoming_releases)

def mal_link(title):
    link = 'N/A'
    try:
        with urlopen(f'https://myanimelist.net/manga.php?q={title.replace(" ", "+")}&type=2') as site:#open lndb search page, get html, and close
            soup = BeautifulSoup(site, 'html.parser')
    except HTTPError:
        print(f'HTTP Error searching for MAL link for {title}')
        return link
    try:
        title_link = soup.find('div', class_='js-categories-seasonal js-block-list list').find_all('tr')[1].find('a', class_='hoverinfo_trigger fw-b')
    except:
        return link
    if title.translate(str.maketrans("", "", punctuation)).casefold() in title_link.get_text(strip=True).replace('\u2019', "'").translate(str.maketrans("", "", punctuation)).casefold():
        link = title_link['href']
    else:
        try:
            with urlopen(title_link['href']) as site_secondary:#open lndb search page, get html, and close
                soup_secondary = BeautifulSoup(site_secondary, 'html.parser')
                title_english = soup_secondary.find('div', id="content").find('div').find('div', class_='spaceit_pad')
            if title.translate(str.maketrans("", "", punctuation)).casefold() in title_english.get_text(strip=True).replace('\u2019', "'").translate(str.maketrans("", "", punctuation)).casefold():
                link = title_link['href']
        except:
            return link
    if link == 'N/A':
        for c in punctuation:
            if c in title:
                return mal_link(title.translate(str.maketrans("", "", punctuation)))#attempt search with title without punctuation
    if link.rfind('/') > 30:
        return link[:link.rfind('/')]
    else:
        return link

def create_content(releases_all):#turns release dicts into Reddit-readable tables and calls functions to update and archive the wiki, create the monthly post, and update the sidebar
    if not releases_all: return print('No releases found')#skip everything if no releases are found
    wiki_content, post_content, sidebar_content = '', '', ''
    MONTH_NAMES = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
    stats = {'Book Walker':0, 'Cross Infinite World':0, 'Dark Horse':0, 'J-Novel Club':0, 'One Peace':0, 'Seven Seas':0, 'Sol Press':0, 'Square Enix':0, 'Vertical':0, 'Viz Media':0, 'Yen Press':0}
    for i in range (0, 11):#finds upcoming releases for the next 12 months
        m = today.month+i if today.month+i<=12 else today.month+i-12
        y = today.year if today.month+i<=12 else today.year+1
        releases_month = []
        j = 0
        while j < len(releases_all):#adds releases for target month to new list while removing them from old
            if releases_all[j]['date'].month == m: releases_month.append(releases_all.pop(j))
            else: j += 1
        if len(releases_month) > 0:#skip months with no target releases
            releases_month.sort(key=itemgetter('date', 'title', 'format'))
            k = 1
            while k < len(releases_month):#checking for duplicate subsequent entries
                if releases_month[k]['title'] == releases_month[k-1]['title'] and releases_month[k]['date'] == releases_month[k-1]['date']:
                    if releases_month[k]['format'] != releases_month[k-1]['format']: releases_month[k]['format'] += f' & {releases_month[k-1]["format"]}'
                    releases_month.pop(k-1)
                else: k += 1
            table_month = f'###{MONTH_NAMES[m]} {str(y)}\n'
            table_month += 'Release Date|Series Name|Volume #|Purchase Page|Release Type|\n:--|:--|:--:|:--|:--|\n'
            for release in releases_month:#create table row for each release
                #if release['lndb_link'] == 'N/A': release['lndb_link'] = lndb_link(release['title'].replace('\u2019', "'"))
                title_link = release['title'] if release['lndb_link'] == 'N/A' or release['lndb_link'] == '' else f'[{release["title"]}]({release["lndb_link"]})'
                publisher_link = release['publisher'] if release['store_link'] == 'N/A' else f'[{release["publisher"]}]({release["store_link"]})'
                table_month += f'{release["date"].strftime("%B %d")}|{title_link}|{release["volume"]}|{publisher_link}|{release["format"]}|\n'
                if i == 0: stats[release['publisher']] = stats.get(release['publisher'], 0) + 1#stats only relate to target month
            wiki_content += table_month
            if i == 0:#post and sidebar only want releases from target month
                post_content += table_month
                sidebar_content += table_month
    post_content += '\n###STATS\n'
    stats_total = sum(stats.values())
    for key, value in stats.items():#turn stats data into text
        if value > 0: post_content += f'* {key} ({str(value)}/{str(stats_total)})\n'
    update_wiki(wiki_content)
    #save_releases(wiki_content)
    #post_creation(post_content)
    #update_sidebar(sidebar_content)

def archive_wiki():#move latest month of data from main wikipage and put at end of archive page, creating archive page if it does not exist
    wiki_name = f'{today.year}releases' if today.month > 1 else f'{today.year-1}releases'
    try:
        post_text = f'{wikipage.content_md}\n\n###{subreddit.wiki["upcomingreleases"].content_md.split("###")[1]}'#finds current wikipage content and appends first section of active wikipage
    except:
        post_text = f'###{subreddit.wiki["upcomingreleases"].content_md.split("###")[1]}'#finds only first section of active wikipage
    subreddit.wiki[wiki_name].edit(content=post_text, reason=today.strftime('Archive for %B %Y Update'))#should automatically create wikipage if it does not already exist

def update_wiki(wiki_content):#archive last month's data, compiles new wiki text, and overwrites wiki with new content
    #archive_wiki()#moves first month's table from upcoming releases wikipage onto separate archive wikipage
    wiki_text = 'UPCOMING RELEASES 2020\n\nThis page updated by bot. Contact /u/SignificantMaybe with any corrections.\n\n'
    wiki_text += 'List of relevant publishers: Book Walker, Cross Infinite World, Dark Horse, J-Novel Club, One Peace, Seven Seas, Sol Press, Square Enix, Vertical, Viz Media, Yen Press.\n\n'
    wiki_text += wiki_content
    subreddit.wiki['upcomingreleases'].edit(content=wiki_text, reason=today.strftime('Update for %B %Y'))
    #subreddit.wiki['releasestest'].edit(content=wiki_text, reason=today.strftime('Update for %B %Y'))
    '''with open('test.txt', 'w') as f:
        f.write(wiki_text)'''

def save_releases(wiki_content):
    with open('tmp_post.txt', 'w') as f:
        f.write(wiki_content)

def post_creation(post_content):#compiles post text, creates post, unstickies old posts by bot, and stickies latest post
    post_text = '###MONTHLY RELEASES\n\nThis post is made by bot. Please comment below with any errors or contact /u/SignificantMaybe. Messages to this account will not be monitored.\n\n'
    post_text += '[See release wiki](https://www.reddit.com/r/LNReleaseBot/wiki/upcomingreleases) for up-to-date information as well as releases further ahead than this month.'
    post_text += " The [manually updated wiki](https://www.reddit.com/r/LightNovels/wiki/upcomingreleases) is still available. I haven't overwritten it yet.\n\n"
    post_text += post_content
    subreddit.submit(title=today.strftime('Upcoming English Light Novel Releases for %B %Y'), selftext=post_text, send_replies=False)
    stickies = subreddit.hot(limit=2)#any stickied post will be in the first two posts when sorting by hot
    for post_old in stickies:#go through possible stickies, unstickying any sticky post made by the bot
        if post_old.stickied and post_old.author.name == 'LNReleaseBot': post_old.mod.sticky(state=False)
    for post_new in reddit.redditor('LNReleaseBot').submissions.new(limit=1): post_new.mod.sticky()#finds the latest post made by the bot and stickies it
    #reddit.subreddit('LightNovels').submit(title=today.strftime('Upcoming English Light Novel Releases for %B %Y'), selftext=post_text, send_replies=False)#submits post to main subreddit

def update_sidebar(sidebar_content):#compiles sidebar text and overwrites sidebar with new text
    sidebar_text = 'Scheduled releases for this month. For further releases see wiki.\n\n'
    sidebar_text += sidebar_content
    for widget in subreddit.widgets.sidebar:#search all sidebar widgets for Upcoming Releases widget
        if widget.kind == 'textarea' and widget.shortName == 'Upcoming Releases': widget.mod.update(text=sidebar_text)
"""

'''
def j_novel_club_physical():#gets upcoming physical releases from Right Stuf Anime
    result = rsa_scrape('/category/Novels/publisher/J~NOVEL-CLUB,J~NOVEL-HEART?order=custitem_rs_release_date:desc&show=96')#read results from Right Stuf Anime
    for release in result:#iterates through all found releases to update title, link, and publisher
        #title, volume, link = jnc_get_title_volume_link([release['title'], release['volume']])#searches JNC site for more accurate title and link
        title, link = jnc_get_title_link(release['title'])
        #release['title'] = title
        release['store_link'] = link#this doesn't seem to work anymore
        #release['store_link'] = f'N/A'
        release['publisher'] = 'J-Novel Club'
    print(f'{len(result)} releases found for J-Novel Club (physical), completed at {perf_counter()-start_time}')
    return result
'''

def rsa_scrape(url):#scrape needed physical release data for any publisher from Right Stuf Anime, given the url
    result = []
    driver.get(f'https://www.rightstufanime.com{url}')
    soup = BeautifulSoup(driver.execute_script('return document.body.innerHTML'), 'html.parser')
    """with urlopen(f'https://www.rightstufanime.com{url}') as site:#open page on Right Stuf Anime, get html, and close
        soup = BeautifulSoup(site, 'html.parser')"""
    for item in soup.find_all('div', class_='facets-items-collection-view-cell-span3'):#iterate through every item on page
        title_volume_link = item.find('a', class_='facets-item-cell-grid-title')
        link = f'https://www.rightstufanime.com{title_volume_link["href"]}'
        if 'Release Date' not in item.get_text():#break loop if item found with no upcoming release date (already released)
            with urlopen(link) as site_secondary:#open item page on Right Stuf Anime, get html, and close
                soup_secondary = BeautifulSoup(site_secondary, 'html.parser')
            try:
                release_date = datetime.strptime(soup_secondary.find('div', class_='custom-item-details-tab-content').find_all('li')[5].get_text(strip=True).split(': ')[1], '%m/%d/%Y').date()
            except:
                break
        else: release_date = datetime.strptime(item.find('p', class_='product-line-stock-msg-pre-order').get_text(strip=True).split('Date: ')[1], '%m/%d/%Y').date()
        if release_date < today: break#break loop if date is earlier than target date
        title_volume = title_volume_link.get_text(strip=True).replace(' Novel', '').replace(' (Hardcover)', '').replace(' Vol ', ' Volume ').replace(' Part ', ' Volume ').split(' Volume ', 1)
        title = title_volume[0]
        volume = title_volume[-1] if len(title_volume)>1 else '1'
        release = {'date': release_date, 'title': title, 'lndb_link': '', 'volume': volume, 'publisher': 'N/A', 'store_link': 'N/A', 'format': 'Physical'}
        result.append(release)
    return result

def jnc_get_title_link(title_search):
    driver_secondary.get('https://j-novel.club/series?search=' + title_search.replace(" ", "+"))
    sleep(sleep_time)#ensure page loads before getting html
    driver_secondary.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div[3]/div/div[2]/div[4]/div[2]').click()
    sleep(sleep_time)#ensure page loads before getting html
    soup_secondary = BeautifulSoup(driver_secondary.execute_script('return document.body.innerHTML'), 'html.parser')
    div_tag = soup_secondary.find('div', class_='ffukg03 header normal fixhvra')
    if div_tag is not None:#corrects title and link if search results are found
        link_tag = div_tag.find('a')
        if link_tag is not None:
            title = link_tag.get_text(strip=True)
            link = f'https://j-novel.club{link_tag["href"]}'#returns the series link instead of the volume link because I am lazy and the site keeps changing anyways
            return title, link
    
    """
    driver_secondary.get('https://j-novel.club/series?search=' + title_search[:len(title_search)//2].strip().replace(" ", "+"))#open secondary driver to search url
    sleep(sleep_time)#ensure page loads before getting html
    soup_secondary = BeautifulSoup(driver_secondary.execute_script('return document.body.innerHTML'), 'html.parser')
    link_tag = soup_secondary.find('div', class_='_11Q4tC _1-4gZSQEDRoFOVWrDrXKju')
    if link_tag is not None:#corrects title and link if search results are found
        title = link_tag.find('div', class_='_1Brt5KBz9dVAP5Gm6bo7m2').get_text(strip=True)
        link = jnc_get_link(f'https://j-novel.club{link_tag.find("a")["href"].split("search?")[0]}', volume)#attempts to get link for individual volume instead of entire series
    else: link = 'N/A'
    """
    
    return title_search, 'N/A'

def jnc_get_title_volume_link(title_volume):
    title = title_volume[0]
    title_search = title.replace("\u2019", "'").split("'")[0].translate(str.maketrans("", "", punctuation))
    volume = title_volume[-1] if len(title_volume)>1 else '1'
    driver_secondary.get('https://j-novel.club/search?curFilter=%7B"order"%3A"title+ASC"%2C"keyword"%3A"' + title_search.replace(" ", "+") + '"%2C"type"%3A"Novel"%7D&curModel=series')#open secondary driver to search url
    sleep(sleep_time)#ensure page loads before getting html
    soup_secondary = BeautifulSoup(driver_secondary.execute_script('return document.body.innerHTML'), 'html.parser')
    link_tag = soup_secondary.find('div', class_='_11Q4tC _1-4gZSQEDRoFOVWrDrXKju')
    if link_tag is not None:#corrects title and link if search results are found
        title = link_tag.find('div', class_='_1Brt5KBz9dVAP5Gm6bo7m2').get_text(strip=True)
        link = jnc_get_link(f'https://j-novel.club{link_tag.find("a")["href"].split("search?")[0]}', volume)#attempts to get link for individual volume instead of entire series
    else:
        driver_secondary.get('https://j-novel.club/search?curFilter=%7B"order"%3A"title+ASC"%2C"keyword"%3A"' + title_search[:len(title_search)//2].strip().replace(" ", "+") + '"%2C"type"%3A"Novel"%7D&curModel=series')#open secondary driver to search url
        sleep(sleep_time)#ensure page loads before getting html
        soup_secondary = BeautifulSoup(driver_secondary.execute_script('return document.body.innerHTML'), 'html.parser')
        link_tag = soup_secondary.find('div', class_='_11Q4tC _1-4gZSQEDRoFOVWrDrXKju')
        if link_tag is not None:#corrects title and link if search results are found
            title = link_tag.find('div', class_='_1Brt5KBz9dVAP5Gm6bo7m2').get_text(strip=True)
            link = jnc_get_link(f'https://j-novel.club{link_tag.find("a")["href"].split("search?")[0]}', volume)#attempts to get link for individual volume instead of entire series
        else: link = 'N/A'
    return (title, volume, link)

""" old jnc_get_link, site no longer works that way
def jnc_get_link(series_link, volume):#attempt to get volume link instead of link for entire series for J-Novel Club releases):
    try:#attempts to read volume (string) as an integer
        v = int(volume)
    except ValueError:#returns series_link if volume is not a valid integer
        return series_link
    driver_secondary.get(series_link)
    sleep(sleep_time)#ensure page loads before proceeding
    try:#attempts to find link to specific volume
        while v > 4:
            v -= 4
            driver_secondary.find_element_by_xpath('/html/body/div/div/div/div[1]/div[2]/div[1]/div[2]/div[1]/div/div/div[3]/button').click()#click right arrow button on volume list
            sleep(sleep_time)
        volume_link = driver_secondary.find_element_by_xpath(f'/html/body/div/div/div/div[1]/div[2]/div[1]/div[2]/div[1]/div/a[{v}]').get_attribute('href')#get url from correct volume
    except NoSuchElementException:#returns series_link if specific volume link
        return series_link
    if volume_link is not None and volume in volume_link: return volume_link
    return series_link
"""

if __name__ == '__main__':
    main()
    print(f'Total time: {str(perf_counter()-start_time)}')