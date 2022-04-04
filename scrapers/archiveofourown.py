import requests
from bs4 import BeautifulSoup

def archive_of_our_own(url: str):
    try:
    # URL Cleaning
        if 'https://archiveofourown.org/works/' in soup:
        # https://archiveofourown.org/works/35158198/chapters/88291957?view_adult=true
            new_url = f'https://www.scribblehub.com/series/{int()}'  # Incomplete
            url = new_url
        elif url[-16:] != '?view_adult=true':
            url += '?view_adult=true'

        webPage = requests.get(url)
        soup = BeautifulSoup(webPage.text.encode('unicode-escape').decode('utf-8'), "html.parser")

        # RATING = soup.find('dd', class_='rating tags').get_text(strip=True)[4:-4]
        RATING = soup.find('dd', class_='rating tags').get_text(strip=True).replace(r'\n', '')
        # ARCHIVE_WARNING = ' '.join(_.get_text(strip=True) for _ in soup.find('dd', class_='warning tags').contents)
        # ARCHIVE_WARNING = ' '.join(soup.find('dd', class_='warning tags').contents[1].text.split())[3:-2]
        ARCHIVE_WARNING = ' '.join(soup.find('dd', class_='warning tags').contents[1].text.split()).replace(r'\n', '').lstrip()
        CATEGORY = ''.join(soup.find('dd', class_='category tags').text.split()).replace(r'\n', '')
        FANDOM = soup.find('dd', class_='fandom tags').contents[1].text.replace(r'\n', '').strip()
        RELATIONSHIPS = ' '.join(_.get_text() for _ in soup.find('dd', class_='relationship tags').contents)
        CHARACTERS = ' '.join(_.get_text() for _ in soup.find('dd', class_='character tags').contents)
        ADDITIONAL_TAGS = ' '.join(_.get_text() for _ in soup.find('dd', class_='freeform tags').contents)
        LANGUAGE = soup.find('dd', class_='language').stripped_strings
        SERIES = ''
        STATS = ''.join(_.get_text() for _ in soup.find('dd', class_='stats').contents)

        TITLE = soup.find('h2', class_='title heading').stripped_strings
        AUTHOR = soup.find('a', {'rel': 'author'}).stripped_strings
        AUTHOR_LINK = soup.find('a', {'rel': 'author'})['href']

        """
            date_updated.append(article.find('p', {'class':'datetime'}).text)
            ratings.append(article.find('span', {'class':re.compile(r'rating\-.*rating')}).text)
            pairings.append(article.find('span', {'class':re.compile(r'category\-.*category')}).text)
            warnings.append(article.find('span', {'class':re.compile(r'warning\-.*warnings')}).text)
            complete.append(article.find('span', {'class':re.compile(r'complete\-.*iswip')}).text)
            languages.append(article.find('dd', {'class':'language'}).text)
            count = article.find('dd', {'class':'words'}).text
            if len(count) > 0:
                word_count.append(count)
            else:
                word_count.append('0')
            chapters.append(article.find('dd', {'class':'chapters'}).text.split('/')[0])
            try:
                comments.append(article.find('dd', {'class':'comments'}).text)
            except:
                comments.append('0')
            try:
                kudos.append(article.find('dd', {'class':'kudos'}).text)
            except:
                kudos.append('0')
            try:
                bookmarks.append(article.find('dd', {'class':'bookmarks'}).text)
            except:
                bookmarks.append('0')
            try:
                hits.append(article.find('dd', {'class':'hits'}).text)
            except:
                hits.append('0')
        """

        # return {
        #     'Rating': RATING,
        #     'Archive Warning': ARCHIVE_WARNING,
        #     'Category': CATEGORY,
        #     'Fandom': FANDOM,
        #     'Relationships': RELATIONSHIPS,
        #     'Characters': CHARACTERS,
        #     'Additional Tags': ADDITIONAL_TAGS,
        #     'Language': LANGUAGE,
        #     'Stats': STATS,
        #     'Title': TITLE,
        #     'Author': AUTHOR,
        #     'Author Link': AUTHOR_LINK
        #     }
        # return ARCHIVE_WARNING
        # return ' '.join(_.get_text() for _ in soup.find('dd', class_='fandom tags').contents)
        # return ''.join(_.text for _ in soup.find('dd', class_='relationship tags').children)
        return ''.join(f"{_}\n" for _ in soup.find('dd', class_='relationship tags').contents)

    except Exception as err:
        return f'Error -> {err}'