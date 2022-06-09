from discord import Embed, File
from scrapers.fanfictionnet import fanfictiondotnet
from dateutil import tz
from datetime import datetime

now = datetime.now(tz=tz.tzlocal())


def FanFictionDotNetEmbed(URL: str):
	FFReply = fanfictiondotnet(URL)
	file = File('./embed_messages/Logos/FanFictionDotNet.png', filename='FanFictionDotNet.png')
	try:
		# fields	Up to 25 field objects
		# field.name	256 characters
		# field.value	1024 characters
		# footer.text	2048 characters
		# author.name	256 characters

		# Create the initial embed object #
		embed = Embed(
			title=f"{FFReply['STORY_TITLE']}",
			url=str(URL),
			description=f"{FFReply['SYNOPSIS']}",
			color=0x333399
		)

		# Add author, thumbnail, fields, and footer to the embed
		embed.set_author(
			name=f"{FFReply['AUTHOR']}",
			url=f"{FFReply['AUTHOR_LINK']}",
			icon_url="attachment://FanFictionDotNet.png"
		)

		if FFReply['COVER_IMAGE'] is not None and FFReply['COVER_IMAGE'].startswith('https://'):
			embed.set_thumbnail(url=FFReply['COVER_IMAGE'])
		else:
			embed.set_thumbnail(url='attachment://FanFictionDotNet.png')

		if FFReply['CHARACTERS'] is not None:
			embed.add_field(name="Characters", value=str(FFReply['CHARACTERS']), inline=True)

		if FFReply['GENRE'] is not None:
			embed.add_field(name="Genre", value=FFReply['GENRE'], inline=True)

		embed.add_field(name="Status", value=f"*{FFReply['STATUS'].capitalize()}* • \
		Published on {FFReply['PUBLISHED'][:10]} • Updated on {FFReply['UPDATED'][:10]}", inline=False)

		# Because why not?
		chapterstring = f"{FFReply['CHAPTERS']} chapter" if int(FFReply['CHAPTERS']) == 1 else \
			f"{FFReply['CHAPTERS']} chapters"
		embed.add_field(name="Stats", value=f"{FFReply['RATING']} • {FFReply['WORDS']} words • {chapterstring}\
		 • {FFReply['LANGUAGE']}", inline=False)

		embed.set_footer(text=f"Info retrieved by Summarium on {now.strftime('%a %-d at %X')}")

		return file, embed

	except Exception:
		embed = Embed(
			title="Summarium Error",
			url=str(URL),
			description=f"Can not get {URL}",
			color=0x993633
		)
		embed.set_thumbnail(url='attachment://FanFictionDotNet.png')
		return file, embed
