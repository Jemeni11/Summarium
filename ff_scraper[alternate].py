
import requests
from bs4 import BeautifulSoup
import re
from pprint import pprint

def fanfiction_dot_net(url: str):
    # if re.search(r"^https://m?\.?fanfiction\.net/s/\d+",url, re.IGNORECASE):
    #     #? For basic fanfiction_dot_net stories/works
    #     """ 
    #     """
        try:
            webPage = requests.get(url)
            soup = BeautifulSoup(webPage.text, "lxml")

            #!INCOMPLETE: Does not support multi-fandoms
            FANDOM = soup.find('div', {'id': 'pre_story_links'}).span.contents[2].get_text()

            #*********** PROFILE TOP ***********
            PROFILE_TOP = soup.find('div', {'id': 'profile_top'})

            COVER_IMAGE = PROFILE_TOP.span.img['src']
            if not COVER_IMAGE.startswith('https://'):
                COVER_IMAGE = f"https://www.fanfiction.net{COVER_IMAGE}"
            
            STORY_TITLE = PROFILE_TOP.find('b', class_='xcontrast_txt').get_text(strip=True)
            
            AUTHOR = PROFILE_TOP.find('a', class_='xcontrast_txt').get_text(strip=True)
            
            AUTHOR_LINK = PROFILE_TOP.find('a', class_='xcontrast_txt')['href']
            if not AUTHOR_LINK.startswith('https://'):
                AUTHOR_LINK = f"https://www.fanfiction.net{AUTHOR_LINK}"
            
            SYNOPSIS = PROFILE_TOP.find('div', class_='xcontrast_txt').get_text(strip=True)

            STATS = PROFILE_TOP.find('span', class_='xgray xcontrast_txt').get_text(strip=True).split('-')
            RATING = f"[{STATS[0][6:]}](https://www.fictionratings.com/)"
            LANGUAGE = STATS[1].strip()
            GENRE = STATS[2].strip()
            CHARACTERS = STATS[3].strip()
            CHAPTERS = STATS[4].strip()[10:]
            WORDS = STATS[5].strip()[7:]
            UPDATED = STATS[9].strip()[8:]
            PUBLISHED = STATS[10].strip()[10:]

            return {
                'FANDOM': FANDOM,
                'COVER_IMAGE': COVER_IMAGE,
                'STORY_TITLE': STORY_TITLE,
                'AUTHOR': AUTHOR,
                'AUTHOR_LINK': AUTHOR_LINK,
                'SYNOPSIS': SYNOPSIS,
                'RATING': RATING,
                'LANGUAGE': LANGUAGE,
                'GENRE': GENRE,
                'CHARACTERS': CHARACTERS,
                'CHAPTERS': CHAPTERS,
                'WORDS': WORDS,
                'UPDATED': UPDATED,
                'PUBLISHED': PUBLISHED
            }

        except Exception as err:
            return f'Error with Fanfiction -> {err}'

if __name__ == '__main__':
    print(fanfiction_dot_net('https://www.fanfiction.net/s/13942236/1/'))
