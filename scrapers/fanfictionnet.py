import requests
import json
from bs4 import BeautifulSoup

def fanfictiondotnet(url: str):
    try:
        headers = {
            'User-Agent': 'fichub-client/0.0.1 +@Jemeni11/Summarium/1.0.0.0',
        }
        payload = {'q': url}

        response = requests.get(f'https://fichub.net/api/v0/epub', headers=headers, params=payload)
        FICTION_DATA = response.json()['meta']
        
    #*********** PROFILE TOP ***********
        FANDOM = None
        COVER_IMAGE = None

        STORY_TITLE = FICTION_DATA['title']
        AUTHOR = FICTION_DATA['author']
        AUTHOR_LINK = FICTION_DATA['authorUrl']
        SYNOPSIS = BeautifulSoup(FICTION_DATA['description'], "lxml").get_text(strip=True)
        CHAPTERS = FICTION_DATA['chapters']
        WORDS = f"{FICTION_DATA['words']:,}"
        STATUS = FICTION_DATA['status']
        UPDATED = FICTION_DATA['updated']
        PUBLISHED = FICTION_DATA['created']

        STATS = FICTION_DATA['extraMeta'].split(' - ')
        RATING = f"[{STATS[0][6:].strip()}](https://www.fictionratings.com/)"
        LANGUAGE = STATS[1][10:].strip()
        GENRE =  None
        CHARACTERS =  None

        for i in STATS:
            if i.startswith('Genre:'):
                GENRE = i[7:].strip()
            elif i.startswith('Characters:'):
                CHARACTERS = i[12:].strip()

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
            'STATUS':STATUS,
            'UPDATED': UPDATED,
            'PUBLISHED': PUBLISHED
        }

    except Exception as err:
        return f'Error with FF Story -> {err}'
