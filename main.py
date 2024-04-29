import re
import os

import discord
from utils import pattern_matcher, regex_strings
from constants import Site

from embed_messages.SH_Embed import ScribbleHubEmbed
from embed_messages.AO3_Embed import ao3_main
from embed_messages.FF_Embed import FanFictionDotNetEmbed
from embed_messages.FL_Embed import FictionDotLiveEmbed
from embed_messages.WN_Embed import WebNovelEmbed
from embed_messages.SB_Embed import SpaceBattlesEmbed

from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()

BOT_TOKEN = os.getenv("TOKEN")

description = """A discord bot that scrapes metadata from certain sites."""

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = discord.Bot(
    description=description, intents=intents, debug_guilds=[916010209221177385]
)


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
		|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7}
		[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]
		{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::
		[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]
		{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}
		|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]
		{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)
		|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]+|::(?:ffff(?::0{1,4})
		?:)?(?:(?:25[0-5]|(?:2[0-4]|1?[0-9])?[0-9])\.){3}
		(?:25[0-5]|(?:2[0-4]|1?}[0-9])?[0-9])|(?:[0-9a-fA-F]{1,4}:)
		{1,4}:(?:(?:25[0-5]|(?:2[0-4]|1?[0-9])?[0-9])\.){3}(?:25
		[0-5]|(?:2[0-4]|1?[0-9])?[0-9])))(?::[0-9]{1,4}|[1-5][0-9]
		{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?
		(?:/[\w\.-]*)*/?)\b
		""",
        message.content,
        re.VERBOSE,
    )

    for i in URLs:
        if pattern_matcher(regex_strings(Site.ScribbleHub), i):
            await message.reply(embed=ScribbleHubEmbed(i))
        elif pattern_matcher(regex_strings(Site.ArchiveOfOurOwn), i):
            await message.reply(embed=ao3_main(i))
        elif pattern_matcher(regex_strings(Site.FanFictionDotNet), i):
            await message.reply(
                file=FanFictionDotNetEmbed(i)[0], embed=FanFictionDotNetEmbed(i)[1]
            )
        elif pattern_matcher(regex_strings(Site.FictionLive), i):
            await message.reply(embed=FictionDotLiveEmbed(i))
        elif pattern_matcher(regex_strings(Site.WebNovel), i):
            await message.reply(embed=WebNovelEmbed(i))
        elif pattern_matcher(regex_strings(Site.SpaceBattles), i):
            await message.reply(embed=SpaceBattlesEmbed(i))


# Slash Commands
# ScribbleHub
@bot.command(
    name="scribblehub", description="Gets ScribbleHub Stories or Profiles metadata"
)
async def scribblehub(
    ctx,
    scribblehub_url: discord.Option(
        input_type=str,
        description="The ScribbleHub Stories" "/Profiles URL",
        required=True,
    ),
):
    await ctx.defer()
    await ctx.respond(embed=ScribbleHubEmbed(scribblehub_url))


# ArchiveOfOurOwn
@bot.command(
    name="archive_of_our_own",
    description="Gets ArchiveOfOurOwn story/series/collection metadata",
)
async def archive_of_our_own(
    ctx,
    ao3_url: discord.Option(
        input_type=str,
        description="The ArchiveOfOurOwn story/series/collection URL",
        required=True,
    ),
):
    await ctx.defer()
    await ctx.respond(embed=ao3_main(ao3_url))


# FanFiction.net
@bot.command(name="fanfictiondotnet", description="Gets FanFiction.Net story metadata")
async def fanfictiondotnet(
    ctx,
    ff_url: discord.Option(
        input_type=str, description="The FanFiction.Net story URL", required=True
    ),
):
    await ctx.defer()
    await ctx.respond(
        file=FanFictionDotNetEmbed(ff_url)[0], embed=FanFictionDotNetEmbed(ff_url)[1]
    )


# Fiction.live
@bot.command(name="fictiondotlive", description="Gets Fiction.Live story metadata")
async def fictiondotlive(
    ctx,
    fl_url: discord.Option(
        input_type=str, description="The Fiction.Live story URL", required=True
    ),
):
    await ctx.defer()
    await ctx.respond(embed=FictionDotLiveEmbed(fl_url))


# WebNovel
@bot.command(name="webnovel", description="Gets WebNovel story metadata")
async def webnovel(
    ctx,
    wn_url: discord.Option(
        input_type=str, description="The WebNovel story URL", required=True
    ),
):
    await ctx.defer()
    await ctx.respond(embed=WebNovelEmbed(wn_url))


# SpaceBattles
@bot.command(name="spacebattles", description="Gets SpaceBattles story metadata")
async def spacebattles(
    ctx,
    sb_url: discord.Option(
        input_type=str, description="The SpaceBattles story URL", required=True
    ),
):
    await ctx.defer()
    await ctx.respond(embed=SpaceBattlesEmbed(sb_url))


if __name__ == "__main__":
    keep_alive()
    bot.run(BOT_TOKEN)
