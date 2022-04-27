import requests
from bs4 import BeautifulSoup
import re

def chunker(seq, size):
    return [seq[pos:pos + size] for pos in range(0, len(seq), size)]

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
            # AUTHOR & AUTHOR_LIST are only used when there's one author.
            AUTHOR = AUTHOR_LIST[0][AUTHOR_LIST[0].index('[')+1:AUTHOR_LIST[0].index(']')]
            AUTHOR_LINK = f"https://archiveofourown.org{soup.find('a', {'rel': 'author'})['href']}"
            AUTHOR_IMAGE_SOUP = BeautifulSoup(requests.get(AUTHOR_LINK).text, "lxml").find('div', class_="primary header module")
            AUTHOR_IMAGE = [i for i in AUTHOR_IMAGE_SOUP.contents if i != '\n'][1].a.img['src']
            AUTHOR_IMAGE_LINK = AUTHOR_IMAGE if AUTHOR_IMAGE.startswith('https://') else f"https://archiveofourown.org{AUTHOR_IMAGE}"

            # return STATS
            return {'LINK_TYPE': 'STORY',
                    'RATING': RATING,
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
            return f'Error with A03 Work -> {err}'

    elif re.search(r"^https://archiveofourown\.org/series/\d+",url):
        """
            Series Title* [240 characters left]
            Creator(s): [Add co-creators?]
            Series Begun:
            Series Updated:
            Description: [1250 characters left]
            Notes: [5000 characters left]
            Stats: [Words: Works: Complete: Bookmarks:]
        """
        try:
            webPage = requests.get(url)
            soup = BeautifulSoup(webPage.text, "lxml")
            SERIES_DATA = soup.find('dl', class_='series meta group')

            SERIES_TITLE = soup.find('h2',class_='heading').get_text(strip=True)
    
            AUTHOR_LIST = [f"[{i.get_text()}](https://archiveofourown.org{i['href']})" for i in SERIES_DATA.dd if i not in ['\n', ', ']]
            # AUTHOR & AUTHOR_LINK are only used when there's one author.
            AUTHOR = AUTHOR_LIST[0][AUTHOR_LIST[0].index('[')+1:AUTHOR_LIST[0].index(']')]
            AUTHOR_LINK = f"https://archiveofourown.org{soup.find('a', {'rel': 'author'})['href']}"
            AUTHOR_IMAGE_SOUP = BeautifulSoup(requests.get(AUTHOR_LINK).text, "lxml").find('div', class_="primary header module")
            AUTHOR_IMAGE = [i for i in AUTHOR_IMAGE_SOUP.contents if i != '\n'][1].a.img['src']
            AUTHOR_IMAGE_LINK = AUTHOR_IMAGE if AUTHOR_IMAGE.startswith('https://') else f"https://archiveofourown.org{AUTHOR_IMAGE}"
            SERIES_BEGUN = ''.join(i.next_sibling.next_sibling.get_text() for i in SERIES_DATA.find_all('dt', string='Series Begun:'))
            SERIES_UPDATED = ''.join(i.next_sibling.next_sibling.get_text() for i in SERIES_DATA.find_all('dt', string='Series Updated:'))
            
            # Stats: [Words: Works: Complete: Bookmarks:]
            Stats_text = ''
            statsArr = [i.get_text(strip=True) for i in SERIES_DATA.find_all('dt', string='Stats:')[0].next_sibling.next_sibling.dl][1:-1]
            for group in chunker(statsArr, 4):
                Stats_text += f"{' '.join(group)} • "
            STATS = Stats_text[:-2] 
    
            try:
                descriptionVar = SERIES_DATA.find_all('dt', string='Description:')[0].next_sibling.next_sibling.blockquote
                descriptionVar = str(descriptionVar).replace('<br/>', '\r\n')
                descriptionVar = str(descriptionVar).replace('</p><p>', '</p><p>\r\n</p><p>')
                DESCRIPTION = BeautifulSoup(descriptionVar, 'lxml').get_text()
            except:
                DESCRIPTION = None

            try:
                notesVar = SERIES_DATA.find_all('dt', string='Notes:')[0].next_sibling.next_sibling.blockquote
                notesVar = str(notesVar).replace('<br/>', '\r\n')
                notesVar = str(notesVar).replace('</p><p>', '</p><p>\r\n</p><p>')
                NOTES = BeautifulSoup(notesVar, 'lxml').get_text()
            except:
                NOTES = None

            return {
                'LINK_TYPE': 'SERIES',
                'SERIES_TITLE': SERIES_TITLE,
                'AUTHOR': AUTHOR,
                'AUTHOR_LINK': AUTHOR_LINK,
                'AUTHOR_LIST': AUTHOR_LIST,
                'AUTHOR_IMAGE_LINK': AUTHOR_IMAGE_LINK,
                'SERIES_BEGUN': SERIES_BEGUN,
                'SERIES_UPDATED': SERIES_UPDATED,
                'DESCRIPTION': DESCRIPTION,
                'NOTES': NOTES,
                'STATS': STATS
            }

        except Exception as err:
            return f'Error with A03 Series -> {err}'

if __name__ == '__main__':
    print(archive_of_our_own('https://archiveofourown.org/works/25069339/chapters/91671940'))
    print(archive_of_our_own('https://archiveofourown.org/series/1633756'))
