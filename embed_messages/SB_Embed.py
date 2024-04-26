from discord import Embed
from scrapers.spacebattles import SpaceBattles
from dateutil import tz
from datetime import datetime

now = datetime.now(tz=tz.tzlocal())


def SpaceBattlesEmbed(URL: str):
    SBInstance = SpaceBattles(URL)

    SBReply = SBInstance.SBWork()

    if SBReply["IS_FETCHED"]:
        # Create the initial embed object #

        # Description has a limit of 4096, but I'm setting this to 545 characters.
        DESCRIPTION = (
            SBReply["DESCRIPTION"]
            if len(SBReply["DESCRIPTION"]) < 550
            else f"{SBReply['DESCRIPTION'][:545]} ..."
        )

        embed = Embed(
            title=SBReply["STORY_TITLE"],
            url=URL,
            description=DESCRIPTION,
            color=0x191F2D,
        )

        # Add author, thumbnail, fields, and footer to the embed
        embed.set_author(
            name=SBReply["AUTHOR"],
            url=SBReply["AUTHOR_PROFILE_LINK"],
            icon_url=SBReply["AUTHOR_AVATAR_LINK"],
        )

        embed.set_thumbnail(url=SBReply["COVER_IMAGE"])

        if SBReply["STORY_STATUS"]:
            embed.add_field(
                name="Story Status", value=SBReply["STORY_STATUS"], inline=True
            )

        if SBReply["WORDS"]:
            embed.add_field(name="Words", value=SBReply["WORDS"], inline=True)
        LAST_UPDATED = SBReply["LAST_UPDATED"]
        LAST_UPDATED_YESTERDAY_BOOL = LAST_UPDATED.startswith("Y")
        LAST_UPDATED_STRING = (
            f"{'on' if not LAST_UPDATED_YESTERDAY_BOOL else ''} {LAST_UPDATED}"
        )

        embed.add_field(
            name="Created + Updated",
            value=f"Created on {SBReply['CREATED_ON']} • Last Updated {LAST_UPDATED_STRING}",
            inline=False,
        )

        embed.add_field(
            name="Stats",
            value=f"""{SBReply['THREADMARKS']} Threadmarks • {SBReply['RECENT_READERS']} Recent Readers • {SBReply['WATCHERS']} Watchers""",
            inline=False,
        )

        if len(SBReply["TAGS"]) > 15:
            TAGS = f"{' • '.join(SBReply['TAGS'][:15])} and {len(SBReply['TAGS'][15:])} more"
        else:
            TAGS = " • ".join(SBReply["TAGS"])

        embed.add_field(name="Tags", value=TAGS, inline=False)

        embed.set_footer(
            text=f"Info retrieved by Summarium on {now.strftime('%a %d %b %Y at %X')}"
        )

        return embed

    else:
        embed = Embed(
            title="Summarium Error",
            url=URL,
            description=f"Can not get SpaceBattles URL {URL}",
            color=0x000000,
        )

        return embed
