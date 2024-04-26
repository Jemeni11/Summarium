import pprint  # For testing
import typing
import requests
from bs4 import BeautifulSoup
import re


class ArchiveOfOurOwn:
    def __init__(self, URL: str) -> None:
        self.URL = URL
        if re.search(
            r"^https://archiveofourown\.org/works/\d+", self.URL, re.IGNORECASE
        ) or re.search(
            r"^https://archiveofourown\.org/collections/\w+/\bworks\b/\d+",
            self.URL,
            re.IGNORECASE,
        ):
            url_list = self.URL.split("/")
            if self.URL.startswith("https://archiveofourown.org/works/"):
                self.URL = f"https://archiveofourown.org/works/{url_list[4]}?view_full_work=true&view_adult=true"
            else:
                # view_full_work=true might be unnecessary, but I'll leave it here anyway.
                self.URL = f"https://archiveofourown.org/collections/{url_list[4]}/works/{url_list[6]}?view_full_work=true&view_adult=true"
        elif re.search(
            r"^https://archiveofourown\.org/series/\d+", self.URL, re.IGNORECASE
        ):
            pass
        elif re.search(
            r"^https://archiveofourown\.org/collections/\w+", self.URL, re.IGNORECASE
        ):
            if self.URL.split("/")[-1] != "profile":
                self.URL += "/profile"

        self.scraper = requests.Session()
        webPage = self.scraper.get(self.URL)
        self.soup = BeautifulSoup(webPage.text, "lxml")

    def chunker(self, seq, size) -> list:
        return [seq[pos : pos + size] for pos in range(0, len(seq), size)]

    def A03Story(self) -> typing.Union[dict, str]:
        """
        \nTags:
            Tags are comma separated, 100 characters per tag. Fandom,
            relationship, character, and additional tags must not add
            up to more than 75. Archive warning, category, and rating
            tags do not count toward this limit.
            - Rating*
            - Archive Warnings*
            - Fandoms*
            - Categories
            - Relationships
            - Characters
            - Additional Tags
        \nPreface:
            - Work Title* [255 characters]
            - Add co-creators?
            - Summary [1250 characters]
            - Notes
        \nAssociation:
            - Post to Collections/Challenges
            - Gift this work to
            - This work is part of a series?
            - Choose a language*
            - Select Work Skin
        \nPrivacy:
            - Who can comment on this work
        \nWork Text:
            - [500000 characters ]
        """

        try:
            if self.soup.title.getText(strip=True).startswith("Mystery Work"):
                MYSTERY_DESCRIPTION = self.soup.find("div", {"id": "main"}).find_all(
                    "p", class_="notice"
                )[0]
                MYSTERY_WORK_DETAILS_LINK = (
                    f"https://archiveofourown.org{MYSTERY_DESCRIPTION.a['href']}"
                )
                DESCRIPTION_TEXT = str(MYSTERY_DESCRIPTION).replace(
                    f"{MYSTERY_DESCRIPTION.a}",
                    f"[{MYSTERY_DESCRIPTION.get_text(strip=True).split(':')[1]}]({MYSTERY_WORK_DETAILS_LINK})",
                )
                FINAL_DESCRIPTION = BeautifulSoup(DESCRIPTION_TEXT, "lxml").get_text(
                    strip=True
                )
                FINAL_DESCRIPTION = FINAL_DESCRIPTION.replace("      ", "")
                return {
                    "TYPE": "MYSTERY_WORK",
                    "EMBED_TITLE": "Mystery Work",
                    "DESCRIPTION": FINAL_DESCRIPTION,
                }
            elif (
                self.soup.title.getText(strip=True)
                == "New\n          Session\n        |\n        Archive of Our Own"
            ):
                return {
                    "TYPE": "LOGIN_REQUIRED",
                    "EMBED_TITLE": "Login Required",
                    "DESCRIPTION": "This work needs you need to login",
                }
            else:
                # ===============TAGS
                RATING = self.soup.find("dd", class_="rating tags").get_text(strip=True)

                ARCHIVE_WARNING_LIST = [
                    _.get_text(strip=True)
                    for _ in self.soup.find("dd", class_="warning tags").contents[1]
                ]
                ARCHIVE_WARNING = ", ".join(ARCHIVE_WARNING_LIST)[2:-2]

                FANDOM_LIST = [
                    i.get_text()
                    for i in self.soup.find("dd", class_="fandom tags").contents[1]
                ]
                FANDOM = ", ".join(FANDOM_LIST)[3:-3]

                relationshipExists = self.soup.find("dd", class_="relationship tags")
                if relationshipExists:
                    RELATIONSHIPS = [
                        _.get_text() for _ in relationshipExists.contents[1]
                    ]
                else:
                    RELATIONSHIPS = "N/A"

                charactersExists = self.soup.find("dd", class_="character tags")
                if charactersExists:
                    CHARACTERS = [_.get_text() for _ in charactersExists.contents[1]]
                else:
                    CHARACTERS = "N/A"

                # ===============PREFACE
                TITLE = self.soup.find("h2", class_="title heading").get_text(
                    strip=True
                )

                summary_module_container = self.soup.find(
                    "div", class_="summary module"
                )
                try:
                    summaryVar = summary_module_container.find(
                        "blockquote", class_="userstuff"
                    )
                    summaryVar = str(summaryVar).replace("<br/>", "\r\n")
                    summaryVar = str(summaryVar).replace(
                        "</p><p>", "</p><p>\r\n</p><p>"
                    )
                    SUMMARY = BeautifulSoup(summaryVar, "lxml").get_text()
                except:
                    SUMMARY = summary_module_container.find(
                        "blockquote", class_="userstuff"
                    ).get_text(strip=True)

                # ===============ASSOCIATION
                SERIES_LIST = []
                for i in self.soup.find_all("span", class_="series"):
                    SERIES_LIST.extend(
                        [
                            f"[{_.get_text()}](https://archiveofourown.org{_['href']})"
                            for _ in i.find_all("a", class_=None)
                        ]
                    )
                # For some weird reason, I was getting duplicate results
                # so turning it into a set first then turning it into
                # a list handles that
                SERIES = list(set(SERIES_LIST))

                LANGUAGE = self.soup.find("dd", class_="language").get_text(strip=True)

                # ===============EXTRAS
                STATS_SOUP = self.soup.find("dl", class_="stats")
                STATS_LIST = []
                Stats_that_need_a_comma = [
                    "Words:",
                    "Comments:",
                    "Kudos:",
                    "Bookmarks:",
                    "Hits:",
                ]
                for group in self.chunker(STATS_SOUP.contents, 2):
                    new_group = [group[0].get_text(), group[1].get_text()]
                    i, j = new_group
                    if i[-1] == ":":
                        STATS_LIST.append(i)
                        if i in Stats_that_need_a_comma:
                            try:
                                STATS_LIST.append(f"{int(j):,} •")
                            except ValueError:
                                STATS_LIST.append(f"{int(j.replace(',', '')):,} •")
                        else:
                            STATS_LIST.append(f"{j} •")
                try:
                    # Remove Comments
                    STATS_LIST.remove(STATS_LIST[STATS_LIST.index("Comments:") + 1])
                    STATS_LIST.remove("Comments:")
                except:
                    pass
                STATS = " ".join(STATS_LIST)[:-2]

                """
				AUTHOR_LIST = Gets all the authors in one list. There will always be at least one author #TODO Test orphan accounts
				AUTHOR = Gets the first author in AUTHOR_LIST. This is used when there's only one author.
				AUTHOR_LINK = The link leading to the AUTHOR'S profile page.
				AUTHOR_IMAGE_SOUP = This uses AUTHOR_LINK to get the AUTHOR's Profile Image.
				"""
                AUTHOR_SOUP = self.soup.find("h3", class_="byline heading")
                if "<a href" in str(AUTHOR_SOUP):
                    AUTHOR_LIST = [
                        f"[{i.get_text()}](https://archiveofourown.org{i['href']})"
                        for i in AUTHOR_SOUP.contents
                        if i not in ["\n", ", "]
                    ]

                    # AUTHOR & AUTHOR_LIST are only used when there's one author.
                    AUTHOR = AUTHOR_LIST[0][
                        AUTHOR_LIST[0].index("[") + 1 : AUTHOR_LIST[0].index("]")
                    ]
                    AUTHOR_LINK = AUTHOR_LIST[0][
                        AUTHOR_LIST[0].rindex("(") + 1 : AUTHOR_LIST[0].rindex(")")
                    ]

                elif AUTHOR_SOUP.get_text(strip=True) == "Anonymous":
                    AUTHOR = "Anonymous"
                    AUTHOR_LINK = (
                        "https://archiveofourown.org/collections/anonymous/profile"
                    )
                    AUTHOR_LIST = [
                        "[Anonymous](https://archiveofourown.org/collections/anonymous/profile)"
                    ]

                AUTHOR_IMAGE_SOUP = BeautifulSoup(
                    self.scraper.get(AUTHOR_LINK).text, "lxml"
                ).find("div", class_="primary header module")
                AUTHOR_IMAGE = AUTHOR_IMAGE_SOUP.find(class_="icon").img["src"]
                AUTHOR_IMAGE_LINK = (
                    AUTHOR_IMAGE
                    if AUTHOR_IMAGE.startswith("https://")
                    else f"https://archiveofourown.org{AUTHOR_IMAGE}"
                )

                return {
                    "TYPE": "STORY",
                    "RATING": RATING,
                    "ARCHIVE_WARNING": ARCHIVE_WARNING,
                    "ARCHIVE_WARNING_LIST": ARCHIVE_WARNING_LIST,
                    "FANDOM": FANDOM,
                    "CHARACTERS": CHARACTERS,
                    "RELATIONSHIPS": RELATIONSHIPS,
                    "TITLE": TITLE,
                    "SUMMARY": SUMMARY,
                    "SERIES": SERIES,
                    "LANGUAGE": LANGUAGE,
                    "STATS": STATS,
                    "AUTHOR": AUTHOR,
                    "AUTHOR_LINK": AUTHOR_LINK,
                    "AUTHOR_LIST": AUTHOR_LIST,
                    "AUTHOR_IMAGE_LINK": AUTHOR_IMAGE_LINK,
                }

        except Exception as err:
            return f"Error with A03 Story -> {err}"

    def A03Series(self) -> typing.Union[dict, str]:
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
            SERIES_DATA = self.soup.find("dl", class_="series meta group")

            SERIES_TITLE = self.soup.find("h2", class_="heading").get_text(strip=True)

            AUTHOR_LIST = [
                f"[{i.get_text()}](https://archiveofourown.org{i['href']})"
                for i in SERIES_DATA.dd
                if i not in ["\n", ", "]
            ]

            # AUTHOR & AUTHOR_LINK are only used when there's one author.
            AUTHOR = AUTHOR_LIST[0][
                AUTHOR_LIST[0].index("[") + 1 : AUTHOR_LIST[0].index("]")
            ]
            AUTHOR_LINK = AUTHOR_LIST[0][
                AUTHOR_LIST[0].rindex("(") + 1 : AUTHOR_LIST[0].rindex(")")
            ]

            AUTHOR_IMAGE_SOUP = BeautifulSoup(
                self.scraper.get(AUTHOR_LINK).text, "lxml"
            ).find("div", class_="primary header module")
            AUTHOR_IMAGE = [i for i in AUTHOR_IMAGE_SOUP.contents if i != "\n"][
                1
            ].a.img["src"]
            AUTHOR_IMAGE_LINK = (
                AUTHOR_IMAGE
                if AUTHOR_IMAGE.startswith("https://")
                else f"https://archiveofourown.org{AUTHOR_IMAGE}"
            )

            SERIES_BEGUN = "".join(
                i.next_sibling.next_sibling.get_text()
                for i in SERIES_DATA.find_all("dt", string="Series Begun:")
            )
            SERIES_UPDATED = "".join(
                i.next_sibling.next_sibling.get_text()
                for i in SERIES_DATA.find_all("dt", string="Series Updated:")
            )

            # Stats: [Words: Works: Complete: Bookmarks:]
            Stats_text = ""
            statsArr = [
                i.get_text(strip=True)
                for i in SERIES_DATA.find_all("dt", string="Stats:")[
                    0
                ].next_sibling.next_sibling.dl
            ][1:-1]
            for group in self.chunker(statsArr, 4):
                Stats_text += f"{' '.join(group)} • "
            STATS = Stats_text[:-2]

            try:
                descriptionVar = SERIES_DATA.find_all("dt", string="Description:")[
                    0
                ].next_sibling.next_sibling.blockquote
                descriptionVar = str(descriptionVar).replace("<br/>", "\r\n")
                descriptionVar = str(descriptionVar).replace(
                    "</p><p>", "</p><p>\r\n</p><p>"
                )
                DESCRIPTION = BeautifulSoup(descriptionVar, "lxml").get_text()
            except:
                DESCRIPTION = None

            try:
                notesVar = SERIES_DATA.find_all("dt", string="Notes:")[
                    0
                ].next_sibling.next_sibling.blockquote
                notesVar = str(notesVar).replace("<br/>", "\r\n")
                notesVar = str(notesVar).replace("</p><p>", "</p><p>\r\n</p><p>")
                NOTES = BeautifulSoup(notesVar, "lxml").get_text()
            except:
                NOTES = None

            # WORKS
            try:
                MAIN_DIV = self.soup.find("div", {"id": "main"})
                WORK_LIST = MAIN_DIV.find(
                    "ul", class_="series work index group"
                ).contents
                WORKS = []
                for i in WORK_LIST:
                    if i.find("a") != -1:
                        WORKS.append(
                            f"[{i.find('a').text}](https://archiveofourown.org{i.find('a')['href']})"
                        )
            except:
                WORKS = "N/A"

            pprint.pprint(
                {
                    "SERIES_TITLE": SERIES_TITLE,
                    "AUTHOR": AUTHOR,
                    "AUTHOR_LINK": AUTHOR_LINK,
                    "AUTHOR_LIST": AUTHOR_LIST,
                    "AUTHOR_IMAGE_LINK": AUTHOR_IMAGE_LINK,
                    "SERIES_BEGUN": SERIES_BEGUN,
                    "SERIES_UPDATED": SERIES_UPDATED,
                    "DESCRIPTION": DESCRIPTION,
                    "NOTES": NOTES,
                    "STATS": STATS,
                    "WORKS": WORKS,
                }
            )

            return {
                "SERIES_TITLE": SERIES_TITLE,
                "AUTHOR": AUTHOR,
                "AUTHOR_LINK": AUTHOR_LINK,
                "AUTHOR_LIST": AUTHOR_LIST,
                "AUTHOR_IMAGE_LINK": AUTHOR_IMAGE_LINK,
                "SERIES_BEGUN": SERIES_BEGUN,
                "SERIES_UPDATED": SERIES_UPDATED,
                "DESCRIPTION": DESCRIPTION,
                "NOTES": NOTES,
                "STATS": STATS,
                "WORKS": WORKS,
            }

        except Exception as err:
            return f"Error with A03 Series -> {err}"

    def AO3Collection(self) -> typing.Union[dict, str]:
        try:
            # ++++++++++++++++++ HEADING ++++++++++++++++++
            HEADING = self.soup.find("div", class_="primary header module")

            STORY_TITLE = HEADING.find("h2", class_="heading")
            STORY_TITLE_TEXT = STORY_TITLE.get_text(strip=True)
            STORY_TITLE_LINK = (
                f"https://archiveofourown.org{STORY_TITLE.find('a')['href']}"
            )

            IMAGE_LINK = HEADING.find("div", class_="icon").img["src"]
            IMAGE = (
                IMAGE_LINK
                if IMAGE_LINK.startswith("https://")
                else f"https://archiveofourown.org{IMAGE_LINK}"
            )

            try:
                summaryVar = HEADING.find("blockquote", class_="userstuff")
                summaryVar = str(summaryVar).replace("<br/>", "\r\n")
                summaryVar = str(summaryVar).replace("</p><p>", "</p><p>\r\n</p><p>")
                SUMMARY = BeautifulSoup(summaryVar, "lxml").get_text()
            except:
                SUMMARY = HEADING.find("blockquote", class_="userstuff").get_text(
                    strip=True
                )

            STATUS = HEADING.find("p", class_="type").get_text(strip=True)

            # ++++++++++++++++++ WRAPPER ++++++++++++++++++
            WRAPPER = self.soup.find("dl", class_="meta group")

            ACTIVE_SINCE = WRAPPER.dt.next_sibling.get_text(strip=True)

            MAINTAINERS_LIST_HTML = [
                i
                for i in WRAPPER.find("ul", class_="mods commas")
                if i not in ["\n", ", "]
            ]
            MAINTAINERS_LIST = [
                f"[{i.get_text(strip=True)}](https://archiveofourown.org{i.a['href']})"
                for i in MAINTAINERS_LIST_HTML
            ]
            # If there's only one author
            AUTHOR = MAINTAINERS_LIST[0][
                MAINTAINERS_LIST[0].index("[") + 1 : MAINTAINERS_LIST[0].index("]")
            ]
            AUTHOR_LINK = MAINTAINERS_LIST[0][
                MAINTAINERS_LIST[0].rindex("(") + 1 : MAINTAINERS_LIST[0].rindex(")")
            ]

            try:
                CONTACT_HTML = MAINTAINERS_LIST_HTML[
                    0
                ].parent.parent.next_sibling.next_sibling
                CONTACT = CONTACT_HTML.next_sibling.next_sibling.get_text(strip=True)
            except:
                CONTACT = None

            # ++++++++++++++++++ PREFACE GROUP ++++++++++++++++++
            PREFACE_GROUP = self.soup.find("div", class_="preface group")
            try:
                INTROsoup = PREFACE_GROUP.find("div", {"id": "intro"}).blockquote
                intro_var = str(INTROsoup).replace("<br/>", "<p>\r\n</p>")
                intro_var_edit = intro_var.replace("</p><p>", "</p><p>\r\n</p><p>")
                INTRO = BeautifulSoup(intro_var_edit, "lxml").get_text()[1:-1]
            except:
                INTRO = None

            try:
                RULESsoup = PREFACE_GROUP.find("div", {"id": "rules"}).blockquote
                rules_var = str(RULESsoup).replace("<br/>", "<p>\r\n</p>")
                rules_var_edit = rules_var.replace("</p><p>", "</p><p>\r\n</p><p>")
                RULES = BeautifulSoup(rules_var_edit, "lxml").get_text()[1:-1]
            except:
                RULES = None

            return {
                "STORY_TITLE_TEXT": STORY_TITLE_TEXT,
                "STORY_TITLE_LINK": STORY_TITLE_LINK,
                "IMAGE": IMAGE,
                "SUMMARY": SUMMARY,
                "STATUS": STATUS,
                "ACTIVE_SINCE": ACTIVE_SINCE,
                "MAINTAINERS_LIST": MAINTAINERS_LIST,
                "AUTHOR": AUTHOR,
                "AUTHOR_LINK": AUTHOR_LINK,
                "CONTACT": CONTACT,
                "INTRO": INTRO,
                "RULES": RULES,
            }

        except Exception as err:
            return f"Error with A03 Collection -> {err}"
