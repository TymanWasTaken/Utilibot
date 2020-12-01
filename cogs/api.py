import discord, random, datetime, asyncio, fastapi
from fastapi import FastApi
from discord.ext import commands
from discord.ext import tasks

class web(commands.Cog):

	def get_app(self, bot):
		app = FastAPI()

		app.mount("/", StaticFiles(directory="web/static"), name="static")

	def __init__(self, bot):
		self.bot = bot
		self.app = self.get_app(bot)

def setup(bot):
	bot.add_cog(web(bot))
	print('[web] web cog loaded')