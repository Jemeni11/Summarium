import re
from discord import Embed
from scrapers.archiveofourown import ArchiveOfOurOwn
from dateutil import tz
from datetime import datetime

now = datetime.now(tz=tz.tzlocal())


def ArchiveOfOurOwnEmbed(url: str):
	AO3instance = ArchiveOfOurOwn(url)
	try:
		if re.search(r"^https://archiveofourown\.org/works/\d+", url, re.IGNORECASE) \
				or re.search(r"^https://archiveofourown\.org/collections/\w+/\bworks\b/\d+", url, re.IGNORECASE):
			AO3Reply = AO3instance.A03Story()
			# Dealing with limits
			AUTHOR_NAME = f"{AO3Reply['AUTHOR']}" if len(
				AO3Reply['AUTHOR']) <= 256 else f"{AO3Reply['AUTHOR'][:251]} ..."
			ARCHIVE_WARNING = f"{AO3Reply['ARCHIVE_WARNING']}" if len(
				AO3Reply['ARCHIVE_WARNING']) <= 250 else f"{AO3Reply['ARCHIVE_WARNING'][:245]} ..."
			FANDOM = f"{AO3Reply['FANDOM']}" if len(AO3Reply['FANDOM']) <= 250 else f"{AO3Reply['FANDOM'][:245]} ..."
			if len(AO3Reply['RELATIONSHIPS']) == 3:
				RELATIONSHIPS = AO3Reply['RELATIONSHIPS'][1] + " "
			else:
				RELATIONSHIPS = ', '.join(AO3Reply['RELATIONSHIPS'][1:6]).strip() + " "
			if len(AO3Reply['CHARACTERS']) == 3:
				CHARACTERS = AO3Reply['CHARACTERS'][1] + " "
			else:
				CHARACTERS = ', '.join(AO3Reply['CHARACTERS'][1:6]).strip() + " "
			STATS = f"{AO3Reply['STATS']}" if len(AO3Reply['STATS']) <= 250 else f"{AO3Reply['STATS'][:245]} ..."
			DESCRIPTION = AO3Reply['SUMMARY'] if len(AO3Reply['SUMMARY']) < 270 else f"{AO3Reply['SUMMARY'][:265]} ..."
			# fields	Up to 25 field objects
			# field.name	256 characters
			# field.value	1024 characters
			# footer.text	2048 characters
			# author.name	256 characters

			# Create the initial embed object #
			embed = Embed(
				title=AO3Reply['TITLE'],
				url=url,
				description=DESCRIPTION,
				color=0xFF0000
			)

			# Add author, thumbnail, fields, and footer to the embed
			if len(AO3Reply['AUTHOR_LIST']) == 1:
				embed.set_author(
					name=AUTHOR_NAME,
					url=AO3Reply['AUTHOR_LINK'],
					icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png"
				)
				if AO3Reply['AUTHOR_IMAGE_LINK'].startswith('https://'):
					embed.set_thumbnail(url=AO3Reply['AUTHOR_IMAGE_LINK'])
			else:
				embed.set_author(
					name="Archive Of Our Own",
					url=url,
					icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png"
				)
				embed.add_field(name="Authors", value=' • '.join(AO3Reply['AUTHOR_LIST']), inline=False)

			AWBoolean = True if len(AO3Reply['ARCHIVE_WARNING_LIST']) == 3 else False
			embed.add_field(name="Archive Warnings", value=ARCHIVE_WARNING, inline=AWBoolean)

			embed.add_field(name="Rating", value=AO3Reply['RATING'], inline=True)
			embed.add_field(name="Language", value=AO3Reply['LANGUAGE'], inline=True)

			embed.add_field(name="Fandom", value=FANDOM, inline=False)

			# if AO3Reply['CHARACTERS'] != 'N/A':
			#   embed.add_field(name="Characters", value=CHARACTERS, inline=False)

			# if AO3Reply['RELATIONSHIPS'] != 'N/A':
			#   embed.add_field(name="Relationships", value=RELATIONSHIPS, inline=False)

			if AO3Reply['CHARACTERS'] != 'N/A' and AO3Reply['RELATIONSHIPS'] != 'N/A':
				if len(AO3Reply['CHARACTERS']) + len(AO3Reply['RELATIONSHIPS']) <= 10:
					embed.add_field(
						name="Characters + Relationships",
						value=f"{CHARACTERS[:-1]} • *{RELATIONSHIPS[:-1]}* ",
						inline=False
					)
				else:
					embed.add_field(
						name="Characters + Relationships",
						value=f"{CHARACTERS} ... • *{RELATIONSHIPS}* ...",
						inline=False
					)
			elif AO3Reply['CHARACTERS'] != 'N/A' and AO3Reply['RELATIONSHIPS'] == 'N/A':
				embed.add_field(
					name="Characters",
					value=', '.join(AO3Reply['CHARACTERS'][1:11]).strip(),
					inline=False
				)
			elif AO3Reply['RELATIONSHIPS'] != 'N/A' and AO3Reply['CHARACTERS'] == 'N/A':
				embed.add_field(
					name="Relationships",
					value=', '.join(AO3Reply['CHARACTERS'][1:11]).strip(),
					inline=False
				)

			if len(AO3Reply['SERIES']):
				embed.add_field(name="Series", value=' • '.join(AO3Reply['SERIES']), inline=False)

			embed.add_field(name="Stats", value=STATS, inline=False)

			embed.set_footer(text=f"Info retrieved by Summarium on {now.strftime('%a %-d at %X')}")

			return embed

		elif re.search(r"^https://archiveofourown\.org/series/\d+", url, re.IGNORECASE):
			AO3Reply = AO3instance.A03Series()
			# Dealing with limits
			# Series Title* [240 characters left]
			# Description: [1250 characters left]
			# Notes: [5000 characters left]
			AUTHOR_NAME = f"{AO3Reply['AUTHOR']}" if len(
				AO3Reply['AUTHOR']) <= 256 else f"{AO3Reply['AUTHOR'][:251]} ..."
			if AO3Reply['DESCRIPTION'] is not None:
				DESCRIPTION = f"{AO3Reply['DESCRIPTION']}" if len(
					AO3Reply['DESCRIPTION']) <= 300 else f"{AO3Reply['DESCRIPTION'][:295]} ..."
			else:
				DESCRIPTION = 'No description available'
			if AO3Reply['NOTES'] is not None:
				NOTES = f"{AO3Reply['NOTES']}" if len(AO3Reply['NOTES']) <= 300 else f"{AO3Reply['NOTES'][:295]} ..."
			else:
				NOTES = 'No Notes available'

			# Create the initial embed object #
			embed = Embed(
				title=AO3Reply['SERIES_TITLE'],
				url=url,
				description=DESCRIPTION,
				color=0xFF0000
			)

			# Add author, thumbnail, fields, and footer to the embed
			if len(AO3Reply['AUTHOR_LIST']) == 1:
				embed.set_author(
					name=AUTHOR_NAME,
					url=AO3Reply['AUTHOR_LINK'],
					icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")
				if AO3Reply['AUTHOR_IMAGE_LINK'].startswith('https://'):
					embed.set_thumbnail(url=f"{AO3Reply['AUTHOR_IMAGE_LINK']}")
			else:
				if len(' • '.join(AO3Reply['AUTHOR_LIST'])) <= 1024:
					AUTHORS = ' • '.join(AO3Reply['AUTHOR_LIST'])
				else:
					AUTHORS_ARR = f"{' • '.join(AO3Reply['AUTHOR_LIST'])[:1019]} ..."
					AUTHORS_ARR_SPLIT = AUTHORS_ARR.split('•')
					del AUTHORS_ARR_SPLIT[-1]
					AUTHORS = f"{' • '.join(AUTHORS_ARR_SPLIT)} ..."
				embed.set_author(
					name="Archive Of Our Own",
					url=url,
					icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png"
				)
				embed.add_field(name="Authors", value=AUTHORS, inline=False)

			embed.add_field(name="Series Begun", value=f"{AO3Reply['SERIES_BEGUN']}", inline=True)
			embed.add_field(name="Series Updated", value=f"{AO3Reply['SERIES_UPDATED']}", inline=True)

			embed.add_field(name="Notes", value=NOTES, inline=False)

			if AO3Reply['WORKS'] != "N/A":
				if len(" • ".join(AO3Reply['WORKS'])) <= 1024:
					WORKS = ' • '.join(AO3Reply['WORKS'])
					print(WORKS)
				else:
					WORKS_ARR = f"{' • '.join(AO3Reply['WORKS'])[:1015]} ..."
					if WORKS_ARR[1014] != ')':
						WORKS_ARR_SPLIT = WORKS_ARR.split(' • ')
						del WORKS_ARR_SPLIT[-1]
						WORKS = f"{' • '.join(WORKS_ARR_SPLIT)} ..."
						embed.add_field(name="Works", value=WORKS, inline=False)
					else:
						embed.add_field(name="Works", value=WORKS_ARR, inline=False)

			embed.add_field(name="Stats", value=AO3Reply['STATS'], inline=False)

			embed.set_footer(text=f"Info retrieved by Summarium on {now.strftime('%a %-d at %X')}")

			return embed

		elif re.search(r"^https://archiveofourown\.org/collections/\w+", url, re.IGNORECASE):
			AO3Reply = AO3instance.AO3Collection()
			MAIN_LT = AO3Reply['MAINTAINERS_LIST']

			# Create the initial embed object #
			embed = Embed(
				title=f"{AO3Reply['STORY_TITLE_TEXT']}",
				url=str(url),
				description=AO3Reply['SUMMARY'],
				color=0xFF0000
			)

			# Add author, thumbnail, fields, and footer to the embed
			if AO3Reply['IMAGE'].startswith('https://'):
				embed.set_thumbnail(url=AO3Reply['IMAGE'])
			if len(MAIN_LT) == 1:
				embed.set_author(
					name=AO3Reply['AUTHOR'],
					url=f"{AO3Reply['AUTHOR_LINK']}",
					icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png"
				)
			else:
				if len(' • '.join(MAIN_LT)) > 1024:
					AUTHORS_ARR = f"{' • '.join(MAIN_LT)[:1019]} ..."
					AUTHORS_ARR_SPLIT = AUTHORS_ARR.split('•')
					del AUTHORS_ARR_SPLIT[-1]
					AUTHORS = f"{' • '.join(AUTHORS_ARR_SPLIT)} ..."
				else:
					AUTHORS = ' • '.join(MAIN_LT)
				embed.set_author(
					name="Archive Of Our Own",
					url=url,
					icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png"
				)
				embed.add_field(name="Maintainers", value=AUTHORS, inline=False)

			if AO3Reply['INTRO'] is not None:
				INTRO = f"{AO3Reply['INTRO']}" if len(AO3Reply['INTRO']) <= 300 else f"{AO3Reply['INTRO'][:295]} ..."
				embed.add_field(name="Intro", value=INTRO, inline=False)

			if AO3Reply['RULES'] is not None:
				RULES = f"{AO3Reply['RULES']}" if len(AO3Reply['RULES']) <= 300 else f"{AO3Reply['RULES'][:295]} ..."
				embed.add_field(name="Rules", value=RULES, inline=False)

			embed.add_field(name="Status", value=f"{AO3Reply['STATUS']}", inline=True)

			embed.add_field(name="Active Since", value=f"{AO3Reply['ACTIVE_SINCE']}", inline=True)

			if AO3Reply['CONTACT'] is not None:
				embed.add_field(name="Contact", value=AO3Reply['CONTACT'], inline=True)

			embed.set_footer(text=f"Info retrieved by Summarium on {now.strftime('%a %-d at %X')}")

			return embed

	except:
		embed = Embed(
			title="Summarium Error",
			url=str(url),
			description=f"Can not get {url}",
			color=0x0000FF
		)

		return embed
