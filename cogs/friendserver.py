import discord, asyncio, aiohttp, pytz, datetime
from discord.ext import commands

class FriendServer(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

def setup(bot):
	cog = FriendServer(bot)
	bot.add_cog(cog)
	print('[FriendServer] FriendServer cog loaded')