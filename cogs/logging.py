import discord
from discord.ext import commands

class Logging(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="log")
	async def log(self, ctx):
		await ctx.send("Logging coming soon!")

def setup(bot):
	bot.add_cog(Loggging(bot))
	print('[LoggingCog] Logging cog loaded')