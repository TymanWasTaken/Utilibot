import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv(verbose=True)
import os

client = discord.Client()

@client.event
async def on_ready():
	print('Bot logged in as {0.user}'.format(client))

bot = commands.Bot(command_prefix='u!')

@bot.command
async def ping(ctx):
	await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))

client.run(os.getenv("BOT_TOKEN"))