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
	@commands.has_permissions(administrator=True)
	@commands.bot_has_permissions(administrator=True)
	async def purge(self, ctx, number):
		number = int(number) #Converting the amount of messages to delete to an integer
		counter = 0
		async for x in bot.logs_from(ctx.message.channel, limit = number):
			if counter < number:
				await bot.delete_message(x)
				counter += 1
				await asyncio.sleep(1.2) #1.2 second timer so the deleting process can be even

def setup(bot):
	bot.add_cog(Utils(bot))
	print('[UtilsCog] Utils cog loaded')