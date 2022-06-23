# This example requires the 'members' and 'message_content' privileged intents

import re
import os

import discord
from discord.ext import commands

from embed_messages.SH_Embed import ScribbleHubEmbed
from embed_messages.AO3_Embed import ArchiveOfOurOwnEmbed
from embed_messages.FF_Embed import FanFictionDotNetEmbed
from embed_messages.FL_Embed import FictionDotLiveEmbed

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')

description = """An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here."""

intents = discord.Intents.default()
intents.members = True
# intents.message_content = True 
"""
This worked perfectly about an hour ago and now it throws the following error:

(virtualenv) nonso@HPEnvy:~/Documents/Code/Projects/Summarium$ python3 main.py 
Traceback (most recent call last):
  File "main.py", line 25, in <module>
    intents.message_content = True
AttributeError: 'Intents' object has no attribute 'message_content'
(virtualenv) nonso@HPEnvy:~/Documents/Code/Projects/Summarium$

So I commented that line out and ran my code again and it worked 
somehow even though it shouldn't.
Putting this comment here incase it causes chaos later on.
"""

bot = commands.Bot(command_prefix="?", description=description, intents=intents)


@bot.event
async def on_ready():
	print(f"Logged in as {bot.user} (ID: {bot.user.id})")
	print("____________________________________________")


@bot.event
async def on_message(message):
	if message.author.id == bot.user.id:
		return

	if message.author.bot:
		return  # Do not reply to other bots

	# Pulling out all URLs
	URLs = re.findall(
		r"""
		\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})
		|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]
		|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}
		[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]
		{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::
		[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]
		{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}
		|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]
		{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)
		|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4})
		{0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}
		(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:)
		{1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25
		[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]
		{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?
		(?:/[\w\.-]*)*/?)\b
		""",
		message.content, re.VERBOSE)

	for i in URLs:
		if re.search(r"(^https://www\.scribblehub\.com/(series|read|profile))/\d+", i, re.IGNORECASE):
			await message.reply(embed=ScribbleHubEmbed(i))
		elif re.search(r"^https://archiveofourown\.org/(\bseries\b|\bworks\b|\bcollections\b)/", i, re.IGNORECASE):
			await message.reply(embed=ArchiveOfOurOwnEmbed(i))
		elif re.search(r"^https://(www|m)\.(\bfanfiction\b\.\bnet\b)/s/\d+/\d+/\w*", i, re.IGNORECASE):
			await message.reply(file=FanFictionDotNetEmbed(i)[0], embed=FanFictionDotNetEmbed(i)[1])
		elif re.search(r'^https?://fiction\.live/(?:stories|Sci-fi)/[^\/]+/([0-9a-zA-Z\-]+)/?.*', i, re.IGNORECASE):
			await message.reply(embed=FictionDotLiveEmbed(i))

if __name__ == '__main__':
	bot.run(BOT_TOKEN)
