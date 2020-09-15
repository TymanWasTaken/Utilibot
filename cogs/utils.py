import discord
from discord.ext import commands

class Utils(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		
	@commands.command()
	async def ping(self, ctx):
		await ctx.send('Pong! {0}'.format(bot.latency * 1000 + " Seconds"))

def setup(bot):
    bot.add_cog(Utils(bot))