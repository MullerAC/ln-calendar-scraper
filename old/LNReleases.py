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

def book_walker():#gets links to all exclusive light novel series from homepage, then searches those links for upcoming releases
    result = []
    with urlopen('https://global.bookwalker.jp/') as site:#open homepage, get html, and close
        soup = BeautifulSoup(site, 'html.parser')
    series_list = []
    for series_tags in soup.find_all('div', class_='drop-down-categories-box'):#search homepage for all exclusive light novel series
        if 'Exclusive Light Novels' in series_tags.get_text():
            series_list = series_tags.find_all('a')
            break
    for series in series_list:result.extend(bw_scrape(f'{series["href"]}/?&order=release'))#iterate through all exclusive light novel series and read results
    for release in result: release['publisher'] = 'Book Walker'#iterates through all found releases to update publisher
    print(f'{len(result)} releases found for Book Walker, completed at {perf_counter()-start_time}')
    return result

def cross_infinite_world_digital():#gets upcoming digital releases from Book Walker
    '''result = bw_scrape('/publishers/1176/?np=1&order=release')#read results from Book Walker
    for release in result: release['publisher'] = 'Cross Infinite World'#iterates through all found releases to update publisher
    print(f'{len(result)} releases found for Cross Infinite World (digital), completed at {perf_counter()-start_time}')'''
    result = []
    print(f'Cross Infinite World (digital) not yet implemented, completed at {perf_counter()-start_time}')
    return result

def cross_infinite_world_physical():#not yet implemented
    result = []
    print(f'Cross Infinite World (physical) not yet implemented, completed at {perf_counter()-start_time}')
    return result

def dark_horse():#runs a search for Vampire Hunter D (Dark Horse's only active license) and searches that page for upcoming releases
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

def j_novel_club_beta():#gets all upcoming releases from the calendar, then searches the series nickname on the website to get the full title and link
    result = []
    month = today.month
    year = today.year
    #url = f'https://j-novel.club/calendar?year={year}&month={month}&type=novel&rel=digital'
    driver.get('https://j-novel.club/')#open driver to calendar url
    sleep(sleep_time)
    driver.find_element_by_xpath('/html/body/div/div/div[1]/div[1]/div[2]/a[3]').click()#go to calendar, using url messes up html
    sleep(sleep_time)
    driver.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div[3]/div/div[5]/div[2]').click()#show only full digital ebook releases
    sleep(sleep_time)
    driver.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div[3]/div/div[7]/div[2]').click()#show only novels
    sleep(sleep_time)
    driver.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div[4]/div/div[1]/div[2]').click()
    sleep(sleep_time)
    soup = BeautifulSoup(driver.execute_script('return document.body.innerHTML'), 'html.parser')
 
    calendar = soup.find('div', class_='f1owoso1')
    while 'Nothing to see here!' not in calendar.find('h2').get_text(strip=True):
        release_date = datetime.strptime(calendar.find('span', class_='f182sjpl').get_text(strip=True), '%B%Y').date()
        for item in calendar.find_all('div', recursive=False):
            if item.has_attr('class') and 'ffukg03' in item['class']:#item is a date
                release_date = release_date.replace(day=int(item.find('h2').find(text=True, recursive=False).strip()[:-2]))
            elif item.has_attr('class') and 'fhkbwa' in item['class']:#item is a release
                if release_date < today:
                    continue#skips item if it is before target date
                for item_release in item.find_all('a', class_='link f122npxj block'):
                    link = 'https://j-novel.club' + item_release['href']
                    volume_tag = item_release.find('span', class_='fpcytuh')
                    if volume_tag is None:
                        volume = 'tbd'
                    else:
                        volume = volume_tag.get_text().split()[-1]
                    driver_secondary.get(link)
                    sleep(sleep_time)
                    soup2 = BeautifulSoup(driver_secondary.execute_script('return document.body.innerHTML'), 'html.parser')
                    title = soup2.find('div', class_='ffukg03 header large fl45o3o').get_text(strip=True)
                    link = driver_secondary.current_url
                    #title = 'tmp'
                    
                    release = {'date': release_date, 'title': title, 'lndb_link': 'N/A', 'volume': volume, 'publisher': 'J-Novel Club', 'store_link': link, 'format': 'Digital'}
                    result.append(release)
            else:#item is a header, footer, empty date, or something else
                continue
        """year = year + 1 if month == 12 else year
        month = 1 if month == 12 else month + 1
        driver.get(f'https://j-novel.club/calendar?year={year}&month={month}&type=novel&rel=digital')#open driver to calendar url"""
        driver.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div[4]/div/div[1]/div[2]').click()
        sleep(sleep_time)
        soup = BeautifulSoup(driver.execute_script('return document.body.innerHTML'), 'html.parser')
        calendar = soup.find('div', class_='f1owoso1')
    print(f'{len(result)} releases found for J-Novel Club (beta/digital), completed at {perf_counter()-start_time}')
    return result

