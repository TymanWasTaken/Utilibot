import discord
from discord.ext import commands

async def is_owner(ctx):
	return ctx.author.id == 487443883127472129

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

def setup(bot):
    bot.add_cog(Utils(bot))