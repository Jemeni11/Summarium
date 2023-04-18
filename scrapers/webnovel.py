from pprint import pprint

import requests
from bs4 import BeautifulSoup


def webnovel(url: str):
	global csrf_token
	if "_" in url:
		STORY_ID = url.split("_")[-1]
	else:
		STORY_ID = url.split("/")[-1]
	web_novel_url = f"https://www.webnovel.com/book/{STORY_ID}"
	headers = {
		"User-Agent": "Mozilla / 5.0 (X11; Ubuntu; Linux x86_64; rv: 102.0) Gecko / 20100101 Firefox / 102.0"
	}
	scraper = requests.Session()
	try:
		response = scraper.get(web_novel_url, headers=headers)
	except:
		response = scraper.get(url, headers=headers)

	if "_csrfToken" in response.cookies.keys():
		csrf_token = response.cookies["_csrfToken"]

	soup = BeautifulSoup(response.text, "lxml")

	if not soup.title.get_text(strip=True) == "404 - Webnovel - Your Fictional Stories Hub":
		PAGE = soup.find_all('div', class_="page")[0]
		info_header = PAGE.find_all('div', class_="det-info g_row c_000 fs16 pr")[0]

		COVER_IMAGE = info_header.find_all('img')[0]['src']
		if COVER_IMAGE.startswith('//'):
			COVER_IMAGE = f"http:{COVER_IMAGE}"

		info_div = info_header.find_all('div', class_="_mn g_col _8 pr")[0]
		STORY_TITLE = info_div.h1.contents[0].strip()
		mini_info_div = [i.get_text(strip=True) for i in info_div.h2.contents if i.get_text() != ' ']
		GENRE = mini_info_div[0]
		CHAPTERS = mini_info_div[1]
		VIEWS = mini_info_div[2]
		AUTHOR = info_div.address.get_text(strip=True)[7:]
		AUTHOR_URL = f"https://www.webnovel.com{info_div.address.a['href']}"

		AUTHOR_response = scraper.get(AUTHOR_URL, headers=headers)
		AUTHOR_SOUP = BeautifulSoup(AUTHOR_response.text, "lxml").body
		AUTHOR_PAGE = AUTHOR_SOUP.find_all('div', {'class': 'avatar-area mb32 pr', 'data-id': '0'})[0]
		AUTHOR_IMAGE = f"https:{AUTHOR_PAGE.img['src']}"

		RATINGS = info_div.find_all('p', class_="_score ell mb24 fs0")[0].get_text(strip=True)
		RATINGS_FINAL = ''
		for i in RATINGS:
			RATINGS_FINAL += f' / 5 stars {i}' if i == '(' else i

		about_div = PAGE.find('div', {'id': 'about'})

		try:
			SYNOPSISVar = about_div.find('div', class_="g_txt_over mb48 fs16 j_synopsis")
			SYNOPSISVar = str(SYNOPSISVar).replace('\r', '\r\n')
			SYNOPSISVar = str(SYNOPSISVar).replace('<br/>', '\r\n')
			SYNOPSISVar = str(SYNOPSISVar).replace('</p><p>', '</p><p>\r\n</p><p>')
			SYNOPSIS = BeautifulSoup(SYNOPSISVar, 'lxml').get_text()
		except:
			SYNOPSIS = about_div.find('div', class_="g_txt_over mb48 fs16 j_synopsis").get_text(strip=True)

		TAGS_LIST = about_div.find_all('div', class_="j_tagWrap")[0].find('div', class_="m-tags").contents
		TAGS = [i.get_text(strip=True)[2:] for i in TAGS_LIST if i.get_text() != ' ']

		try:
			payload = {'_csrfToken': f'{csrf_token}', 'bookId': f'{STORY_ID}', 'bookType': 2, 'novelType': 0}
			random_variable = "https://www.webnovel.com/go/pcm/powerStone/getRankInfoAjax"
			# RANKING = about_div.find('div', class_="fl fs0 mr24 pt8 pb8 power-rank").strong.get_text(strip=True)
			RANKING = scraper.get(random_variable, headers=headers, params=payload).json()["data"]["rank"]
			if RANKING == -1:
				RANKING = "N/A"
		except:
			RANKING = None

		return {
			'STORY_TITLE': STORY_TITLE,
			'GENRE': GENRE,
			'CHAPTERS': CHAPTERS,
			'VIEWS': VIEWS,
			'COVER_IMAGE': COVER_IMAGE,
			'AUTHOR': AUTHOR,
			'AUTHOR_PROFILE_LINK': AUTHOR_URL,
			'AUTHOR_IMAGE': AUTHOR_IMAGE,
			'RATINGS': RATINGS_FINAL,
			'SYNOPSIS': SYNOPSIS,
			'TAGS': TAGS,
			'RANKING': RANKING
		}

	else:
		return "Error"
