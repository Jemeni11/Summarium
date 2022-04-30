import requests
import json
from bs4 import BeautifulSoup

def fanfictiondotnet(url: str):
    try:
        headers = {
            'User-Agent': 'fichub-client/0.0.1 +@iris',
        }

        response = requests.get(f'https://fichub.net/api/v0/epub?q={url}', headers=headers)
        FICTION_DATA = json.loads(response.text)['meta']
        
    #*********** PROFILE TOP ***********
            
        STORY_TITLE = FICTION_DATA['title']
        AUTHOR = FICTION_DATA['author']
        AUTHOR_LINK = FICTION_DATA['authorUrl']
        SYNOPSIS = BeautifulSoup(FICTION_DATA['description'], "lxml").get_text(strip=True)
        CHAPTERS = FICTION_DATA['chapters']
        WORDS = FICTION_DATA['words']
        UPDATED = FICTION_DATA['updated']
        PUBLISHED = FICTION_DATA['created']

        STATS = FICTION_DATA['extraMeta'].split(' - ')
        RATING = f"[{STATS[0][6:].strip()}](https://www.fictionratings.com/)"
        LANGUAGE = STATS[1][10:].strip()
        GENRE = STATS[2][7:].strip()
        CHARACTERS = STATS[3][12:].strip()

        return {
            # 'FANDOM': FANDOM,
            # 'COVER_IMAGE': COVER_IMAGE,
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
        return f'Error with FF Story -> {err}'

if __name__ == '__main__':
    print(fanfictiondotnet('https://www.fanfiction.net/s/13942236/1/'))
    print(fanfictiondotnet('https://www.fanfiction.net/s/14035761/9'))
    print(fanfictiondotnet('https://www.fanfiction.net/s/13371364/1/'))
