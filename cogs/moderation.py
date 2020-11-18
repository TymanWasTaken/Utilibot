import discord, random, asyncio
from discord.ext import commands

# PurgeError
class PurgeError(Exception):
	pass

# purge checks
def is_bot(m):
	return 	m.author.bot
def is_not_bot(m):
	return not m.author.bot
async def purge_messages(number, channel, mode, check=None):
	#WARNING!
	# THE WAY YOU CHECK HISTORY HERE IS VERY RATELIMIT HEAVY
	# ID CONSIDER SOME OTHER METHOD
	if check is None:
		return await channel.purge(limit=number)
# 	diff_message = 0
	total_message = 0
	"""
	async for message in channel.history(limit=None):
		if diff_message == number:
			break
		if check(message):
			diff_message += 1
		total_message += 1
	else:
		e = PurgeError(f'Could not find enough messages with mode {mode}')
		raise e
	"""
	# This entire section has no use, you don't use "diff_message" at any point
	return await channel.purge(limit=total_message, check=check)


class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	async def purge(self, ctx, number, mode="all"):
		"""
		Purge a specified amount of messages from the current channel.

		Number = The number of messages to delete, depending on the mode. If the mode is all, it will just delete this number of messages. If the mode is bot, it will delete this number of messages made by bots.
		Mode = The mode of deleteing messages, can be all (defualt), bot, or humans (opposite of bot)
		"""
		await ctx.message.delete()
		mode = str(mode).lower()
		number = int(number)
		try:
			if mode == "all":
				deleted = await purge_messages(number, ctx.channel, mode)
			elif mode == "bot":
				deleted = await purge_messages(number, ctx.channel, mode, is_bot)
			elif mode == "human":
				deleted = await purge_messages(number, ctx.channel, mode, is_not_bot)
			else:
				return await ctx.send('Mode must be one of: all (default), bot, or human')
		except PurgeError as e:
			return await ctx.send(e)

		message = await ctx.channel.send(f'Deleted {len(deleted)} message(s)')
		await asyncio.sleep(2.5)
		await message.delete()
	

	@commands.command(name="kick")
	@commands.bot_has_guild_permissions(kick_members=True)
	@commands.has_permissions(kick_members=True)
	async def kick(self, ctx, member: discord.Member, *, reason=None):
		"""
		Does what it says, kicks them from the server.
		"""
		if member.top_role >= ctx.author.top_role:
			await ctx.message.delete()
			await ctx.send("This user can't be kicked due to hierachry.")
		else:
			await ctx.message.delete()
			try:
				await member.send(f"You were banned from {ctx.guild} for the reason: `{reason}`")
			except discord.Forbidden:
				await ctx.send("Unable to message user.")
			await member.kick(reason=f"{member.name} was kicked by {ctx.author.name}, for the reason: {reason}")
			await ctx.send(f"Kicked {member} for the reason: `{reason}`")
	
	@commands.command(name="ban")
	@commands.bot_has_guild_permissions(ban_members=True)
	@commands.has_permissions(ban_members=True)
	async def ban(self, ctx, member: discord.Member, *, reason=None):
		"""
		Does what it says, bans them from the server.
		"""
		if member.top_role >= ctx.author.top_role or member.top_role >= ctx.me.top_role:
			await ctx.send("This user can't be banned due to hierachry.")
		else:
			await ctx.message.delete()
			try:
				await member.send(f"You were banned from {ctx.guild} for the reason: `{reason}`")
			except discord.Forbidden:
				await ctx.send("Unable to message user.")
			await member.ban(reason=f"{member.name} was banned by {ctx.author.name}, for the reason: {reason}")
			await ctx.send(f"Banned {member} for the reason: `{reason}`")

def setup(bot):
	bot.add_cog(Moderation(bot))
	print('[ModerationCog] Utils cog loaded')
