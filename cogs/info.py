import discord, random, asyncio
from discord.ext import commands

def randcolor():
	return int("%06x" % random.randint(0, 0xFFFFFF), 16)

class Info(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def ping(self, ctx):
		"""
		Get the bot's latency, in miliseconds.
		"""
		embed = discord.Embed(title="Ping!", description=f"Pong! `{round(self.bot.latency * 1000)} ms`", color=randcolor())
		await ctx.send(embed=embed)

	@commands.command()
	async def invite(self, ctx):
		"""
		Get the invite for the bot, and support server.
		"""
		embed = discord.Embed(title="Invite link", description="Click the links below to invite the bot to your server, or join our support server!\n[Click me to invite the bot!](https://discord.com/api/oauth2/authorize?client_id=755084857280954550&permissions=2147483639&redirect_uri=https%3A%2F%2Fdiscord.com&scope=bot)\n[Click me to join the support server!](https://discord.gg/Tbg3HDW)", color=randcolor())
		await ctx.send(embed=embed)
	
	@commands.command(name="botperms")
	async def _bot_permissions(self, ctx, channel_permissions="False"):
		"""
		Shows all of the bot's permissions, neatly sorted.

		channel_permissions = Whether or not to check the channel permissions, instead of the guild ones (default false)
		"""
		if channel_permissions.lower() == "true":
			perms = sorted([x for x,y in dict(ctx.me.permissions_in(ctx.channel)).items() if y])
			nice_perms = ""
			for perm in perms:
				nice_perms = nice_perms + "`" + perm.replace("_", " ").capitalize() + "`\n"
			await ctx.send(embed=discord.Embed(title="All of the bot's permissions in this channel:", description=nice_perms, color=randcolor()))
		elif channel_permissions.lower() == "false":
			perms = sorted([x for x,y in dict(ctx.me.guild_permissions).items() if y])
			nice_perms = ""
			for perm in perms:
				nice_perms = nice_perms + "`" + perm.replace("_", " ").capitalize() + "`\n"
			await ctx.send(embed=discord.Embed(title="All of the bot's permissions in this server:", description=nice_perms, color=randcolor()))

def setup(bot):
	bot.add_cog(Info(bot))
	print('[InfoCog] Info cog loaded')
