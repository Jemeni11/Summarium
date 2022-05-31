from dateutil import tz
from datetime import datetime
now = datetime.now(tz=tz.tzlocal())

from discord import Embed
from scrapers.fictionlive import fictiondotlive

def FictionDotLiveEmbed(URL: str):
  FLReply = fictiondotlive(URL)
  try:
    #### Create the initial embed object ####

    # Description has a limit of 4096 but I'm setting this to 380 characters.
    DESCRIPTION = FLReply['DESCRIPTION'] if len(FLReply['DESCRIPTION']) < 380 else f"{FLReply['DESCRIPTION'][:375]} ..."

    embed=Embed(
      title=FLReply['TITLE'], 
      url=URL, 
      description=DESCRIPTION, 
      color=0xFFFFFF)

    # Add author, thumbnail, fields, and footer to the embed
    embed.set_author(
      name=FLReply['AUTHOR'], 
      url=FLReply['AUTHOR_LINK'], 
      icon_url=FLReply['AUTHOR_IMAGE']
    )

    embed.set_thumbnail(url=FLReply['COVER_IMAGE'])

    if FLReply['AUTHOR_NOTE'] != ' ':
      embed.add_field(name="Author's Note", value=FLReply['AUTHOR_NOTE'], inline=False)
    
    if FLReply['STORY_STATUS'] != None:
      embed.add_field(name="Story Status", value=f"{FLReply['STORY_STATUS']}".capitalize(), inline=True)
    
    if FLReply['CONTENT_RATING'] != None:
      embed.add_field(
        name="Content Rating", 
        value=f"{FLReply['CONTENT_RATING'][0].title()}{FLReply['CONTENT_RATING'][1:]}", 
        inline=True
      )

    embed.add_field(
      name="Stats",
      value=
      f"""
        {FLReply['NOS_OF_CHAPTERS']} Chapters • {FLReply['NOS_OF_WORDS']} Words • \
          Updated on {FLReply['UPDATED']} • Created on {FLReply['PUBLISHED']}
      """,
      inline=False)

    embed.add_field(name="Tags", value=' • '.join(FLReply['TAGS']), inline=False)

    embed.set_footer(text=f"Info retrieved by Summarium on {now.strftime('%a %-d at %X')}")

    return embed

  except:
    embed=Embed(
      title="Summarium Error", 
      url=URL, 
      description=f"Can not get Fiction.live URL {URL}", 
      color=0x000000
    )

    return embed