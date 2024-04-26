from re import search, IGNORECASE
from discord import Embed
from dateutil import tz
from datetime import datetime

now = datetime.now(tz=tz.tzlocal())


def validate_url(url: str, url_patterns: list[str]) -> bool:
    for pattern in url_patterns:
        if search(pattern, url, IGNORECASE):
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


def process_list(field_list: list[str]) -> str | None:
    """Process a list of items and return a formatted string.

    Args:
        field_list: The list of items to process.

    Returns:
        A formatted string representing the processed list. Or None if field_list is None.
    """
    if field_list is not None:
        # Join the items into a string
        processed_field = ", ".join(field_list)

        # If the list is longer than the max_items_to_display, truncate and display more count
        if len(processed_field) > 1024:
            visible_items = processed_field[:1024].split(",")
            del visible_items[-1]
            cut_off_items = len(processed_field[1024:].split(",")) + 1
            visible_items_string = ", ".join(visible_items)
            processed_field = f"{visible_items_string} and {cut_off_items} more"

        return processed_field

    # If field_list is None
    return None


def delete_first_and_last_from_list(list_arg: list[str] | None, threshold: int = 3):
    if list_arg is not None and len(list_arg) >= threshold:
        # Remove the first and last items from the list if the list is long enough
        del list_arg[0]
        del list_arg[-1]
    return list_arg
