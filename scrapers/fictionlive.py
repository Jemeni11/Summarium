import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fictiondotlive(url: str):
  STORY_ID =  url.split("/")[5]

  response = requests.get(f'https://fiction.live/api/node/{STORY_ID}').json()

  TITLE = response['t'][:-4] if '<br>' == response['t'][-4:] else response['t']
  AUTHOR = response['u'][0]['n']
  
  if not 'a' in response['u'][0].keys():
    AUTHOR_IMAGE = None
  else:
    AUTHOR_IMAGE = response['u'][0]['a']
  
  AUTHOR_LINK = f"https://fiction.live/user/{AUTHOR}"
  STORY_STATUS = None if not 'storyStatus' in response.keys() else response['storyStatus']
  CONTENT_RATING = None if not 'contentRating' in response.keys() else response['contentRating']

  if not 'i' in response.keys():
    COVER_IMAGE = None
  else:
    COVER_IMAGE = response['i'][0]
  
  AUTHOR_NOTE = ' ' if not 'd' in response.keys() else response['d']
  AUTHOR_NOTEVar = str(AUTHOR_NOTE).replace('<br>', '\r\n')
  AUTHOR_NOTEVar2 = str(AUTHOR_NOTEVar).replace('</p><p>', '</p><p>\r\n</p><p>')
  AUTHOR_NOTE = BeautifulSoup(AUTHOR_NOTEVar2, 'lxml').get_text()

  DESCRIPTION = ' ' if not 'b' in response.keys() else response['b']
  DESCRIPTIONVar = str(DESCRIPTION).replace('<br>', '\r\n')
  DESCRIPTIONVar2 = str(DESCRIPTIONVar).replace('</p><p>', '</p><p>\r\n</p><p>')
  DESCRIPTION = BeautifulSoup(DESCRIPTIONVar2, 'lxml').get_text()

  TAGS = ' ' if not 'ta' in response.keys() else response['ta']
  NOS_OF_CHAPTERS = ' ' if not 'bm' in response.keys() else f"{len(response['bm']):,}"
  NOS_OF_WORDS = ' ' if not 'w' in response.keys() else f"{response['w']:,}"

  if not 'cht' in response.keys():
    UPDATED = ' '
  else:
    UPDATED = str(datetime.fromtimestamp(response['cht'] / 1000.0, None))[:10]
  
  if not 'rt' in response.keys():
    PUBLISHED = ' '
  else:
    PUBLISHED = str(datetime.fromtimestamp(response['rt'] / 1000.0, None))[:10]

  return {
    'TITLE': TITLE, 
    'AUTHOR': AUTHOR,
    'AUTHOR_IMAGE':AUTHOR_IMAGE,
    'AUTHOR_LINK':AUTHOR_LINK,
    'STORY_STATUS': STORY_STATUS,
    'CONTENT_RATING': CONTENT_RATING,
    'COVER_IMAGE': COVER_IMAGE,
    'AUTHOR_NOTE': AUTHOR_NOTE,
    'DESCRIPTION': DESCRIPTION,
    'TAGS': TAGS,
    'NOS_OF_CHAPTERS': NOS_OF_CHAPTERS,
    'NOS_OF_WORDS': NOS_OF_WORDS,
    'UPDATED': UPDATED,
    'PUBLISHED': PUBLISHED
  }
