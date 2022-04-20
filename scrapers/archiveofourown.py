import requests
from bs4 import BeautifulSoup
import re

def archive_of_our_own(url: str):
    if re.search(r"^https://archiveofourown\.org/works/\d+",url):
        # For basic AO3 stories/works
        if url[-16:] != '?view_adult=true':
            url += '?view_adult=true'
        """ 
        Tags:
            Tags are comma separated, 100 characters per tag. Fandom, 
            relationship, character, and additional tags must not add
            up to more than 75. Archive warning, category, and rating
            tags do not count toward this limit. Tags are comma separated,
            100 characters per tag. Fandom, relationship, character, and
            additional tags must not add up to more than 75. Archive warning,
            category, and rating tags do not count toward this limit.
            - Rating*
            - Archive Warnings*
            - Fandoms*
            - Categories
            - Relationships
            - Characters 
            - Additional Tags
        Preface:
            - Work Title* [255 characters]
            - Add co-creators?
            - Summary [1250 characters]
            - Notes
        Association:
            - Post to Collections/Challenges
            - Gift this work to
            - This work is part of a series?
            - Choose a language*
            - Select Work Skin
        Privacy:
            - Who can comment on this work
        Work Text:
            - [500000 characters ]
        """
        try:
            webPage = requests.get(url)
            soup = BeautifulSoup(webPage.text, "lxml")

            # ===============TAGS   
            RATING = soup.find('dd', class_='rating tags').get_text(strip=True)
            ARCHIVE_WARNING = ', '.join(_.get_text(strip=True) for _ in soup.find('dd', class_='warning tags').contents[1])[2:-2]
            FANDOM = ', '.join(i.get_text() for i in soup.find('dd', class_='fandom tags').contents[1])[3:-3]
            RELATIONSHIPS = 'N/A' if not soup.find('dd', class_='relationship tags') else ', '.join(_.get_text() for _ in soup.find('dd', class_='relationship tags').contents[1])[3:-3]
            CHARACTERS = 'N/A' if not soup.find('dd', class_='character tags') else ', '.join(_.get_text() for _ in soup.find('dd', class_='character tags').contents[1])[3:-3]
            
            # ===============PREFACE 
            TITLE = soup.find('h2', class_='title heading').get_text(strip=True)
            SUMMARY = soup.find('blockquote', class_="userstuff").get_text(strip=True)

            # ===============ASSOCIATION
            SeriesList = []
            for i in soup.find_all('span', class_='series'):
                SeriesList.extend([f"[{_.get_text()}](https://archiveofourown.org{_['href']})" for _ in i.find_all('a', class_=None)])
            SERIES = list(set(SeriesList))
            LANGUAGE = soup.find('dd', class_='language').get_text(strip=True)

            # ===============EXTRAS
            STATS = ' '.join([f"{_.get_text()} •" if _.get_text()[-1] != ':' else _.get_text() for _ in soup.find('dl', class_='stats').contents ])[:-2]
            AUTHOR_LIST = [f"[{i.get_text()}](https://archiveofourown.org{i['href']})" for i in soup.find('h3', class_='byline heading').contents if i not in ['\n', ', ']]
            AUTHOR = AUTHOR_LIST[0][AUTHOR_LIST[0].index('[')+1:AUTHOR_LIST[0].index(']')]
            AUTHOR_LINK = f"https://archiveofourown.org{soup.find('a', {'rel': 'author'})['href']}"
            AUTHOR_IMAGE_SOUP = BeautifulSoup(requests.get(AUTHOR_LINK).text, "lxml").find('div', class_="primary header module")
            AUTHOR_IMAGE = [i for i in AUTHOR_IMAGE_SOUP.contents if i != '\n'][1].a.img['src']
            AUTHOR_IMAGE_LINK = AUTHOR_IMAGE if AUTHOR_IMAGE.startswith('https://') else f"https://archiveofourown.org{AUTHOR_IMAGE}"

            # return STATS
            return {'RATING': RATING,
                    'ARCHIVE_WARNING': ARCHIVE_WARNING,
                    'FANDOM': FANDOM,
                    'CHARACTERS': CHARACTERS,
                    'RELATIONSHIPS': RELATIONSHIPS,
                    'TITLE': TITLE,
                    'SUMMARY': SUMMARY,
                    'SERIES': SERIES,
                    'LANGUAGE': LANGUAGE,
                    'STATS': STATS,
                    'AUTHOR': AUTHOR,
                    'AUTHOR_LINK': AUTHOR_LINK,
                    'AUTHOR_LIST': AUTHOR_LIST,
                    'AUTHOR_IMAGE_LINK': AUTHOR_IMAGE_LINK
                    }
        except Exception as err:
            return f'Error -> {err}'

    elif re.search(r"^https://archiveofourown\.org/works/\d+",url):
        # class="series meta group"
        pass

if __name__ == '__main__':
    print(archive_of_our_own('https://archiveofourown.org/works/25069339/chapters/91671940'))
