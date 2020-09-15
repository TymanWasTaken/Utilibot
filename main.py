import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv(verbose=True)
import os

bot = commands.Bot(command_prefix=commands.when_mentioned_or('u!'), case_insensitive=True)

async def is_owner(ctx):
    return ctx.author.id == 487443883127472129

@bot.event
async def on_ready():
    print('Bot logged in as {0.user}'.format(bot))
    
@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.TooManyArguments):
    await ctx.send('Too many arguments')
  elif isinstance(error, commands.NotOwner):
    await ctx.send('Nice try but you are not the owner.')
  else:
    pass

bot.load_extension("jishaku")
bot.load_extension("cogs.utils")
bot.run(os.getenv("BOT_TOKEN"))