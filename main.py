# This example requires the 'members' and 'message_content' privileged intents

import random
import re

import discord
from discord.ext import commands

from embed_messages.SH_Embed import ScribbleHubEmbed
from embed_messages.AO3_Embed import ArchiveOfOurOwnEmbed

description = """An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here."""

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="?", description=description, intents=intents)


@bot.event
async def on_ready():
  print(f"Logged in as {bot.user} (ID: {bot.user.id})")
  print("------")

@bot.event
async def on_message(message):
  if message.author.id == bot.user.id:
    return

  if message.author.bot:
    return  # Do not reply to other bots

  if re.search(r"(^https://www\.scribblehub\.com/(series|read))/\d+", message.content):
    await message.reply(embed=ScribbleHubEmbed(message.content))
  elif re.search(r"", message.content):
    await message.reply(embed=ArchiveOfOurOwnEmbed(message.content))

@bot.command()
async def add(ctx, left: int, right: int):
  """Adds two numbers together."""
  await ctx.send(left + right)


@bot.command()
async def roll(ctx, dice: str):
  """Rolls a dice in NdN format."""
  try:
    rolls, limit = map(int, dice.split("d"))
  except Exception:
    await ctx.send("Format has to be in NdN!")
    return

  result = ", ".join(str(random.randint(1, limit)) for r in range(rolls))
  await ctx.send(result)


@bot.command(description="For when you wanna settle the score some other way")
async def choose(ctx, *choices: str):
  """Chooses between multiple choices."""
  await ctx.send(random.choice(choices))


@bot.command()
async def repeat(ctx, times: int, content="repeating..."):
  """Repeats a message multiple times."""
  for _ in range(times):
    await ctx.send(content)

  
@bot.command()
async def joined(ctx, member: discord.Member):
  """Says when a member joined."""
  await ctx.send(f"{member.name} joined in {member.joined_at}")


@bot.group()
async def cool(ctx):
  """Says if a user is cool.
  In reality this just checks if a subcommand is being invoked.
  """
  if ctx.invoked_subcommand is None:
    await ctx.send(f"No, {ctx.subcommand_passed} is not cool")


@cool.command(name="bot")
async def _bot(ctx):
  """Is the bot cool?"""
  await ctx.send("Yes, the bot is cool.")

bot.run('OTU5NDM5MDYxNjgzMTU5MTMx.Ykb5QQ.ATcpX4nZFWQCt--OFdP4wMr2q64')