import requests
from bs4 import BeautifulSoup
import re

def chunker(seq, size):
    return [seq[pos:pos + size] for pos in range(0, len(seq), size)]

def archive_of_our_own(url: str):
    if re.search(r"^https://archiveofourown\.org/works/\d+",url, re.IGNORECASE):
        # For basic AO3 stories/works
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
            if url[-16:] != '?view_adult=true':
                url += '?view_adult=true'
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

    elif re.search(r"^https://archiveofourown\.org/series/\d+",url, re.IGNORECASE):
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
            AUTHOR_LINK = AUTHOR_LIST[0][AUTHOR_LIST[0].index('(')+1:AUTHOR_LIST[0].index(')')]
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

    elif re.search(r"^https://archiveofourown\.org/collections/\w+",url, re.IGNORECASE):
        try:
            if url.split('/')[-1] != 'profile':
                url += '/profile'

            webPage = requests.get(url)
            soup = BeautifulSoup(webPage.text, "lxml")

            # ++++++++++++++++++ HEADING ++++++++++++++++++
            HEADING = soup.find('div', class_='primary header module')

            STORY_TITLE = HEADING.find('h2', class_='heading')
            STORY_TITLE_TEXT = STORY_TITLE.get_text(strip=True)
            STORY_TITLE_LINK = f"https://archiveofourown.org{STORY_TITLE.find('a')['href']}"

            IMAGE_LINK = HEADING.find('div', class_='icon').img['src'] 
            IMAGE = IMAGE_LINK if IMAGE_LINK.startswith('https://') else f"https://archiveofourown.org{IMAGE_LINK}"

            SUMMARY = HEADING.find('blockquote', class_='userstuff').get_text(strip=True)
            STATUS = HEADING.find('p', class_='type').get_text(strip=True)

            # ++++++++++++++++++ WRAPPER ++++++++++++++++++
            WRAPPER = soup.find('dl', class_='meta group')

            ACTIVE_SINCE = WRAPPER.dt.next_sibling.get_text(strip=True)

            MAINTAINERS_LIST_HTML = [i for i in WRAPPER.find('ul', class_='mods commas') if i not in ['\n', ', ']]  
            MAINTAINERS_LIST = [f"[{i.get_text(strip=True)}](https://archiveofourown.org{i.a['href']})" for i in MAINTAINERS_LIST_HTML]
            # If there's only one author
            AUTHOR = MAINTAINERS_LIST[0][MAINTAINERS_LIST[0].index('[')+1:MAINTAINERS_LIST[0].index(']')]
            AUTHOR_LINK = MAINTAINERS_LIST[0][MAINTAINERS_LIST[0].index('(')+1:MAINTAINERS_LIST[0].index(')')]

            try:
                CONTACT_HTML = MAINTAINERS_LIST_HTML[0].parent.parent.next_sibling.next_sibling
                CONTACT = CONTACT_HTML.next_sibling.next_sibling.get_text(strip=True)
            except:
                CONTACT = None

            # ++++++++++++++++++ PREFACE GROUP ++++++++++++++++++
            PREFACE_GROUP = soup.find('div', class_='preface group')
            try:
                INTROsoup = PREFACE_GROUP.find('div', {'id': 'intro'}).blockquote
                intro_var = str(INTROsoup).replace('<br/>', '<p>\r\n</p>')
                intro_var_edit = intro_var.replace('</p><p>', '</p><p>\r\n</p><p>')
                INTRO = BeautifulSoup(intro_var_edit, 'lxml').get_text()[1:-1]
            except:
                INTRO = None

            try:
                RULESsoup = PREFACE_GROUP.find('div', {'id': 'rules'}).blockquote
                rules_var = str(RULESsoup).replace('<br/>', '<p>\r\n</p>')
                rules_var_edit = rules_var.replace('</p><p>', '</p><p>\r\n</p><p>')
                RULES = BeautifulSoup(rules_var_edit, 'lxml').get_text()[1:-1]
            except:
                RULES = None

            return {
                'LINK_TYPE': 'COLLECTION',
                'STORY_TITLE_TEXT': STORY_TITLE_TEXT,
                'STORY_TITLE_LINK': STORY_TITLE_LINK,
                'IMAGE': IMAGE,
                'SUMMARY': SUMMARY,
                'STATUS': STATUS,
                'ACTIVE_SINCE': ACTIVE_SINCE,
                'MAINTAINERS_LIST' : MAINTAINERS_LIST,
                'AUTHOR': AUTHOR,
                'AUTHOR_LINK': AUTHOR_LINK,
                'CONTACT': CONTACT,
                'INTRO': INTRO,
                'RULES': RULES
            }

        except Exception as err:
            return f'Error with A03 Collections -> {err}'

    return "AO3 Error!"

if __name__ == '__main__':
    print(archive_of_our_own('https://archiveofourown.org/works/25069339/chapters/91671940'))
    print(archive_of_our_own('https://archiveofourown.org/series/1633756'))
