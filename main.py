# Imports
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv(verbose=True)
import os
import time

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
	elif isinstance(error, commands.CommandNotFound):
		await ctx.send('Not a command!')
	else:
		pass

class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def hello(self, ctx):
		await ctx.send("Hello there.")

class Utils(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def ping(self, ctx):
		embed = discord.Embed(title="Ping!", description=f"Pong! `{round(self.bot.latency * 1000)} ms`", color=0x3bff00)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.check(is_owner)
	async def quit(self, ctx):
		await ctx.send('Shutting down...')
		print('Recived quit command, shutting down.')
		await bot.logout()
		sys.exit()

bot.load_extension("jishaku")
bot.load_extension("riftgun")
bot.add_cog(Fun(bot))
bot.add_cog(Utils(bot))
bot.run(os.getenv("BOT_TOKEN"))
