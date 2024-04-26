from discord import Embed
from scrapers.scribblehub import ScribbleHub
import re
from dateutil import tz
from datetime import datetime

now = datetime.now(tz=tz.tzlocal())


def ScribbleHubEmbed(URL: str):
	SHinstance = ScribbleHub(URL)
	try:
		if re.search(r"(^https://www\.scribblehub\.com/(series|read))/\d+", URL, re.IGNORECASE):
			SHReply = SHinstance.SHWork()

			# Create the initial embed object #

			# Description has a limit of 4096, but I'm setting this to 350 characters.
			DESCRIPTION = SHReply['SYNOPSIS'] if len(SHReply['SYNOPSIS']) < 350 else f"{SHReply['SYNOPSIS'][:345]} ..."

			embed = Embed(
				title=SHReply['STORY_TITLE'],
				url=URL,
				description=DESCRIPTION,
				color=0xE09319)

			# Add author, thumbnail, fields, and footer to the embed
			embed.set_author(
				name=SHReply['AUTHOR'],
				url=SHReply['AUTHOR_PROFILE_LINK'],
				icon_url=SHReply['AUTHOR_AVATAR_LINK']
			)

			embed.set_thumbnail(url=SHReply['COVER_IMAGE'])

			if SHReply['FANDOM'] != 'N/A':
				embed.add_field(name="Fandom", value=SHReply['FANDOM'], inline=False)

			if SHReply['CONTENT_WARNING'] != 'N/A':
				embed.add_field(name="Content Warning", value=SHReply['CONTENT_WARNING'], inline=False)

			embed.add_field(
				name="Stats",
				value=
				f"""{SHReply['VIEWS']} • {SHReply['FAVOURITES']} • {SHReply['CHAPTER_COUNT']} • {SHReply['READERS']}""",
				inline=False)

			embed.add_field(name="Genres", value=SHReply['GENRES'], inline=False)

			if SHReply['RELATED_SERIES'] is not None:
				embed.add_field(name="Related Series", value=SHReply['RELATED_SERIES'], inline=False)

			embed.set_footer(text=f"Info retrieved by Summarium on {now.strftime('%a %d at %X')}")

			return embed

		elif re.search(r"(^https://www\.scribblehub\.com/profile)/\d+/(\w+)*", URL, re.IGNORECASE):
			SHReply = SHinstance.SHProfile()

			# Create the initial embed object #

			# Description has a limit of 4096, but I'm setting this to 500 characters.

			embed = Embed(
				title="ScribbleHub Profile",
				url=URL,
				description='',
				color=0xE09319
			)

			# Add author, thumbnail, fields, and footer to the embed
			embed.set_author(
				name=SHReply['AUTHOR_NAME'],
				url=URL,
				icon_url=SHReply['PROFILE_PHOTO']
			)

			embed.set_thumbnail(url=SHReply['PROFILE_PHOTO'])

			if SHReply['ABOUT'] != '':
				embed.add_field(name="About", value=SHReply['ABOUT'], inline=False)

			if SHReply['HOME_PAGE'] != 'N/A':
				embed.add_field(name="Home Page", value=SHReply['HOME_PAGE'], inline=False)

			embed.add_field(name="Last Active", value=SHReply['LAST_ACTIVE'], inline=True)
			embed.add_field(name="Followers", value=SHReply['FOLLOWERS'], inline=True)
			embed.add_field(name="Following", value=SHReply['FOLLOWING'], inline=True)

			embed.add_field(
				name="Stats",
				value=
				f"""
				Joined: {SHReply['JOINED']} • Readers: {SHReply['READERS']} • Series: {SHReply['NUMBER_OF_SERIES']}
				""",
				inline=False)

			embed.set_footer(text=f"Info retrieved by Summarium on {now.strftime('%a %d at %X')}")

			return embed

	except:
		embed = Embed(
			title="Summarium Error",
			url=URL,
			description=f"Can not get scribblehub URL {URL}",
			color=0x6A0DAD
		)

		return embed