def j_novel_club_digital():#gets all upcoming releases from the calendar, then searches the series nickname on the website to get the full title and link
    result = []
    driver.get('https://old.j-novel.club/comingup')#open driver to calendar url
    while True:#loop through each month of releases
        sleep(sleep_time)
        soup = BeautifulSoup(driver.execute_script('return document.body.innerHTML'), 'html.parser')
        main_div = soup.find('div', class_='_3cr17rf9k2KgJzj1q6CzVI').find('div', class_='_2iUMdY')
        if 'No releases scheduled yet!' in main_div.get_text(): break#break from loop when reaching a month with no scheduled releases
        release_date = datetime.strptime(soup.find('div', class_='_3vBXdKgEyugvFJSj0XHYbJ').get_text().replace(' RELEASE SCHEDULE', '').strip(), '%B %Y').date()
        if release_date.month >= today.month or release_date.year > today.year:#go to next month if calendar month is before target date
            for item in main_div.children:#iterate through every item on page, dates and releases
                item_text = item.get_text(strip=True)
                try:#will change date if item is a date
                    release_date = datetime.strptime(item_text, '%A, %B %d').date()
                    release_date = release_date.replace(year=today.year+(release_date.month<today.month))
                except ValueError:#if item is not a date, it is a release item
                    if release_date < today: continue#skips item if it is before target date
                    if any(s not in item_text for s in ['Ebook', 'Novel']): continue#skips item if not a light novel ebook release
                    title_volume = item.find('h1').get_text(strip=True).replace(' Vol. ', ' Vol ').replace(' Volume ', ' Vol ').replace(': Vol ', ' Vol ').split(' Vol ', 1)
                    title, volume, link = jnc_get_title_volume_link(title_volume)#searches JNC site for more accurate title and link
                    release = {'date': release_date, 'title': title, 'lndb_link': '', 'volume': volume, 'publisher': 'J-Novel Club', 'store_link': link, 'format': 'Digital'}
                    result.append(release)
        driver.find_element_by_xpath('/html/body/div/div/div/div[1]/div[2]/div[1]/div[1]/div[3]/button').click()#click "NEXT MONTH" button to load next month's calendar
    print(f'{len(result)} releases found for J-Novel Club (digital), completed at {perf_counter()-start_time}')
    return result

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

def one_peace_digital():#gets upcoming digital releases from Book Walker
    '''result = bw_scrape('/publishers/736/?np=1&order=release')#read results from Book Walker
    for release in result:#iterates through all found releases to update publisher and links
        release['publisher'] = 'One Peace Books'
        if 'Shield Hero' in release['title']: release['store_link'] = 'https://www.onepeacebooks.com/jt/ShieldHeroLNV.html'
        elif 'Spear Hero' in release['title']: release['store_link'] = 'https://www.onepeacebooks.com/jt/SpearHeroLNV.html'
    print(f'{len(result)} releases found for One Peace (digital), completed at {perf_counter()-start_time}')'''
    result = []
    print(f'One Peace (digital) not yet implemented, completed at {perf_counter()-start_time}')
    return result

    return result

