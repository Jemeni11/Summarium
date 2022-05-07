import typing
from bs4 import BeautifulSoup
import requests
import re

class ScribbleHub:
    def __init__(self, url: str) -> None:
        self.url = url
        if re.search(r"(^https://www\.scribblehub\.com/read)/\d+", self.url, re.IGNORECASE):
            # Turns'https://www.scribblehub.com/read/412872-star-burst-of-sector-/chapter/412875/'
            # into 'https://www.scribblehub.com/series/412872/star-burst-of-sector-/'
            
            urlSplit = self.url.split('/')
            storyID = urlSplit[4].split('-')[0]
            storyName = '-'.join(urlSplit[4].split('-')[1:-1]) + '-'
            self.url = f'https://www.scribblehub.com/series/{storyID}/{storyName}/'
        self.webPage = requests.get(self.url)
        self.soup = BeautifulSoup(self.webPage.text, "lxml")

    def SHWork(self) -> typing.Union[dict, str]:
        """
        REQUIRED: 
            - Title
            - Description
            - Genre
            - Main Genre
            - Fandom (only if 'Fanfiction' is selected as the Main Genre)
        """
        # ++++++++++++++++++++++COVER IMAGE++++++++++++++++++++++
        COVER_IMAGE = ' ' if not self.soup.find('div', class_='fic_image') else self.soup.find('div', class_='fic_image').contents[1]['src']

        # ++++++++++++++++++++++FIC STATS++++++++++++++++++++++
        STORY_TITLE = self.soup.find('div', class_='fic_title')['title'].strip()
        AUTHOR = self.soup.find('span', class_='auth_name_fic').text.strip()
        AUTHOR_PROFILE_LINK = self.soup.find('span', class_='auth_name_fic').parent['href']
        AUTHOR_AVATAR_LINK = self.soup.find('img', {'id': 'acc_ava_change none'})['src']
        VIEWS = self.soup.find('i', class_='fa fa-eye').parent.text.strip()
        FAVOURITES = self.soup.find('i', class_='fa fa-heart').parent.text.strip()
        CHAPTER_COUNT = self.soup.find('i', class_='fa fa-list-alt').parent.text.strip()
        READERS = self.soup.find('i', class_='fa fa-user-o fic').parent.text.strip()
        
        SYNOPSIS_SOUP = self.soup.find('div', {'class': 'wi_fic_desc', 'property': 'description'})
        SYNOPSIS = '\n'.join(SYNOPSIS_SOUP.stripped_strings)

        # Each novel is limited to 9 genres
        GENRES = ' • '.join(i.get_text() for i in self.soup.find_all('span', {'property': 'genre'}))

        # If the Fanfiction genre is selected, a fandom is required. 
        # Which series are you writing your fanfiction for? One entry per line. Limit five.
        if 'Fanfiction' in GENRES:
            FANDOM_SOUP = self.soup.find_all('span', class_='wi_fic_genre')
            FANDOM_SOUP_LIST = [i.get_text() for i in FANDOM_SOUP[1].contents if i.get_text()[-1] != ' ']
            FANDOM = ' • '.join(FANDOM_SOUP_LIST)
        else:
            FANDOM = 'N/A'

        CONTENT_WARNING_SOUP = self.soup.find('ul', class_='ul_rate_expand')
        CONTENT_WARNING = 'N/A' if not CONTENT_WARNING_SOUP else ' • '.join(i.get_text() for i in CONTENT_WARNING_SOUP)

        return {
            'COVER_IMAGE': COVER_IMAGE,
            'STORY_TITLE': STORY_TITLE, 
            'AUTHOR': AUTHOR, 
            'AUTHOR_PROFILE_LINK': AUTHOR_PROFILE_LINK,
            'AUTHOR_AVATAR_LINK': AUTHOR_AVATAR_LINK,
            'VIEWS': VIEWS, 
            'FAVOURITES': FAVOURITES,
            'CHAPTER_COUNT': CHAPTER_COUNT,
            'READERS': READERS, 
            'CONTENT_WARNING': CONTENT_WARNING, 
            'SYNOPSIS': SYNOPSIS, 
            'GENRES': GENRES,
            'FANDOM': FANDOM
        }

    def SHProfile(self) -> typing.Union[dict, str]:
        #? Header
        HEADING = self.soup.find('div', class_='top_header_profile')

        PROFILE_PHOTO = HEADING.find('span', class_='p_avatar').img['src']
        AUTHOR_NAME = HEADING.find('div', class_='p_m_username').get_text(strip=True)

        STATS = [i.get_text(strip=True) for i in HEADING.find('div', class_='p_pairstats').contents if i != '\n']
        JOINED = STATS[0][6:]
        FOLLOWERS = STATS[1][9:]
        FOLLOWING = STATS[2][9:]

        #? Overview
        OVERVIEW = self.soup.find('section', {'id': 'profile_content6'})

        #? Personal Information
        PERSONAL_INFORMATION = self.soup.find('div', class_='overview_title', text='Personal Information')
        PERSONAL_TABLE = PERSONAL_INFORMATION.next_sibling.next_sibling.tbody
        PERSONAL_TABLE_STATS = [i.get_text(strip=True) for i in PERSONAL_TABLE if i != '\n']
        
        LAST_ACTIVE = PERSONAL_TABLE_STATS[0][12:]
        HOME_PAGE = PERSONAL_TABLE_STATS[4][9:]
        if HOME_PAGE == f"http://{AUTHOR_NAME}" or HOME_PAGE == "--":
            HOME_PAGE = "N/A"

        #? About
        ABOUT = OVERVIEW.find('div', class_='user_bio_profile').text.strip()

        #? Author Information
        AUTHOR_INFORMATION = self.soup.find('div', class_='overview_title', text='Author Information')
        TABLE = AUTHOR_INFORMATION.next_sibling.next_sibling.tbody
        TABLE_STATS = [i.get_text(strip=True) for i in TABLE if i != '\n']
        del TABLE_STATS[-1]

        NUMBER_OF_SERIES = TABLE_STATS[0][7:]
        READERS = TABLE_STATS[4][8:]

        return {
            'PROFILE_PHOTO': PROFILE_PHOTO,
            'AUTHOR_NAME': AUTHOR_NAME,
            'ABOUT': ABOUT,
            'HOME_PAGE': HOME_PAGE,
            'LAST_ACTIVE': LAST_ACTIVE,
            'JOINED': JOINED,
            'FOLLOWERS': FOLLOWERS,
            'FOLLOWING': FOLLOWING,
            'NUMBER_OF_SERIES': NUMBER_OF_SERIES,
            'READERS': READERS
        }
