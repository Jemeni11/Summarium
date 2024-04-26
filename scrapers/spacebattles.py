from bs4 import BeautifulSoup
import re
import requests
import pprint


class SpaceBattles:
    def __init__(self, URL: str) -> None:
        self.URL = URL

        # Example input
        # https://forums.spacebattles.com/threads/luminous-star-wars-si.1037538/reader/
        # https://forums.spacebattles.com/threads/luminous-star-wars-si.1037538/page-7#post-87760270

        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, "
            "like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36",
        }
        # 	([a-zA-Z0-9#-/]+)*
        m = re.search(
            r"^https?://forums?\.spacebattles\.com/threads/(([a-zA-Z%0-9]+-*)+\.[0-9]+)/?",
            self.URL,
            re.I,
        )
        newURL = f"https://forums.spacebattles.com/threads/{m.group(1)}/reader/"

        self.scraper = requests.Session()
        webPage = self.scraper.get(newURL, headers=headers)
        self.soup = BeautifulSoup(webPage.text, "lxml")

    def SBWork(self) -> dict:
        """
        STORY_TITLE,
        AUTHOR,
        AUTHOR_PROFILE_LINK,
        AUTHOR_AVATAR_LINK,
        CREATED_ON,
        TAGS,
        STORY_STATUS,
        WATCHERS,
        RECENT_READERS,
        THREADMARKS,
        DESCRIPTION,
        WORDS,
        LAST_UPDATED,
        IS_FETCHED
        """
        IS_FETCHED = False
        BODY = self.soup.find("div", class_="p-body").find("div", class_="p-body-inner")

        HEADER = BODY.find("div", class_="p-body-header")
        BODY_CONTENT = BODY.find("div", class_="p-body-content").find(
            "div", class_="p-body-pageContent"
        )
        BODY_CONTENT_BLOCK_ONE = BODY_CONTENT.find_all("div", class_="block")[0]
        BODY_CONTENT_BLOCK_TWO = BODY_CONTENT.find_all("div", class_="block")[1]
        BODY_CONTENT_BLOCK_THREE = BODY_CONTENT.find_all("div", class_="block")[2]

        try:
            COVER_IMAGE = f"https://forums.spacebattles.com{BODY.find('span', class_='threadmarkListingHeader-icon').span.img['src']}"
        except Exception as _e:
            COVER_IMAGE = "https://forums.spacebattles.com/data/svg/2/1/1669334645/2022_favicon_192x192.png"

        DESCRIPTION_HEADER = HEADER.find("div", class_="p-description")

        STORY_TITLE = (
            HEADER.find("div", class_="p-title")
            .find("h1", class_="p-title-value")
            .get_text(strip=True)
        )
        AUTHOR = DESCRIPTION_HEADER.find_all("li")[0].a.get_text(strip=True)
        AUTHOR_PROFILE_LINK = f"https://forums.spacebattles.com{DESCRIPTION_HEADER.find_all('li')[0].a['href']}"
        CREATED_ON = DESCRIPTION_HEADER.find_all("li")[1].a.time.get_text(strip=True)
        TAGS = [
            i.get_text(strip=True)
            for i in DESCRIPTION_HEADER.find_all("li")[2].dl.dd.span.find_all("a")
        ]

        THREADMARK_HEADER_STATS = (
            BODY_CONTENT_BLOCK_ONE.find("div", class_="threadmarkListingHeader-stats")
            .find("div", class_="pairJustifier")
            .find_all("dl", class_="pairs")
        )

        STORY_STATUS = THREADMARK_HEADER_STATS[1].dd.get_text(strip=True)
        WATCHERS = THREADMARK_HEADER_STATS[2].dd.get_text(strip=True)
        RECENT_READERS = THREADMARK_HEADER_STATS[3].dd.get_text(strip=True)

        description_body = BODY_CONTENT_BLOCK_ONE.find(
            "div", class_="threadmarkListingHeader-extraInfo"
        )

        DESCRIPTION = description_body.find("div", class_="bbWrapper").get_text(
            strip=True
        )

        # try:
        # 	description_last_edited = description_body.find("dl", class_="message-lastEdit").get_text(strip=True)
        # except:
        # 	description_last_edited = None

        THREADMARKS = (
            BODY_CONTENT_BLOCK_TWO.find(
                "span", {"data-xf-init": "threadmarks-toggle-storage"}
            )
            .get_text(strip=True)
            .split(" ")[1][1:]
        )

        WORDS = (
            BODY_CONTENT_BLOCK_TWO.find(
                "span", {"data-xf-init": "threadmarks-toggle-storage"}
            )
            .get_text(strip=True)
            .split("threadmarks, ")[-1][:-1]
        )

        LAST_UPDATED = (
            BODY_CONTENT_BLOCK_TWO.find_all("div", class_="structItem--threadmark")[-1]
            .contents[-2]
            .get_text(strip=True)
        )

        AUTHOR_AVATAR_LINK = (
            BODY_CONTENT_BLOCK_THREE.find_all("article", class_="message")[0]
            .find("div", class_="message-cell--user")
            .find("img")["src"]
        )
        AUTHOR_AVATAR_LINK = f"https://forums.spacebattles.com{AUTHOR_AVATAR_LINK}"

        IS_FETCHED = True

        return {
            "STORY_TITLE": STORY_TITLE,
            "AUTHOR": AUTHOR,
            "AUTHOR_PROFILE_LINK": AUTHOR_PROFILE_LINK,
            "AUTHOR_AVATAR_LINK": AUTHOR_AVATAR_LINK,
            "COVER_IMAGE": COVER_IMAGE,
            "CREATED_ON": CREATED_ON,
            "TAGS": TAGS,
            "STORY_STATUS": STORY_STATUS,
            "WATCHERS": WATCHERS,
            "RECENT_READERS": RECENT_READERS,
            "THREADMARKS": THREADMARKS,
            "DESCRIPTION": DESCRIPTION,
            "WORDS": WORDS,
            "LAST_UPDATED": LAST_UPDATED,
            "IS_FETCHED": IS_FETCHED,
        }


if __name__ == "__main__":
    s = SpaceBattles(
        "https://forums.spacebattles.com/threads/a-grievous-monster-sw-si.1049660/reader"
    )
    pprint.pprint(s.SBWork())
