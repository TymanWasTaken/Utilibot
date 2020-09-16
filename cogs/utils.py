import discord, random, asyncio
from discord.ext import commands

class Utils(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def ping(self, ctx):
		color = "%06x" % random.randint(0, 0xFFFFFF)
		embed = discord.Embed(title="Ping!", description=f"Pong! `{round(self.bot.latency * 1000)} ms`", color=int(color, 16))
		await ctx.send(embed=embed)

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	async def purge(self, ctx, number):
		deleted = await ctx.channel.purge(limit=int(number)+1)
		message = await ctx.channel.send(f'Deleted {len(deleted)-1} message(s)')
		await asyncio.sleep(2.5)
		await message.delete()

def setup(bot):
	bot.add_cog(Utils(bot))
	print('[UtilsCog] Utils cog loaded')
