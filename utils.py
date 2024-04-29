from re import search, IGNORECASE, Pattern, Match
from discord import Embed
from constants import Site
from dateutil import tz
from datetime import datetime

now = datetime.now(tz=tz.tzlocal())


def pattern_matcher(pattern: str | Pattern[str], string: str) -> Match[str] | None:
    return search(pattern, string, IGNORECASE)


def validate_url(url: str, url_patterns: list[str]) -> bool:
    for pattern in url_patterns:
        if pattern_matcher(pattern, url):
            return True
    return False


def handle_error(url: str, error_message: str) -> Embed:
    embed = Embed(
        title="Summarium Error",
        url=url,
        description=f"An error occurred: {error_message}",
        color=0x0000FF,
    )
    return embed


def trim_text(text: str, max_length: int = 1024, suffix: str = " ...") -> str:
    """
    Trims the text to the specified length
    :param text: The text to trim
    :param max_length: The maximum length of the text
    :param suffix: The suffix to append to the text if it is trimmed (default: " ...")
    :return: The trimmed text
    """
    return text[: max_length - len(suffix)] + suffix if len(text) > max_length else text


def process_list(field_list: list[str], join_string: str = ", ") -> str:
    """
    Process a list of items and return a formatted string.

    :param field_list: The list of items to process.
    :param join_string: The string to use in the join operation.
    :return: A formatted string representing the processed list. Or None if field_list is None.
    """

    # Join the items into a string
    processed_field = join_string.join(field_list)

    # If the list is longer than the max_items_to_display, truncate and display more count
    if len(processed_field) > 1024:
        visible_items = processed_field[:1024].split(join_string)

        cut_off_items = processed_field[1024:].split(join_string)
        cut_off_items_length = len(cut_off_items)

        if not visible_items[-1].endswith(")"):
            del visible_items[-1]

        visible_items_string = join_string.join(visible_items)
        processed_field = f"{visible_items_string} and {cut_off_items_length} more"

    return processed_field


def trim_list_ends(list_arg: list[str], min_length: int = 3) -> list[str]:
    """
    Removes the first and last items from a list if the list length
    is greater than or equal to the specified minimum length.

    :param list_arg: The list to be trimmed.
    :param min_length: The minimum length required for trimming the list. Defaults to 3.
    :return: The trimmed list or the original list.
    """
    if len(list_arg) >= min_length:
        list_arg = list_arg[1:-1]
    return list_arg


def create_footer(embed: Embed):
    return embed.set_footer(
        text=f"Info retrieved by Summarium on {now.strftime('%a %d at %X')}"
    )


def regex_strings(site: Site):
    match site:
        case site.ArchiveOfOurOwn:
            return (
                r"^https://archiveofourown\.org/(\bseries\b|\bworks\b|\bcollections\b)/"
            )
        case site.FanFictionDotNet:
            return r"^https://(www|m)\.(\bfanfiction\b\.\bnet\b)/s/\d+/\d+/\w*"
        case site.SpaceBattles:
            return r"^https?://forums?\.spacebattles\.com/threads/(([a-zA-Z%0-9]+-*)+\.[0-9]+)/?"
        case site.FictionLive:
            return r"^https?://fiction\.live/(?:stories|Sci-fi)/([^\/]+|)/([0-9a-zA-Z\-]+)/?.*"
        case site.ScribbleHub:
            return r"(^https://www\.scribblehub\.com/(series|read|profile))/\d+"
        case site.WebNovel:
            return r"(www|m)\.webnovel\.com/book/"
        case _:
            raise TypeError("not a point we support")
