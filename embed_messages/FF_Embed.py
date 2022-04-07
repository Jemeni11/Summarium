from datetime import datetime

from discord import Embed
from scrapers.fanfictionnet import fanfictionnet

def ArchiveOfOurOwnEmbed(URL: str):
  try:
    time = datetime.utcnow()

    FFReply = fanfictionnet(URL)
    #### Create the initial embed object ####

    embed=Embed(
      title=f"{FFReply['TITLE']}", 
      url=str(URL), 
      description=f"{FFReply['SUMMARY']}", 
      color=0xFF0000)

    AUTHOR_NAME = f"{FFReply['AUTHOR']}" if FFReply <= 256 else f"{FFReply['AUTHOR'][:-5]} ..."
    # Add author, thumbnail, fields, and footer to the embed
    embed.set_author(
      name= AUTHOR_NAME, 
      url=f"{FFReply['AUTHOR_LINK']}", 
      icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")

    # embed.set_thumbnail(url=f"{FFReply['COVER_IMAGE']}")

    embed.add_field(name="Rating", value=f"{FFReply['RATING']}", inline=False)
    
    embed.add_field(name="Archive Warnings", value=f"{FFReply['ARCHIVE_WARNING']}", inline=False)
    
    embed.add_field(name="Fandom", value=f"{FFReply['FANDOM']}", inline=False) 
    
    if FFReply['RELATIONSHIPS'] != 'N/A':
      embed.add_field(name="Relationships", value=f"{FFReply['RELATIONSHIPS']}", inline=False) 

    if FFReply['CHARACTERS'] != 'N/A':
      embed.add_field(name="Characters", value=f"{FFReply['CHARACTERS']}", inline=False) 

    embed.add_field(name="Language", value=f"{FFReply['LANGUAGE']}", inline=False)
    
    embed.add_field(name="Stats", value=f"{FFReply['STATS']}", inline=False)

    embed.set_footer(text=f"Info retrieved by Summarium on {time.strftime('%a %-d at %X')}")

    return embed

  except Exception as e:
    return f'Oops! There was an error!\n{e}'