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

	@commands.command()
	async def say(self, ctx, *, message):
		"""
		Says what you tell it to, self-explanitory
		"""
		await ctx.send(message)

def setup(bot):
	bot.add_cog(Fun(bot))
	print('[FunCog] Fun cog loaded')