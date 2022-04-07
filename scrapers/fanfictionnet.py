import typing
from bs4 import BeautifulSoup
import requests
import re

def fanfictionnet(url: str) -> typing.Union[dict, str]:
    """
    REQUIRED: 
        - Title
        - Description
        - Genre
        - Main Genre
        - Fandom (only if 'Fanfiction' is selected as the Main Genre)
    """
    try:
        urlSplit = url.split('/')

        if re.search(r"(^https://www\.scribblehub\.com/read)/\d+", url):
            storyID = urlSplit[4].split('-')[0]
            storyName = '-'.join(urlSplit[4].split('-')[1:-1]) + '-'
            url = f'https://www.scribblehub.com/series/{storyID}/{storyName}/'

        # mainUrl = 'https://www.scribblehub.com/series/412872/star-burst-of-sector-/'
        #           # /([0-9]{6})/([a-z]*[/-])+
        # annoyingUrl = 'https://www.scribblehub.com/read/412872-star-burst-of-sector-/chapter/412875/'

        webPage = requests.get(url)
        soup = BeautifulSoup(webPage.text, "lxml")

        # ++++++++++++++++++++++COVER IMAGE++++++++++++++++++++++
        COVER_IMAGE = ' ' if not soup.find('div', class_='fic_image') else soup.find('div', class_='fic_image').contents[1]['src']

        # ++++++++++++++++++++++FIC STATS++++++++++++++++++++++
        STORY_TITLE = soup.find('div', class_='fic_title')['title'].strip()
        AUTHOR = soup.find('span', class_='auth_name_fic').text.strip()
        AUTHOR_PROFILE_LINK = soup.find('span', class_='auth_name_fic').parent['href']
        AUTHOR_AVATAR_LINK = soup.find('img', {'id': 'acc_ava_change none'})['src']
        VIEWS = soup.find('i', class_='fa fa-eye').parent.text.strip()
        FAVOURITES = soup.find('i', class_='fa fa-heart').parent.text.strip()
        CHAPTER_COUNT = soup.find('i', class_='fa fa-list-alt').parent.text.strip()
        STORY_UPDATE_FREQUENCY = soup.find('i', class_='fa fa-calendar fic').parent.text.strip()
        READERS = soup.find('i', class_='fa fa-user-o fic').parent.text.strip()

        # SYNOPSIS = soup.find('div', {'class': 'wi_fic_desc', 'property': 'description'}).get_text(strip=True)
        # SYNOPSIS.replace('\n', '<br>')
        SYNOPSIS = '\n'.join(soup.find('div', {'class': 'wi_fic_desc', 'property': 'description'}).stripped_strings)
        # Each novel is limited to 9 genres
        GENRES = ' • '.join(i.get_text() for i in soup.find_all('span', {'property': 'genre'}))
        # If the Fanfiction genre is selected, a fandom is required. Which series are you writing your fanfiction for? One entry per line. Limit five.
        FANDOM = ' • '.join([i.get_text() for i in soup.find_all('span', class_='wi_fic_genre')[1].contents if i.get_text()[-1] != ' '])
        # Each novel is limited to 25 tags
        # TAGS = '#' + ' #'.join([i.get_text() for i in soup.find('span', class_='wi_fic_showtags_inner').contents if i.get_text()[-1] != ' '])

        CONTENT_WARNING = 'N/A' if not soup.find('ul', class_='ul_rate_expand') else '\n'.join(f"- {i.get_text()}" for i in soup.find('ul', class_='ul_rate_expand'))

        STATS = {'COVER_IMAGE': COVER_IMAGE,
                'STORY_TITLE': STORY_TITLE, 
                'AUTHOR': AUTHOR, 
                'AUTHOR_PROFILE_LINK': AUTHOR_PROFILE_LINK,
                'AUTHOR_AVATAR_LINK': AUTHOR_AVATAR_LINK,
                'VIEWS': VIEWS, 
                'FAVOURITES': FAVOURITES,
                'CHAPTER_COUNT': CHAPTER_COUNT, 
                'STORY_UPDATE_FREQUENCY': STORY_UPDATE_FREQUENCY,
                'READERS': READERS, 
                'CONTENT_WARNING': CONTENT_WARNING, 
                'SYNOPSIS': SYNOPSIS, 
                'GENRES': GENRES,
                'FANDOM': FANDOM, 
                # 'TAGS': TAGS
                }

        return STATS
    except Exception as err:
        return f'{err}'
