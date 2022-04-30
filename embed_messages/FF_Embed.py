from dateutil import tz
from datetime import datetime
now = datetime.now(tz=tz.tzlocal())

from discord import Embed
from scrapers.fanfictionnet import fanfictiondotnet

def FanFictionDotNetEmbed(URL: str):
  FFReply = fanfictiondotnet(URL)
  try:
    # fields	Up to 25 field objects
    # field.name	256 characters
    # field.value	1024 characters
    # footer.text	2048 characters
    # author.name	256 characters

    #### Create the initial embed object ####
    embed=Embed(
      title=f"{FFReply['STORY_TITLE']}", 
      url=str(URL), 
      description=f"{FFReply['SYNOPSIS']}", 
      color=0x333399
    )

    # Add author, thumbnail, fields, and footer to the embed
    embed.set_author(
      name=f"{FFReply['AUTHOR']}", 
      url=f"{FFReply['AUTHOR_LINK']}", 
      icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png"
    )
    embed.set_thumbnail(url="https://archiveofourown.org/images/ao3_logos/logo_42.png")

    # if FFReply['AUTHOR_IMAGE_LINK'].startswith('https://'):
    #   embed.set_thumbnail(url=f"{FFReply['AUTHOR_IMAGE_LINK']}")

    if str(FFReply['CHARACTERS']).strip() != '':
      embed.add_field(name="Characters", value=str(FFReply['CHARACTERS']), inline=False)
    
    # Because why not?
    chapterstring = f"{FFReply['CHAPTERS']} chapter" if int(FFReply['CHAPTERS']) == 1 else f"{FFReply['CHAPTERS']} chapters"
    embed.add_field(name="Stats", value=f"**{FFReply['GENRE']}** • {FFReply['RATING']} • {FFReply['WORDS']} words • {chapterstring} • {FFReply['LANGUAGE']}", inline=False)

    embed.set_footer(text=f"Using the FicHub API for fanfiction.net\nInfo retrieved by Summarium on {now.strftime('%a %-d at %X')}")

    return embed

  except Exception as e:
    embed=Embed(
      title="Summarium Error", 
      url=str(URL), 
      description=f"Can not get {URL}", 
      color=0x333399
    )
    embed.set_footer(text=f"{e}")

    return embed
    # return None