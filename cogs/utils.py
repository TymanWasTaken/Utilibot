import discord, random, asyncio
from discord.ext import commands

class Utils(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="allperms")
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def loop_channels(self, ctx, permission, state, role=None):
		"""
		Change permission overrides for all channels.
		"""
		if role is None:
			role = ctx.guild.default_role
		else:
			role = ctx.guild.get_role(int(role)) or role
		state = state.lower()
		permission = permission.lower()
		if state == "true":
			state = True
		elif state == "neutral":
			state = None
		elif state == "false":
			state = False
		else:
			return await ctx.send("State must be one of: True, Neutral, or False")
		for channel in ctx.guild.channels:
			await channel.set_permissions(role, **{permission: state})

def setup(bot):
	bot.add_cog(Utils(bot))
	print('[UtilsCog] Utils cog loaded')
