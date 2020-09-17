import discord, random, asyncio
from discord.ext import commands

def randcolor():
	return int("%06x" % random.randint(0, 0xFFFFFF), 16)

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
	
	@commands.command(name="permissions")
	async def permissions_from_value(self, ctx, value):
		"""
		Shows the permissions that correspond to a permissions value
		"""
		perms = discord.Permissions(permissions=int(value))
		perms_true = sorted([x for x,y in dict(perms).items() if y])
		perms_false = sorted([x for x,y in dict(perms).items() if not y])
		nice_perms = ""
		perms_true = ["\u2705 `" + s for s in perms_true]
		perms_false = ["\u274c `" + s for s in perms_false]
		perms_combined = sorted(perms_true + perms_false, key=lambda x: x.strip('\u2705\u274c'))
		for perm in perms_combined:
			nice_perms = nice_perms + perm.replace("_", " ").capitalize() + "`\n"
		await ctx.send(embed=discord.Embed(title=f"Permissions for value {value}:", description=nice_perms, color=randcolor()))

def setup(bot):
	bot.add_cog(Utils(bot))
	print('[UtilsCog] Utils cog loaded')
