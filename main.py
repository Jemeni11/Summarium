# This example requires the 'members' and 'message_content' privileged intents

import re
import os

import discord
from discord import Embed
from discord.ext import commands

from embed_messages.SH_Embed import ScribbleHubEmbed
from embed_messages.AO3_Embed import ArchiveOfOurOwnEmbed
from embed_messages.FF_Embed import FanFictionDotNetEmbed
from embed_messages.FL_Embed import FictionDotLiveEmbed
from embed_messages.WN_Embed import WebNovelEmbed
from embed_messages.SB_Embed import SpaceBattlesEmbed

from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')

description = """A discord bot that scrapes metadata from certain sites."""

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
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

bot = discord.Bot(description=description, intents=intents, debug_guilds=[916010209221177385])


# bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))

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
		elif re.search(r'^https?://fiction\.live/(?:stories|Sci-fi)/([^\/]+|)/([0-9a-zA-Z\-]+)/?.*', i, re.IGNORECASE):
			await message.reply(embed=FictionDotLiveEmbed(i))
		elif re.search(r"(www|m)\.webnovel\.com/book/", i, re.IGNORECASE):
			await message.reply(embed=WebNovelEmbed(i))
		elif re.search(r"spacebattles\.com/threads/(([a-zA-Z%0-9]+-*)+\.[0-9]+)/", i, re.IGNORECASE):
			await message.reply(embed=SpaceBattlesEmbed(i))


# Slash Commands
# ScribbleHub
@bot.command(name="scribblehub", description="Gets ScribbleHub Stories or Profiles metadata")
async def scribblehub(ctx, scribblehub_url: discord.Option(input_type=str, description="The ScribbleHub Stories"
																					   "/Profiles URL", required=True)):
	await ctx.defer()
	await ctx.respond(embed=ScribbleHubEmbed(scribblehub_url))


# ArchiveOfOurOwn
@bot.command(name="archive_of_our_own", description="Gets ArchiveOfOurOwn story/series/collection metadata")
async def archive_of_our_own(ctx, ao3_url: discord.Option(input_type=str,
														  description="The ArchiveOfOurOwn story/series/collection URL"
	, required=True)):
	await ctx.defer()
	await ctx.respond(embed=ArchiveOfOurOwnEmbed(ao3_url))


# FanFiction.net
@bot.command(name="fanfictiondotnet", description="Gets FanFiction.Net story metadata")
async def fanfictiondotnet(ctx, ff_url: discord.Option(input_type=str, description="The FanFiction.Net story URL",
													   required=True)):
	await ctx.defer()
	await ctx.respond(file=FanFictionDotNetEmbed(ff_url)[0], embed=FanFictionDotNetEmbed(ff_url)[1])


# Fiction.live
@bot.command(name="fictiondotlive", description="Gets Fiction.Live story metadata")
async def fictiondotlive(ctx, fl_url: discord.Option(input_type=str, description="The Fiction.Live story URL",
													 required=True)):
	await ctx.defer()
	await ctx.respond(embed=FictionDotLiveEmbed(fl_url))


# WebNovel
@bot.command(name="webnovel", description="Gets WebNovel story metadata")
async def webnovel(ctx, wn_url: discord.Option(input_type=str, description="The WebNovel story URL", required=True)):
	await ctx.defer()
	await ctx.respond(embed=WebNovelEmbed(wn_url))


# SpaceBattles
@bot.command(name="spacebattles", description="Gets SpaceBattles story metadata")
async def spacebattles(ctx, sb_url: discord.Option(input_type=str, description="The SpaceBattles story URL", required=True)):
	await ctx.defer()
	await ctx.respond(embed=SpaceBattlesEmbed(sb_url))


@bot.command(name="allowall", description="Allow the bot to operate in all channels")
async def allow_all(ctx):
	"""Adds send_message perm for all the channels."""
	if not ctx.author.guild_permissions.administrator:
		await ctx.defer()
		try:
			return await ctx.send(
				embed=discord.Embed(
					description="You are missing Administrator permission to run this command."))
		except Exception as err:  # send a DM if send message perms is not enabled
			return await ctx.author.send(
				embed=discord.Embed(
					description="You are missing Administrator permission to run this command."))

	bot_user = ctx.guild.get_member(BOT_TOKEN)
	channel_list = ctx.guild.channels
	for channel in channel_list:
		try:
			await ctx.defer()
			await channel.set_permissions(
				bot_user,
				send_messages=True, manage_permissions=True)
		except Exception as err:
			print(err)

	embed = discord.Embed(
		description="The bot will now start responding to all the channels."
	)
	await ctx.defer()
	await ctx.channel.send(embed=embed)


@bot.command(name="disallowall", description="Disallow the bot from operating in all channels")
async def disallow_all(ctx):
	"""Removes send_message perm for all the channels."""

	await ctx.defer()
	if not ctx.author.guild_permissions.administrator:
		print(ctx.author)
		print(ctx.author.guild_permissions)
		print(ctx.author.guild_permissions.administrator)
		try:
			# send message in channel
			return await ctx.send(
				embed=Embed(description="You are missing Administrator permission to run this command."))
		except Exception as err:  # send a DM if send message perms is not enabled
			return await ctx.author.send(
				embed=Embed(description="You are missing Administrator permission to run this command."))

	embed = Embed(description="The bot will now stop responding to all the channels.")
	try:
		await ctx.channel.send(embed=embed)
	except Exception as err:
		embed = Embed(description=
					  "The bot is not allowed to send messages in that channel. "
					  "Ask one of the server admins to use the `,allow` command in that channel to enable it."
					  )
		await ctx.author.send(embed=embed)

	bot_user = bot.user
	channel_list = ctx.guild.channels
	for channel in channel_list:
		try:
			await ctx.defer()
			await channel.set_permissions(
				bot_user,
				send_messages=False, manage_permissions=True)
		except Exception as err:
			print("line201", err)


if __name__ == '__main__':
	keep_alive()
	bot.run(BOT_TOKEN)
