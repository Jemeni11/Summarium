import requests
from bs4 import BeautifulSoup
from datetime import datetime


def fictiondotlive(url: str):
	STORY_ID = url.split("/")[5]

	response = requests.get(f'https://fiction.live/api/node/{STORY_ID}').json()

	TITLE = response['t'][:-4] if '<br>' == response['t'][-4:] else response['t']
	AUTHOR = response['u'][0]['n']

	if not 'a' in response['u'][0].keys():
		AUTHOR_IMAGE = 'https://ddx5i92cqts4o.cloudfront.net/images/1e1nvq5tm_fllogo.png'
	else:
		AUTHOR_IMAGE = response['u'][0]['a']

	AUTHOR_LINK = f"https://fiction.live/user/{AUTHOR}"
	STORY_STATUS = None if 'storyStatus' not in response.keys() else response['storyStatus']
	CONTENT_RATING = None if 'contentRating' not in response.keys() else response['contentRating']
	if CONTENT_RATING == 'nsfw':
		CONTENT_RATING = 'NSFW'

	if 'i' not in response.keys():
		COVER_IMAGE = 'https://ddx5i92cqts4o.cloudfront.net/images/1e1nvq5tm_fllogo.png'
	else:
		COVER_IMAGE = response['i'][0]

	AUTHOR_NOTE = ' ' if 'd' not in response.keys() else response['d']
	AUTHOR_NOTEVar = str(AUTHOR_NOTE).replace('<br>', '\r\n')
	AUTHOR_NOTEVar2 = str(AUTHOR_NOTEVar).replace('</p><p>', '</p><p>\r\n</p><p>')
	AUTHOR_NOTE = BeautifulSoup(AUTHOR_NOTEVar2, 'lxml').get_text()

	DESCRIPTION = ' ' if 'b' not in response.keys() else response['b']
	DESCRIPTIONVar = str(DESCRIPTION).replace('<br>', '\r\n')
	DESCRIPTIONVar2 = str(DESCRIPTIONVar).replace('</p><p>', '</p><p>\r\n</p><p>')
	DESCRIPTION = BeautifulSoup(DESCRIPTIONVar2, 'lxml').get_text()

	TAGS = ' ' if 'ta' not in response.keys() else response['ta']
	NOS_OF_CHAPTERS = ' ' if 'bm' not in response.keys() else f"{len(response['bm']):,}"
	NOS_OF_WORDS = ' ' if 'w' not in response.keys() else f"{response['w']:,}"

	if 'cht' not in response.keys():
		UPDATED = ' '
	else:
		UPDATED = str(datetime.fromtimestamp(response['cht'] / 1000.0, None))[:10]

	if 'rt' not in response.keys():
		PUBLISHED = ' '
	else:
		PUBLISHED = str(datetime.fromtimestamp(response['rt'] / 1000.0, None))[:10]

	return {
		'TITLE': TITLE,
		'AUTHOR': AUTHOR,
		'AUTHOR_IMAGE': AUTHOR_IMAGE,
		'AUTHOR_LINK': AUTHOR_LINK,
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
