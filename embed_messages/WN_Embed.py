from discord import Embed
from scrapers.webnovel import webnovel
import re
from dateutil import tz
from datetime import datetime

now = datetime.now(tz=tz.tzlocal())


def WebNovelEmbed(URL: str):
	WNinstance = webnovel(URL)
	try:
		if re.search(r"(www|m)\.webnovel\.com/book/", URL, re.IGNORECASE):
			# Create the initial embed object #

			# Description has a limit of 4096, but I'm setting this to 350 characters.
			DESCRIPTION = WNinstance['SYNOPSIS'] if len(WNinstance['SYNOPSIS']) < 350 else f"{WNinstance['SYNOPSIS'][:345]} ..."

			embed = Embed(
				title=WNinstance['STORY_TITLE'],
				url=URL,
				description=DESCRIPTION,
				color=0xF73B83)

			# Add author, thumbnail, fields, and footer to the embed
			embed.set_author(
				name=WNinstance['AUTHOR'],
				url=WNinstance['AUTHOR_PROFILE_LINK'],
				icon_url=WNinstance['AUTHOR_IMAGE']
			)

			embed.set_thumbnail(url=WNinstance['COVER_IMAGE'])

			embed.add_field(
				name="Stats",
				value=
				f"""{WNinstance['VIEWS']} • {WNinstance['CHAPTERS']} • {WNinstance['RATINGS']}""",
				inline=False)

			embed.add_field(name="Genre", value=WNinstance['GENRE'], inline=True)

			if WNinstance['RANKING'] is not None:
				embed.add_field(name="Power Ranking", value=WNinstance['RANKING'], inline=True)

			embed.add_field(name="Tags", value=" • ".join(WNinstance['TAGS']), inline=False)

			embed.set_footer(text=f"Info retrieved by Summarium on {now.strftime('%a %d at %X')}")

			return embed

	except:
		embed = Embed(
			title="Summarium Error",
			url=URL,
			description=f"Can not get WebNovel URL {URL}",
			color=0x544BFF
		)

		return embed
