# Imports
import discord, os, time, glob, postbin, traceback
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv(verbose=True)

bot = commands.Bot(command_prefix=commands.when_mentioned_or('u!'), case_insensitive=True, allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=False))

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
	await bot.get_channel(755979601788010527).send(content=datetime.now().strftime("[%m/%d/%Y %I:%M:%S] ") + "Bot online")

@bot.event
async def on_command_error(ctx, error):
	errorchannel = bot.get_channel(764333133738541056)
	if isinstance(error, commands.TooManyArguments):
		await ctx.send('Too many arguments')
	elif isinstance(error, commands.NotOwner):
		await ctx.send('Nice try but you are not the owner.')
		await errorchannel.send(f"{ctx.author} tried to run `{ctx.command.qualified_name}`, but they are not owner.")
	elif isinstance(error, commands.CommandNotFound):
		await ctx.send(f'Not a command, <@{ctx.author.id}>')
	elif isinstance(error, commands.CheckFailure):
		await ctx.send(error)
	elif isinstance(error, commands.BadArgument):
		await ctx.send(f"There was an error parsing command arguments:\n`{error}`")
	else:
		tb = traceback.format_exception(type(error), error, error.__traceback__)
		url = await postbin.postAsync(content=tb)
		embed = discord.Embed(title="Oh no!", description=f"An error occured.\nIf you are a normal user, you may try and contact the developers.\nIf you are a dev, run with Jishaku debug to see the full error.\nError message: \n`{error}`", color=0xff1100)
		await ctx.send(embed=embed)
		await errorchannel.send(content=f"{ctx.author} tried to run {ctx.command.qualified_name}, but this error happened:\nHastebin: <{url}>", embed=embed)

@bot.event
async def on_message(message):
	if message.channel.id == 755982484444938290:
		for emoji in message.guild.emojis:
			if emoji.id == 755947356834365490:
				yes = emoji
			elif emoji.id == 755947345212080160:
				no = emoji
		await message.add_reaction(yes)
		await message.add_reaction(no)

	await bot.process_commands(message)

bot.load_extension("jishaku")
# bot.load_extension("riftgun")
# bot.load_extension("guildmanager")
# This loads all cogs in the directory, so I don't have to manually add cogs when I make/change them
os.chdir("cogs")
for file in glob.glob("*.py"):
	file = file.replace(".py", "")
	bot.load_extension(f"cogs.{file}")
bot.run(os.getenv("BOT_TOKEN"))
