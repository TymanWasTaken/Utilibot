import discord, random, asyncio
from discord.ext import commands

class Info(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def ping(self, ctx):
		"""
		Get the bot's latency, in miliseconds.
		"""
		color = "%06x" % random.randint(0, 0xFFFFFF)
		embed = discord.Embed(title="Ping!", description=f"Pong! `{round(self.bot.latency * 1000)} ms`", color=int(color, 16))
		await ctx.send(embed=embed)

	@commands.command()
	async def invite(self, ctx):
		"""
		Get the invite for the bot, and support server.
		"""
		color = "%06x" % random.randint(0, 0xFFFFFF)
		embed = discord.Embed(title="Invite link", description="Click the links below to invite the bot to your server, or join our support server!\n[Click me to invite the bot!](https://discord.com/api/oauth2/authorize?client_id=755084857280954550&permissions=2147483639&redirect_uri=https%3A%2F%2Fdiscord.com&scope=bot)\n[Click me to join the support server!](https://discord.gg/Tbg3HDW)", color=int(color, 16))
		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(Info(bot))
	print('[InfoCog] Info cog loaded')
