from datetime import datetime

from discord import Embed
from scrapers.scribblehub import scribble_hub

def ScribbleHubEmbed(URL: str):
  try:
    time = datetime.utcnow()

    SHReply = scribble_hub(URL)
    #### Create the initial embed object ####

    # Description has a limit of 4096 but I'm setting this to 500 characters.
    Description = SHReply['SYNOPSIS'] if len(SHReply['SYNOPSIS']) < 500 else f"{SHReply['SYNOPSIS'][:495]} ..."

    embed=Embed(
      title=f"{SHReply['STORY_TITLE']}", 
      url=str(URL), 
      description=Description, 
      color=0xE09319)

    # Add author, thumbnail, fields, and footer to the embed
    embed.set_author(
      name=f"{SHReply['AUTHOR']}", 
      url=f"{SHReply['AUTHOR_PROFILE_LINK']}", 
      icon_url=f"{SHReply['AUTHOR_AVATAR_LINK']}")

    embed.set_thumbnail(url=f"{SHReply['COVER_IMAGE']}")

    embed.add_field(name="Fandom", value=f"{SHReply['FANDOM']}", inline=False)
    
    embed.add_field(name="Content Warning", value=f"{SHReply['CONTENT_WARNING']}", inline=False)
    
    embed.add_field(
      name="Stats",
      value=
      f"""
        {SHReply['VIEWS']} • {SHReply['FAVOURITES']} • {SHReply['CHAPTER_COUNT']} • {SHReply['STORY_UPDATE_FREQUENCY']} • {SHReply['READERS']}
      """,
      inline=False)

    embed.add_field(name="Genres", value=f"{SHReply['GENRES']}", inline=False)

    embed.set_footer(text=f"Info retrieved by Summarium on {time.strftime('%a %-d at %X')}")

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