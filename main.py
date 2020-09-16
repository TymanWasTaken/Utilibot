# Imports
import discord, os, time, glob
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv(verbose=True)

bot = commands.Bot(command_prefix=commands.when_mentioned_or('u!'), case_insensitive=True)

async def is_owner(ctx):
	return ctx.author.id == 487443883127472129

@bot.check
async def globally_block_dms(ctx):
	if ctx.guild is not None:
		return True
	else:
		await ctx.send("DM's are disabled, please use an actual server.")
		return False

@bot.event
async def on_ready():
	print(f'Bot logged in as {bot.user}')

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.TooManyArguments):
		await ctx.send('Too many arguments')
	elif isinstance(error, commands.NotOwner):
		await ctx.send('Nice try but you are not the owner.')
	elif isinstance(error, commands.CommandNotFound):
		await ctx.send(f'Not a command, <@{ctx.author.id}>')
	elif isinstance(error, commands.CheckFailure):
		await ctx.send(error)
	else:
		embed = discord.Embed(title="Oh no!", description="An error occured.\nIf you are a normal user, you may try and contact the developers.\nIf you are a dev, run with Jishaku debug to see the full error.", color=0xff1100)
		await ctx.send(embed=embed)

bot.load_extension("jishaku")
bot.load_extension("riftgun")
# This loads all cogs in the directory, so I don't have to manually add cogs when I make/change them
os.chdir("/home/pi/utilibot/cogs")
for file in glob.glob("*.py"):
	file = file.replace(".py", "")
	bot.load_extension(f"cogs.{file}")
bot.run(os.getenv("BOT_TOKEN"))
