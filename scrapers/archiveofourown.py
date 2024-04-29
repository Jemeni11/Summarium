import pprint  # For testing
import requests
from bs4 import BeautifulSoup
from utils import process_list, trim_list_ends, pattern_matcher, trim_text


class ArchiveOfOurOwn:
    def __init__(self, url: str) -> None:
        self.URL = url
        if pattern_matcher(
            r"^https://archiveofourown\.org/works/\d+", self.URL
        ) or pattern_matcher(
            r"^https://archiveofourown\.org/collections/\w+/\bworks\b/\d+", self.URL
        ):
            url_list = self.URL.split("/")

            if self.URL.startswith("https://archiveofourown.org/works/"):
                self.URL = f"https://archiveofourown.org/works/{url_list[4]}?view_full_work=true&view_adult=true"

            else:
                # view_full_work=true might be unnecessary, but I'll leave it here anyway.
                self.URL = (
                    f"https://archiveofourown.org/collections/{url_list[4]}/works/{url_list[6]}?view_full_work"
                    f"=true&view_adult=true"
                )

        elif pattern_matcher(r"^https://archiveofourown\.org/series/\d+", self.URL):
            pass
        elif pattern_matcher(
            r"^https://archiveofourown\.org/collections/\w+", self.URL
        ):
            if self.URL.split("/")[-1] != "profile":
                self.URL += "/profile"

        self.scraper = requests.Session()
        web_page = self.scraper.get(self.URL)
        self.soup = BeautifulSoup(web_page.text, "lxml")

    @staticmethod
    def chunker(seq, size) -> list:
        return [seq[pos : pos + size] for pos in range(0, len(seq), size)]

    def ao3_story(self) -> dict:
        """
        \nTags:
            Tags are comma separated, 100 characters per tag. Fandom,
            relationship, character, and additional tags must not add
            up to more than 75. Archive warning, category, and rating
            tags do not count toward this limit.
            - Rating* e.g. Not Rated
            - Archive Warnings* e.g. Creator Chose Not To Use Archive Warnings
            - Fandoms* e.g. Marvel Cinematic Universe, Star Wars: The Clone Wars (2008)
            - Categories e.g. F/M
            - Relationships e.g. Peter Parker/Ahsoka Tano
            - Characters e.g. Peter Parker, Ahsoka Tano
            - Additional Tags e.g. Absolute Best
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
                mystery_description = self.soup.find("div", {"id": "main"}).find_all(
                    "p", class_="notice"
                )[0]
                mystery_work_details_link = (
                    f"https://archiveofourown.org{mystery_description.a['href']}"
                )
                description_text = str(mystery_description).replace(
                    f"{mystery_description.a}",
                    f"[{mystery_description.get_text(strip=True).split(':')[1]}]({mystery_work_details_link})",
                )
                final_description = (
                    BeautifulSoup(description_text, "lxml")
                    .get_text(strip=True)
                    .replace("      ", "")
                )

                return {
                    "TYPE": "MYSTERY_WORK",
                    "EMBED_TITLE": "Mystery Work",
                    "DESCRIPTION": trim_text(final_description),
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
                rating = self.soup.find("dd", class_="rating tags").get_text(strip=True)

                archive_warning_list = [
                    _.get_text(strip=True)
                    for _ in self.soup.find("dd", class_="warning tags").contents[1]
                ]
                archive_warning = ", ".join(archive_warning_list)[2:-2]

                fandom_list = [
                    i.get_text()
                    for i in self.soup.find("dd", class_="fandom tags").contents[1]
                ]
                fandom = ", ".join(fandom_list)[3:-3]

                relationship_exists = self.soup.find("dd", class_="relationship tags")
                if relationship_exists:
                    relationships_array = [
                        _.get_text() for _ in relationship_exists.contents[1]
                    ]
                    relationships_array_trimmed = trim_list_ends(relationships_array)
                    relationships = process_list(relationships_array_trimmed)
                else:
                    relationships = None

                characters_exists = self.soup.find("dd", class_="character tags")
                if characters_exists:
                    characters_array = [
                        _.get_text() for _ in characters_exists.contents[1]
                    ]
                    characters_array_trimmed = trim_list_ends(characters_array)
                    characters = process_list(characters_array_trimmed)
                else:
                    characters = None

                # ===============PREFACE
                title = self.soup.find("h2", class_="title heading").get_text(
                    strip=True
                )

                summary_module_container = self.soup.find(
                    "div", class_="summary module"
                )
                try:
                    summary_var = (
                        str(
                            summary_module_container.find(
                                "blockquote", class_="userstuff"
                            )
                        )
                        .replace("<br/>", "\r\n")
                        .replace("</p><p>", "</p><p>\r\n</p><p>")
                    )
                    summary = BeautifulSoup(summary_var, "lxml").get_text()
                except:
                    summary = summary_module_container.find(
                        "blockquote", class_="userstuff"
                    ).get_text(strip=True)

                # ===============ASSOCIATION
                series_list = []
                for i in self.soup.find_all("span", class_="series"):
                    series_list.extend(
                        [
                            f"[{_.get_text()}](https://archiveofourown.org{_['href']})"
                            for _ in i.find_all("a", class_=None)
                        ]
                    )
                # Using a dict to remove duplicates while preserving order
                series = list(dict.fromkeys(series_list))

                language = self.soup.find("dd", class_="language").get_text(strip=True)

                # ===============EXTRAS
                stats_soup = self.soup.find("dl", class_="stats")
                stats_list = []
                stats_that_need_a_comma = [
                    "Words:",
                    "Comments:",
                    "Kudos:",
                    "Bookmarks:",
                    "Hits:",
                ]
                for group in self.chunker(stats_soup.contents, 2):
                    new_group = [group[0].get_text(), group[1].get_text()]
                    i, j = new_group
                    if i[-1] == ":":
                        stats_list.append(i)
                        if i in stats_that_need_a_comma:
                            try:
                                stats_list.append(f"{int(j):,} •")
                            except ValueError:
                                stats_list.append(f"{int(j.replace(',', '')):,} •")
                        else:
                            stats_list.append(f"{j} •")
                # try:
                #     # Remove Comments
                #     stats_list.remove(stats_list[stats_list.index("Comments:") + 1])
                #     stats_list.remove("Comments:")
                # except:
                #     pass

                stats = " ".join(stats_list)[:-2]

                """
                author_list
                Gets all the authors in one list.
                There will always be at least one author
                #TODO Test orphan accounts
                
                author
                Gets the first author in author_list.
                This is used when there's only one author.
                
                author_link
                The link leading to the author's profile page.

                author_image_soup
                This uses author_link to get the author's Profile Image.
                """

                author_soup = self.soup.find("h3", class_="byline heading")
                author = ""
                author_link = ""
                author_list = []

                if "<a href" in str(author_soup):
                    author_list = [
                        f"[{i.get_text()}](https://archiveofourown.org{i['href']})"
                        for i in author_soup.contents
                        if i not in ["\n", ", "]
                    ]

                    # author & author_list are only used when there's one author.
                    author = author_list[0][
                        author_list[0].index("[") + 1 : author_list[0].index("]")
                    ]
                    author_link = author_list[0][
                        author_list[0].rindex("(") + 1 : author_list[0].rindex(")")
                    ]

                elif author_soup.get_text(strip=True) == "Anonymous":
                    author = "Anonymous"
                    author_link = (
                        "https://archiveofourown.org/collections/anonymous/profile"
                    )
                    author_list = [
                        "[Anonymous](https://archiveofourown.org/collections/anonymous/profile)"
                    ]

                author_image_soup = BeautifulSoup(
                    self.scraper.get(author_link).text, "lxml"
                ).find("div", class_="primary header module")
                author_image = author_image_soup.find(class_="icon").img["src"]
                author_image_link = (
                    author_image
                    if author_image.startswith("https://")
                    else f"https://archiveofourown.org{author_image}"
                )

                ao3_story_dict = {
                    "TYPE": "STORY",
                    "RATING": trim_text(rating),
                    "ARCHIVE_WARNING": trim_text(archive_warning),
                    "ARCHIVE_WARNING_LIST": archive_warning_list,
                    "FANDOM": trim_text(fandom),
                    "CHARACTERS": characters,
                    "RELATIONSHIPS": relationships,
                    "TITLE": trim_text(title),
                    "SUMMARY": trim_text(summary),
                    "SERIES": series,
                    "LANGUAGE": language,
                    "STATS": trim_text(stats),
                    "AUTHOR": trim_text(author, 256),
                    "AUTHOR_LINK": author_link,
                    "AUTHOR_LIST": author_list,
                    "AUTHOR_IMAGE_LINK": author_image_link,
                }

                return ao3_story_dict

        except Exception as err:
            return {"TYPE": "ERROR", "MESSAGE": f"{err}"}

    def ao3_series(self) -> dict:
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
            series_data = self.soup.find("dl", class_="series meta group")

            series_title = self.soup.find("h2", class_="heading").get_text(strip=True)

            author_list = [
                f"[{i.get_text()}](https://archiveofourown.org{i['href']})"
                for i in series_data.dd
                if i not in ["\n", ", "]
            ]

            # AUTHOR & AUTHOR_LINK are only used when there's one author.
            author = author_list[0][
                author_list[0].index("[") + 1 : author_list[0].index("]")
            ]
            author_link = author_list[0][
                author_list[0].rindex("(") + 1 : author_list[0].rindex(")")
            ]

            author_image_soup = BeautifulSoup(
                self.scraper.get(author_link).text, "lxml"
            ).find("div", class_="primary header module")

            author_image = [i for i in author_image_soup.contents if i != "\n"][
                1
            ].a.img["src"]

            author_image_link = (
                author_image
                if author_image.startswith("https://")
                else f"https://archiveofourown.org{author_image}"
            )

            series_begun = "".join(
                i.next_sibling.next_sibling.get_text()
                for i in series_data.find_all("dt", string="Series Begun:")
            )

            series_updated = "".join(
                i.next_sibling.next_sibling.get_text()
                for i in series_data.find_all("dt", string="Series Updated:")
            )

            # Stats: [Words: Works: Complete: Bookmarks:]
            stats_text = ""
            stats_arr = [
                i.get_text(strip=True)
                for i in series_data.find_all("dt", string="Stats:")[
                    0
                ].next_sibling.next_sibling.dl
            ][1:-1]

            for group in self.chunker(stats_arr, 4):
                stats_text += f"{' '.join(group)} • "
            stats = stats_text[:-2]

            try:
                description_var = (
                    str(
                        series_data.find_all("dt", string="Description:")[
                            0
                        ].next_sibling.next_sibling.blockquote
                    )
                    .replace("<br/>", "\r\n")
                    .replace("</p><p>", "</p><p>\r\n</p><p>")
                )
                description = trim_text(
                    BeautifulSoup(description_var, "lxml").get_text()
                )
            except:
                description = None

            try:
                notes_var = (
                    str(
                        series_data.find_all("dt", string="Notes:")[
                            0
                        ].next_sibling.next_sibling.blockquote
                    )
                    .replace("<br/>", "\r\n")
                    .replace("</p><p>", "</p><p>\r\n</p><p>")
                )
                notes = trim_text(BeautifulSoup(notes_var, "lxml").get_text())
            except:
                notes = None

            # WORKS
            try:
                main_div = self.soup.find("div", {"id": "main"})
                work_list = main_div.find(
                    "ul", class_="series work index group"
                ).contents
                works = []
                for i in work_list:
                    if i.find("a") != -1:
                        works.append(
                            f"[{i.find('a').text}](https://archiveofourown.org{i.find('a')['href']})"
                        )
            except:
                works = None

            ao3_series_dict = {
                "TYPE": "SERIES",
                "SERIES_TITLE": trim_text(series_title),
                "AUTHOR": trim_text(author),
                "AUTHOR_LINK": author_link,
                "AUTHOR_LIST": author_list,
                "AUTHOR_IMAGE_LINK": author_image_link,
                "SERIES_BEGUN": series_begun,
                "SERIES_UPDATED": series_updated,
                "DESCRIPTION": description,
                "NOTES": notes,
                "STATS": stats,
                "WORKS": works,
            }

            return ao3_series_dict

        except Exception as err:
            return {"TYPE": "ERROR", "MESSAGE": f"{err}"}

    def ao3_collection(self) -> dict:
        try:
            # ++++++++++++++++++ HEADING ++++++++++++++++++
            heading = self.soup.find("div", class_="primary header module")

            story_title = heading.find("h2", class_="heading")
            story_title_text = story_title.get_text(strip=True)
            story_title_link = (
                f"https://archiveofourown.org{story_title.find('a')['href']}"
            )

            image_link = heading.find("div", class_="icon").img["src"]
            image = (
                image_link
                if image_link.startswith("https://")
                else f"https://archiveofourown.org{image_link}"
            )

            try:
                summary_var = (
                    str(heading.find("blockquote", class_="userstuff"))
                    .replace("<br/>", "\r\n")
                    .replace("</p><p>", "</p><p>\r\n</p><p>")
                )
                summary = BeautifulSoup(summary_var, "lxml").get_text()
            except:
                summary = heading.find("blockquote", class_="userstuff").get_text(
                    strip=True
                )

            status = heading.find("p", class_="type").get_text(strip=True)

            # ++++++++++++++++++ WRAPPER ++++++++++++++++++
            wrapper = self.soup.find("dl", class_="meta group")

            active_since = wrapper.dt.next_sibling.get_text(strip=True)

            maintainers_list_html = [
                i
                for i in wrapper.find("ul", class_="mods commas")
                if i not in ["\n", ", "]
            ]

            maintainers_list = [
                f"[{i.get_text(strip=True)}](https://archiveofourown.org{i.a['href']})"
                for i in maintainers_list_html
            ]

            # If there's only one author
            author = maintainers_list[0][
                maintainers_list[0].index("[") + 1 : maintainers_list[0].index("]")
            ]

            author_link = maintainers_list[0][
                maintainers_list[0].rindex("(") + 1 : maintainers_list[0].rindex(")")
            ]

            try:
                contact_html = maintainers_list_html[
                    0
                ].parent.parent.next_sibling.next_sibling
                contact = contact_html.next_sibling.next_sibling.get_text(strip=True)
            except:
                contact = None

            # ++++++++++++++++++ PREFACE GROUP ++++++++++++++++++
            preface_group = self.soup.find("div", class_="preface group")
            try:
                intro_soup = (
                    str(preface_group.find("div", {"id": "intro"}).blockquote)
                    .replace("<br/>", "<p>\r\n</p>")
                    .replace("</p><p>", "</p><p>\r\n</p><p>")
                )
                intro = trim_text(BeautifulSoup(intro_soup, "lxml").get_text()[1:-1])
            except:
                intro = None

            try:
                rules_soup = (
                    str(preface_group.find("div", {"id": "rules"}).blockquote)
                    .replace("<br/>", "<p>\r\n</p>")
                    .replace("</p><p>", "</p><p>\r\n</p><p>")
                )
                rules = trim_text(BeautifulSoup(rules_soup, "lxml").get_text()[1:-1])
            except:
                rules = None

            ao3_collection_dict = {
                "TYPE": "COLLECTION",
                "STORY_TITLE_TEXT": trim_text(story_title_text),
                "STORY_TITLE_LINK": story_title_link,
                "IMAGE": image,
                "SUMMARY": trim_text(summary),
                "STATUS": status,
                "ACTIVE_SINCE": active_since,
                "MAINTAINERS_LIST": maintainers_list,
                "AUTHOR": author,
                "AUTHOR_LINK": author_link,
                "CONTACT": contact,
                "INTRO": intro,
                "RULES": rules,
            }

            return ao3_collection_dict

        except Exception as err:
            return {"TYPE": "ERROR", "MESSAGE": f"{err}"}