def one_peace_physical():#gets upcoming physical releases from Right Stuf Anime
    '''result = rsa_scrape('/category/Novels/publisher/ONE-PEACE?order=custitem_rs_release_date:desc&show=96')#read results from Right Stuf Anime
    for release in result:#iterates through all found releases to update publisher and links
        release['publisher'] = 'One Peace Books'
        if 'Shield Hero' in release['title']: release['store_link'] = 'https://www.onepeacebooks.com/jt/ShieldHeroLNV.html'
        elif 'Spear Hero' in release['title']: release['store_link'] = 'https://www.onepeacebooks.com/jt/SpearHeroLNV.html'
    print(f'{len(result)} releases found for One Peace (physical), completed at {perf_counter()-start_time}')'''
    result = []
    print(f'One Peace (physical) not yet implemented, completed at {perf_counter()-start_time}')
    return result

    return result

def seven_seas():#digital and physical releases are on two separate calendars
    result = []
    urls = {'https://sevenseasentertainment.com/digital/': 'Digital', 'https://sevenseasentertainment.com/release-dates/': 'Physical'}
    for url in urls.keys():#repeats for both digital and physical calendars
        with urlopen(url) as site:#open calendar, get html, and close
            soup = BeautifulSoup(site, 'html.parser')
        for item in soup.find_all('tr', id='volumes'):#iterate through every item on page
            if 'Novel' not in item.get_text(): continue#skip item if it is not a light novel
            release_date = datetime.strptime(item.find('td').get_text(strip=True), '%Y/%m/%d').date()
            if release_date < today: continue#skips item if it is before target date
            title_volume_link = item.find('a')
            title_volume = title_volume_link.get_text(strip=True).replace(' (Light Novel)', '').replace(' (Novel)', '').split(' Vol. ')
            title = title_volume[0]
            volume = title_volume[-1] if len(title_volume)>1 else '1'
            link = title_volume_link['href']
            release = {'date': release_date, 'title': title, 'lndb_link': '', 'volume': volume, 'publisher': 'Seven Seas', 'store_link': link, 'format': urls[url]}
            result.append(release)
    print(f'{len(result)} releases found for Seven Seas, completed at {perf_counter()-start_time}')
    return result

def sol_press_digital():#gets upcoming digital releases from SOl PRess's website calendar
    result = []
    with urlopen('https://solpress.co/light-novels') as site:#open calendar, get html, and close
        soup = BeautifulSoup(site, 'html.parser')
    for item in soup.find_all('section', class_='details'):#iterate through every item on page
        release_date_text = item.find('section').find_all('strong')[1].get_text(strip=True).split(',')
        if release_date_text[0] == 'To be announced': continue#skips item if it has no set date
        release_date_text[0] = release_date_text[0][:-2]
        release_date = datetime.strptime(','.join(release_date_text), '%B %d, %Y').date()
        if release_date < today: break#breaks loop if the date has gone past the target date
        title_volume_link = item.find('a')
        title_volume = title_volume_link.get_text(strip=True).replace(' (light novel)', '').split(' Vol. ')
        title = title_volume[0]
        if len(title_volume) > 1:
            volume_subtitle = title_volume[1].split(':')
            volume = volume_subtitle[0]
            if len(volume_subtitle) > 1: title += f':{volume_subtitle[1]}'
        else: volume = '1'
        link = f'https://solpress.co{title_volume_link["href"]}'
        release = {'date': release_date, 'title': title, 'lndb_link': '', 'volume': volume, 'publisher': 'Sol Press', 'store_link': link, 'format': 'Digital'}
        result.append(release)
    print(f'{len(result)} releases found for Sol Press (digital), completed at {perf_counter()-start_time}')
    return result

def sol_press_physical():#no upcoming releases scheduled at the moment
    result = []
    print(f'Sol Press (physical) not yet implemented, completed at {perf_counter()-start_time}')
    return result

