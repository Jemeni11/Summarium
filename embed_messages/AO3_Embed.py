from dateutil import tz
from datetime import datetime
now = datetime.now(tz=tz.tzlocal())

from discord import Embed
from scrapers.archiveofourown import archive_of_our_own

def ArchiveOfOurOwnEmbed(URL: str):
  AO3Reply = archive_of_our_own(URL)
  try:
    if AO3Reply['LINK_TYPE'] == 'STORY':
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
        if AO3Reply['AUTHOR_IMAGE_LINK'].startswith('https://'):
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
      
      if len(AO3Reply['SERIES']):
        embed.add_field(name="Series", value=' • '.join(AO3Reply['SERIES']), inline=False)

      embed.add_field(name="Stats", value=STATS, inline=False)

      embed.set_footer(text=f"Info retrieved by Summarium on {now.strftime('%a %-d at %X')}")

      return embed

    elif AO3Reply['LINK_TYPE'] == 'SERIES':
      # Dealing with limits
      # Series Title* [240 characters left]
      # Description: [1250 characters left]
      # Notes: [5000 characters left]
      AUTHOR_NAME = f"{AO3Reply['AUTHOR']}" if len(AO3Reply['AUTHOR']) <= 256 else f"{AO3Reply['AUTHOR'][:251]} ..."
      if AO3Reply['DESCRIPTION'] != None:
        DESCRIPTION = f"{AO3Reply['DESCRIPTION']}" if len(AO3Reply['DESCRIPTION']) <= 300 else f"{AO3Reply['DESCRIPTION'][:295]} ..."
      else:
        DESCRIPTION = 'No description available'
      if AO3Reply['NOTES'] != None:
        NOTES = f"{AO3Reply['NOTES']}" if len(AO3Reply['NOTES']) <= 300 else f"{AO3Reply['NOTES'][:295]} ..."
      else:
        NOTES = 'No Notes available'

      #### Create the initial embed object ####
      embed=Embed(
        title=f"{AO3Reply['SERIES_TITLE']}", 
        url=str(URL), 
        description=DESCRIPTION, 
        color=0xFF0000)

      # Add author, thumbnail, fields, and footer to the embed
      if len(AO3Reply['AUTHOR_LIST']) == 1:
        embed.set_author(
          name= AUTHOR_NAME, 
          url=f"{AO3Reply['AUTHOR_LINK']}", 
          icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")
        if AO3Reply['AUTHOR_IMAGE_LINK'].startswith('https://'):
          embed.set_thumbnail(url=f"{AO3Reply['AUTHOR_IMAGE_LINK']}")
      else:
        AUTHORS_ARR = ' • '.join(AO3Reply['AUTHOR_LIST']) if len(' • '.join(AO3Reply['AUTHOR_LIST'])) <= 1024 else f"{' • '.join(AO3Reply['AUTHOR_LIST'])[:1019]} ..."
        AUTHORS_ARR_SPLIT = AUTHORS_ARR.split('•')
        del AUTHORS_ARR_SPLIT[-1]
        AUTHORS = f"{' • '.join(AUTHORS_ARR_SPLIT)} ..."
        embed.set_author(
          name="Archive Of Our Own", 
          url=URL,
          icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png"
        )
        embed.add_field(name="Authors", value=AUTHORS, inline=False)

      embed.add_field(name="Series Begun", value=f"{AO3Reply['SERIES_BEGUN']}", inline=True)
      embed.add_field(name="Series Updated", value=f"{AO3Reply['SERIES_UPDATED']}", inline=True)

      embed.add_field(name="Notes", value=NOTES, inline=False) 

      embed.add_field(name="Stats", value=AO3Reply['STATS'], inline=False)

      embed.set_footer(text=f"Info retrieved by Summarium on {now.strftime('%a %-d at %X')}")

      return embed

    elif AO3Reply['LINK_TYPE'] == 'COLLECTION':
      MAIN_LT = AO3Reply['MAINTAINERS_LIST']

      #### Create the initial embed object ####
      embed=Embed(
        title=f"{AO3Reply['STORY_TITLE_TEXT']}", 
        url=str(URL), 
        description=AO3Reply['SUMMARY'], 
        color=0xFF0000)

      # Add author, thumbnail, fields, and footer to the embed
      if AO3Reply['IMAGE'].startswith('https://'):
        embed.set_thumbnail(url=AO3Reply['IMAGE'])
      if len(MAIN_LT) == 1:
        embed.set_author(
          name= AO3Reply['AUTHOR'], 
          url=f"{AO3Reply['AUTHOR_LINK']}", 
          icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")
      else:
        if len(' • '.join(MAIN_LT)) > 1024:
          AUTHORS_ARR = f"{' • '.join(MAIN_LT)[:1019]} ..."
          AUTHORS_ARR_SPLIT = AUTHORS_ARR.split('•')
          del AUTHORS_ARR_SPLIT[-1]
          AUTHORS = f"{' • '.join(AUTHORS_ARR_SPLIT)} ..."
        else:
          AUTHORS = ' • '.join(MAIN_LT)
        embed.set_author(
          name="Archive Of Our Own", 
          url=URL,
          icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png"
        )
        embed.add_field(name="Authors", value=AUTHORS, inline=False)


      if AO3Reply['INTRO'] != None:
        INTRO = f"{AO3Reply['INTRO']}" if len(AO3Reply['INTRO']) <= 300 else f"{AO3Reply['INTRO'][:295]} ..."
        embed.add_field(name="Intro",value=INTRO, inline=False)
      
      if AO3Reply['RULES'] != None:
        RULES = f"{AO3Reply['RULES']}" if len(AO3Reply['RULES']) <= 300 else f"{AO3Reply['RULES'][:295]} ..."
        embed.add_field(name="Rules",value=RULES, inline=False)
      
      embed.add_field(name="Status", value=f"{AO3Reply['STATUS']}", inline=True)
      
      embed.add_field(name="Active Since", value=f"{AO3Reply['ACTIVE_SINCE']}", inline=True)

      if AO3Reply['CONTACT'] != None:
        embed.add_field(name="Contact", value=AO3Reply['CONTACT'], inline=True) 

      embed.set_footer(text=f"Info retrieved by Summarium on {now.strftime('%a %-d at %X')}")

      return embed

  except Exception as e:
    embed=Embed(
      title="Summarium Error", 
      url=str(URL), 
      description=f"Can not get {URL}", 
      color=0xFF0000
    )
    embed.set_footer(text=f"{e}")

    return embed