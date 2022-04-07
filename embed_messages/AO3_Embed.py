from datetime import datetime

from discord import Embed
from scrapers.archiveofourown import archive_of_our_own

def ArchiveOfOurOwnEmbed(URL: str):
  try:
    time = datetime.utcnow()

    AO3Reply = archive_of_our_own(URL)

    # Dealing with limits
    AUTHOR_NAME = f"{AO3Reply['AUTHOR']}" if len(AO3Reply['AUTHOR']) <= 256 else f"{AO3Reply['AUTHOR'][:251]} ..."
    ARCHIVE_WARNING = f"{AO3Reply['ARCHIVE_WARNING']}" if len(AO3Reply['ARCHIVE_WARNING']) <= 250 else f"{AO3Reply['ARCHIVE_WARNING'][:245]} ..."
    FANDOM = f"{AO3Reply['FANDOM']}" if len(AO3Reply['FANDOM']) <= 250 else f"{AO3Reply['FANDOM'][:245]} ..."
    RELATIONSHIPS = f"{AO3Reply['RELATIONSHIPS']}" if len(AO3Reply['RELATIONSHIPS']) <= 135 else f"{AO3Reply['RELATIONSHIPS'][:130]} ..."
    CHARACTERS = f"{AO3Reply['CHARACTERS']}" if len(AO3Reply['CHARACTERS']) <= 135 else f"{AO3Reply['CHARACTERS'][:130]} ..."
    STATS = f"{AO3Reply['STATS']}" if len(AO3Reply['STATS']) <= 250 else f"{AO3Reply['STATS'][:245]} ..."
    # fields	Up to 25 field objects
    # field.name	256 characters
    # field.value	1024 characters
    # footer.text	2048 characters
    # author.name	256 characters

    #### Create the initial embed object ####
    embed=Embed(
      title=f"{AO3Reply['TITLE']}", 
      url=str(URL), 
      description=f"{AO3Reply['SUMMARY']}", 
      color=0xFF0000)

    # Add author, thumbnail, fields, and footer to the embed
    if len(AO3Reply['AUTHOR_LIST']) == 1:
      embed.set_author(
        name= AUTHOR_NAME, 
        url=f"{AO3Reply['AUTHOR_LINK']}", 
        icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")
      if AO3Reply['AUTHOR_IMAGE_LINK'].startswith('https://archiveofourown.org/'):
        embed.set_thumbnail(url=f"{AO3Reply['AUTHOR_IMAGE_LINK']}")
    else:
      embed.set_author(
        name="Archive Of Our Own", 
        url=URL,
        icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png"
      )
      embed.add_field(name="Authors", value=' • '.join(AO3Reply['AUTHOR_LIST']), inline=False)


    embed.add_field(name="Rating", value=f"{AO3Reply['RATING']}", inline=True)
    embed.add_field(name="Language", value=f"{AO3Reply['LANGUAGE']}", inline=True)
    
    embed.add_field(name="Archive Warnings", value=ARCHIVE_WARNING, inline=False)
    
    embed.add_field(name="Fandom", value=FANDOM, inline=False) 
    
    if AO3Reply['RELATIONSHIPS'] != 'N/A':
      embed.add_field(name="Relationships", value=RELATIONSHIPS, inline=False) 

    if AO3Reply['CHARACTERS'] != 'N/A':
      embed.add_field(name="Characters", value=CHARACTERS, inline=False) 
    
    embed.add_field(name="Stats", value=STATS, inline=False)

    embed.set_footer(text=f"Info retrieved by Summarium on {time.strftime('%a %-d at %X')}")

    return embed

  except Exception as e:
    return f'Oops! There was an error!\n{e}'