def square_enix():#opens every release on calendar to get light novels
    result = []
    driver.get('https://squareenixmangaandbooks.square-enix-games.com/en-us/release-calendar')#open driver to calendar url
    next_month = today#set initial calendar month to current month
    while True:#loops until no more releases are found
        try:#click calendar month button for the next month
            #print(f"{next_month.strftime('%B %Y')}")
            driver.find_element_by_xpath(f"//*[contains(text(), '{next_month.strftime('%B %Y')}')]").click()
        except NoSuchElementException:#break loop if no next month calendar is found
            break
        sleep(sleep_time)#ensure page loads before getting html
        soup = BeautifulSoup(driver.execute_script('return document.body.innerHTML'), 'html.parser')
        #print(soup.prettify())
        for item in soup.find('div', class_='SeriesWrapper-cLJjJY eZpbto sc-gxMtzJ clmQrN sc-bwzfXH liBCIH sc-bdVaJa iHZvIS').find_all('a'):
            link = f'https://squareenixmangaandbooks.square-enix-games.com{item["href"]}'
            driver_secondary.get(link)#open secondary driver to calendar url
            sleep(sleep_time)#ensure page loads before getting html
            soup_secondary = BeautifulSoup(driver_secondary.execute_script('return document.body.innerHTML'), 'html.parser')
            synopsis = soup_secondary.find('div', class_='synopsis')
            if synopsis is None: continue#skips item if it can not find synopsis
            synopsis = synopsis.find_all('div')
            if 'Novel' not in synopsis[3].get_text() and 'Novel' not in synopsis[4].get_text(): continue#skips item if it is not a light novel
            release_date = datetime.strptime(synopsis[2].get_text(strip=True).replace('release date:', ''), '%B %d, %Y').date()
            if release_date < today: continue#skips item if it is before target date
            title = soup_secondary.find('div', class_='book-title-section').find('div', class_='book-title').get_text(strip=True)
            volume = item.find('div').find_all('div')[-1].get_text().replace('Volume', '').strip()
            format = get_format(soup_secondary.find('div', class_='format-options').get_text())
            release = {'date': release_date, 'title': title, 'lndb_link': '', 'volume': volume, 'publisher': 'Square Enix', 'store_link': link, 'format': format}
            result.append(release)
        next_month = date(next_month.year+(next_month.month==12), next_month.month+1 if next_month.month<12 else 1, 1)
    print(f'{len(result)} releases found for Square Enix, completed at {perf_counter()-start_time}')
    return result

def tentai_digital():
    result = []
    print(f'Tentai (digital) not yet implemented, completed at {perf_counter()-start_time}')
    return result

def tentai_physical():
    result = []
    print(f'Tentai (physical) not yet implemented, completed at {perf_counter()-start_time}')
    return result

def vertical_digital():#not yet implemented
    result = []
    print(f'Vertical (digital) not yet implemented, completed at {perf_counter()-start_time}')
    return result

def vertical_physical():#gets upcoming physical releases from Right Stuf Anime
    result = rsa_scrape('/category/Novels/publisher/VERTICAL?order=custitem_rs_release_date:desc&show=96')#read results from Right Stuf Anime
    for release in result:
        release['publisher'] = 'Vertical'#iterates through all found releases to update publisher
        '''search_text = f'{release["title"]} Volume {release["volume"]}'
        release['store_link'] = 'Vertical'#iterates through all found releases to update publisher'''#auto-searching Random Penguin House seems inconsistent
        #release['store_link'] = 'N/A'
    print(f'{len(result)} releases found for Vertical (physical), completed at {perf_counter()-start_time}')
    return result

def viz_media():#gets upcoming releases from calendar, searches release page for format
    result = []
    url_base = 'https://www.viz.com/calendar/'
    m, y = today.month, today.year
    while True:#loops until no more releases are found
        with urlopen(f'{url_base}{y}/{m}') as site:#open calendar for next month, get html, and close
            soup = BeautifulSoup(site, 'html.parser')
        table = soup.find('table', class_='product-table')
        if table is None: break#break loop if no next month calendar is found
        for item in table.find_all('tr'):#iterate through every item in page
            item_text = []
            for cell in item.find_all('td'):#split up information for item
                item_text.append(cell.get_text(strip=True))
            if 'Novel' not in item_text[2]: continue#skip item if it is not a light novel
            release_date = datetime.strptime(item_text[4], '%b %d').date()
            release_date = release_date.replace(year=y)
            title_volume = item_text[3].split(', Vol. ')
            title = title_volume[0]
            volume = title_volume[-1] if len(title_volume)>1 else '1'
            link_end = item.find("a")["href"].replace('/paperback','').replace('/hardcover','').replace('/digital','')
            link = f'https://www.viz.com{link_end}'
            with urlopen(link) as site_secondary:#open item link page, get html, and close
                soup_secondary = BeautifulSoup(site_secondary, 'html.parser')
            format = get_format(soup_secondary.find('div', class_='type-rg type-md--md weight-bold').get_text())
            release = {'date': release_date, 'title': title, 'lndb_link': '', 'volume': volume, 'publisher': 'Viz Media', 'store_link': link, 'format': format}
            result.append(release)
        m = m+1 if m<12 else 1
        y = y+1 if m==1 else y
    print(f'{len(result)} releases found for Viz Media, completed at {perf_counter()-start_time}')
    return result

