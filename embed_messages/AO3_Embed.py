from discord import Embed
from scrapers.archiveofourown import ArchiveOfOurOwn
from utils import (
    validate_url,
    handle_error,
    pattern_matcher,
    process_list,
    create_footer,
)

# from dateutil import tz
# from datetime import datetime
# now = datetime.now(tz=tz.tzlocal())


def ao3_main(url: str):
    try:
        url_patterns = [
            r"^https://archiveofourown\.org/works/\d+",
            r"^https://archiveofourown\.org/collections/\w+/\bworks\b/\d+",
            r"^https://archiveofourown\.org/series/\d+",
            r"^https://archiveofourown\.org/collections/\w+",
        ]
        if validate_url(url, url_patterns):
            data = process_data(url)
            return archive_of_our_own_embed(data, url)
        else:
            return handle_error(url, "Unable to get ArchiveOfOurOwn data")
    except Exception as e:
        return handle_error(url, f"Development Error: {e}")


def process_data(url: str) -> dict:
    ao3_instance = ArchiveOfOurOwn(url)
    if pattern_matcher(
        r"^https://archiveofourown\.org/works/\d+", url
    ) or pattern_matcher(
        r"^https://archiveofourown\.org/collections/\w+/\bworks\b/\d+", url
    ):
        return ao3_instance.ao3_story()
    elif pattern_matcher(r"^https://archiveofourown\.org/series/\d+", url):
        return ao3_instance.ao3_series()
    elif pattern_matcher(r"^https://archiveofourown\.org/collections/\w+", url):
        return ao3_instance.ao3_collection()
    else:
        raise ValueError("Unsupported URL")


