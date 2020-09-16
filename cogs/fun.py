import discord
from discord.ext import commands

class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def hello(self, ctx):
		"""
		:)
		"""
		await ctx.send("Hello there.")

def setup(bot):
	bot.add_cog(Fun(bot))
	print('[FunCog] Fun cog loaded')