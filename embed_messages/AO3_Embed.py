from discord import Embed
from scrapers.archiveofourown import archive_of_our_own

def ArchiveOfOurOwnEmbed(URL: str):
  try:
    SHReply = archive_of_our_own(URL)
    #### Create the initial embed object ####

    embed=Embed(
      title=f"{SHReply['STORY_TITLE']}", 
      url=str(URL), 
      description=f"{SHReply['SYNOPSIS']}", 
      color=0xE09319)

    # Add author, thumbnail, fields, and footer to the embed
    embed.set_author(
      name=f"{SHReply['AUTHOR']}", 
      url=f"{SHReply['AUTHOR_PROFILE_LINK']}", 
      icon_url=f"{SHReply['AUTHOR_AVATAR_LINK']}")

    embed.set_thumbnail(url=f"{SHReply['COVER_IMAGE']}")

    embed.add_field(name="Fandom", value=f"{SHReply['FANDOM']}", inline=False)
    
    embed.add_field(name="Content Warning", value=f"{SHReply['CONTENT_WARNING']}", inline=False)
    
    embed.add_field(name="Views", value=f"{SHReply['VIEWS']}", inline=True) 
    embed.add_field(name="Favourites", value=f"{SHReply['FAVOURITES']}", inline=True)
    embed.add_field(name="Chapter Count", value=f"{SHReply['CHAPTER_COUNT']}", inline=True)

    embed.add_field(name="Story Update Frequency", value=f"{SHReply['STORY_UPDATE_FREQUENCY']}", inline=True) 
    embed.add_field(name="Readers", value=f"{SHReply['READERS']}", inline=True) 

    embed.set_footer(text=f"{SHReply['GENRES']}")

    return embed
    # await message.reply(embed=embed)

  except Exception as e:
    return f'Oops! There was an error!\n{e}'