def archive_of_our_own_embed(data: dict, url: str):
    # fields	    Up to 25 field objects
    # field.name	256 characters
    # field.value	1024 characters
    # footer.text	2048 characters
    # author.name	256 characters

    if data["TYPE"] == "STORY":
        # Dealing with limits
        author_name = data["AUTHOR"]
        archive_warning = data["ARCHIVE_WARNING"]
        fandom = data["FANDOM"]
        relationships: str | None = data["RELATIONSHIPS"]
        characters: str | None = data["CHARACTERS"]
        stats = data["STATS"]
        summary = data["SUMMARY"]
        rating = data["RATING"]
        title = data["TITLE"]

        ao3_embed = Embed(title=title, url=url, description=summary, color=0xFF0000)

        # Add author
        if len(data["AUTHOR_LIST"]) == 1:
            ao3_embed.set_author(
                name=author_name,
                url=data["AUTHOR_LINK"],
                icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png",
            )
            if data["AUTHOR_IMAGE_LINK"].startswith("https://"):
                ao3_embed.set_thumbnail(url=data["AUTHOR_IMAGE_LINK"])
        else:
            ao3_embed.set_author(
                name="Archive Of Our Own",
                url=url,
                icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png",
            )

            authors_list_string_ = process_list(data["AUTHOR_LIST"])
            ao3_embed.add_field(
                name="Authors", value=authors_list_string_, inline=False
            )

        aw_boolean = True if len(data["ARCHIVE_WARNING_LIST"]) == 3 else False
        ao3_embed.add_field(
            name="Archive Warnings", value=archive_warning, inline=aw_boolean
        )
        ao3_embed.add_field(name="Rating", value=rating, inline=True)
        ao3_embed.add_field(name="Language", value=data["LANGUAGE"], inline=True)
        ao3_embed.add_field(name="Fandom", value=fandom, inline=False)

        ao3_embed.add_field(
            name="Characters",
            value=(characters if characters is not None else "No Characters"),
            inline=False,
        )

        ao3_embed.add_field(
            name="Relationships",
            value=(relationships if relationships is not None else "No Relationships"),
            inline=False,
        )

        if len(data["SERIES"]) > 0:
            ao3_embed.add_field(
                name="Series",
                value=process_list(data["SERIES"], " • "),
                inline=False,
            )

        ao3_embed.add_field(name="Stats", value=stats, inline=False)
        create_footer(ao3_embed)

        return ao3_embed

    elif data["TYPE"] in ["LOGIN_REQUIRED", "MYSTERY_WORK"]:
        return Embed(
            title=data["EMBED_TITLE"],
            url=url,
            description=data["DESCRIPTION"],
            color=0xFF0000,
        )

    elif data["TYPE"] == "SERIES":
        # Dealing with limits
        # Series Title* [240 characters left]
        # Description: [1250 characters left]
        # Notes: [5000 characters left]
        author_name = data["AUTHOR"]
        description = (
            data["DESCRIPTION"]
            if data["DESCRIPTION"] is not None
            else "No description available"
        )
        notes = data["NOTES"] if data["NOTES"] is not None else "No notes available"
        series_title = data["SERIES_TITLE"]

        ao3_series_embed = Embed(
            title=series_title, url=url, description=description, color=0xFF0000
        )

        # Add author, thumbnail, fields, and footer to the embed
        if len(data["AUTHOR_LIST"]) == 1:
            ao3_series_embed.set_author(
                name=author_name,
                url=data["AUTHOR_LINK"],
                icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png",
            )
            if data["AUTHOR_IMAGE_LINK"].startswith("https://"):
                ao3_series_embed.set_thumbnail(url=f"{data['AUTHOR_IMAGE_LINK']}")
        else:
            ao3_series_embed.set_author(
                name="Archive Of Our Own",
                url=url,
                icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png",
            )
            authors_list_string = process_list(data["AUTHOR_LIST"])
            ao3_series_embed.add_field(
                name="Authors", value=authors_list_string, inline=False
            )

        ao3_series_embed.add_field(
            name="Series Begun", value=f"{data['SERIES_BEGUN']}", inline=True
        )
        ao3_series_embed.add_field(
            name="Series Updated",
            value=f"{data['SERIES_UPDATED']}",
            inline=True,
        )
        ao3_series_embed.add_field(name="Notes", value=notes, inline=False)
        if data["WORKS"] is not None:
            works = process_list(data["WORKS"], " • ")
            ao3_series_embed.add_field(name="Works", value=works, inline=False)
        ao3_series_embed.add_field(name="Stats", value=data["STATS"], inline=False)

        create_footer(ao3_series_embed)

        return ao3_series_embed

    elif data["TYPE"] == "COLLECTION":
        main_lt: list[str] = data["MAINTAINERS_LIST"]

        story_title = data["STORY_TITLE_TEXT"]
        ao3_collection_embed = Embed(
            title=story_title, url=url, description=data["SUMMARY"], color=0xFF0000
        )

        # Add author, thumbnail, fields, and footer to the embed
        if data["IMAGE"].startswith("https://"):
            ao3_collection_embed.set_thumbnail(url=data["IMAGE"])

        if len(main_lt) == 1:
            ao3_collection_embed.set_author(
                name=data["AUTHOR"],
                url=f"{data['AUTHOR_LINK']}",
                icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png",
            )
        else:
            ao3_collection_embed.set_author(
                name="Archive Of Our Own",
                url=url,
                icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png",
            )
            authors = process_list(main_lt, " • ")
            ao3_collection_embed.add_field(
                name="Maintainers", value=authors, inline=False
            )

        if data["INTRO"] is not None:
            intro = data["INTRO"]
            ao3_collection_embed.add_field(name="Intro", value=intro, inline=False)

        if data["RULES"] is not None:
            rules = data["RULES"]
            ao3_collection_embed.add_field(name="Rules", value=rules, inline=False)

        ao3_collection_embed.add_field(
            name="Status", value=f"{data['STATUS']}", inline=True
        )

        ao3_collection_embed.add_field(
            name="Active Since", value=f"{data['ACTIVE_SINCE']}", inline=True
        )

        if data["CONTACT"] is not None:
            ao3_collection_embed.add_field(
                name="Contact", value=data["CONTACT"], inline=True
            )

        create_footer(ao3_collection_embed)

        return ao3_collection_embed

    else:
        return handle_error(url, f"Can not get {url}")