def yen_press():#gets links to releases from calendar, opens item links to get rest of information
    result = []
    with urlopen(Request('https://yenpress.com/yen-on/', headers={'User-Agent': 'Mozilla/5.0'})) as site:#spoof as a normal browser, open calendar, get html, and close
        soup = BeautifulSoup(site, 'html.parser')
    for month in soup.find_all('div', class_='book-shelf-wrap'):#iterate through every month on calendar
        for item in month.find_all('li'):#iterate through every item in month
            link = f'https://yenpress.com{item.find("a")["href"]}'
            with urlopen(Request(link, headers={'User-Agent': 'Mozilla/5.0'})) as site_secondary:#spoof as a normal browser, open item link, get html, and close
                soup_secondary = BeautifulSoup(site_secondary, 'html.parser')
            release_date = datetime.strptime(soup_secondary.find_all('span', class_='detail-value')[-1].get_text(strip=True), '%m/%d/%Y').date()
            if release_date < today: continue#skips item if it is before target date
            title_volume = soup_secondary.find('h2', id='book-title').get_text(strip=True).replace(' (light novel)', '').split(', Vol. ')
            title = title_volume[0]
            volume = title_volume[-1] if len(title_volume)>1 else '1'
            format = get_format(soup_secondary.find('div', id='book-format-details').get_text())
            release = {'date': release_date, 'title': title, 'lndb_link': '', 'volume': volume, 'publisher': 'Yen Press', 'store_link': link, 'format': format}
            result.append(release)
    print(f'{len(result)} releases found for Yen Press, completed at {perf_counter()-start_time}')
    return result

def get_format(format_text):#reads text to determine format type
    format = []
    if 'Paperback' in format_text or 'Hardcover' in format_text: format.append('Physical')
    if 'Digital' in format_text: format.append('Digital')
    if not format: format.append('N/A')
    return ' & '.join(format)

def bw_scrape(url):#scrape needed digital release data for any publisher from Book Walker, given the url
    result = []
    with urlopen(f'https://global.bookwalker.jp{url}') as site:#open page on Book Walker, get html, and close
        soup = BeautifulSoup(site, 'html.parser')
    for item in soup.find_all('li', class_='o-tile'):#iterate through every item on page
        date_tag = item.find('div', class_='a-tile-release-date')
        if date_tag is None: break#break loop if item found with no upcoming release date (already released)
        release_date = datetime.strptime(date_tag.get_text(strip=True).replace('.', ' '), '%b %d release').date()
        release_date = release_date.replace(year=today.year+(release_date.month<today.month))
        if release_date < today: break#break loop if date is earlier than target date
        if 'Novel' not in item.find('ul', class_='m-tile-tag-box').get_text(): continue#skip item if it is not a light novel
        title_volume_link = item.find('h2', class_='a-tile-ttl').find('a')
        title_volume = title_volume_link.get_text(strip=True).split(' Volume ')
        title = title_volume[0]
        volume = title_volume[-1] if len(title_volume)>1 else '1'
        link = title_volume_link['href']
        release = {'date': release_date, 'title': title, 'lndb_link': '', 'volume': volume, 'publisher': 'N/A', 'store_link': link, 'format': 'Digital'}
        result.append(release)
    return result

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