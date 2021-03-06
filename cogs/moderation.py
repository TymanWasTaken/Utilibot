import discord, random, asyncio, aiofiles, json, typing
from discord.ext import commands
async def readDB():
	try:
		async with aiofiles.open('/home/tyman/code/utilibot/data.json', mode='r') as f:
			return json.loads(await f.read())
	except Exception as e:
		print(f"An error occurred, {e}")

async def writeDB(data: dict):
	try:
		async with aiofiles.open('/home/tyman/code/utilibot/data.json', mode='r') as f_main:
			async with aiofiles.open('/home/tyman/code/utilibot/data.json.bak', mode='w') as f_bak:
				await f_bak.write(await f_main.read())
		async with aiofiles.open('/home/tyman/code/utilibot/data.json', mode='w') as f:
			d = json.dumps(data)
			await f.write(d)
	except Exception as e:
		print(f"An error occurred, {e}")

# PurgeError
class PurgeError(Exception):
	pass

# purge checks
def is_bot(m):
	return 	m.author.bot
def is_not_bot(m):
	return not m.author.bot

class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(invoke_without_command=True)
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.guild_only()
	async def purge(self, ctx, number: int=10):
		"""
		Purge a specified amount of messages from the current channel.
		Number = The number of messages to delete.
		"""
		if ctx.invoked_subcommand is None:
			async with ctx.typing():
				await ctx.message.delete()
				deleted = await ctx.channel.purge(limit=number)
			message = await ctx.channel.send(f'Deleted {len(deleted)} message(s)')
			await asyncio.sleep(2.5)
			await message.delete()

	@purge.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.guild_only()
	async def bot(self, ctx, number:int =10):
		"""
		Purge a specified amount of messages from the current channel. It will only delete messages made by bots.
		Number = The number of messages to delete.
		"""
		async with ctx.typing():
			await ctx.message.delete()
			deleted = await ctx.channel.purge(limit=number, check=is_bot)
		message = await ctx.channel.send(f'Deleted {len(deleted)} message(s)')
		await asyncio.sleep(2.5)
		await message.delete()

	@purge.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.guild_only()
	async def user(self, ctx, user: typing.Union[discord.User, int], number:int =10):
		"""
		Purge a specified amount of messages from the current channel. It will only delete messages made by the mentioned user.
		Number = The number of messages to delete.
		"""
		if isinstance(user, discord.User): is_user = lambda msg: msg.author.id == user.id
		else: is_user = lambda msg: msg.author.id == user
		
		async with ctx.typing():
			await ctx.message.delete()
			deleted = await ctx.channel.purge(limit=number, check=is_user)
		message = await ctx.channel.send(f'Deleted {len(deleted)} message(s)')
		await asyncio.sleep(2.5)
		await message.delete()

	@purge.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.guild_only()
	async def after(self, ctx, message: discord.Message, number:int =10):
		"""
		Purge a specified amount of messages from after a given message.
		Number = The number of messages to delete.
		"""
		async with ctx.typing():
			await ctx.message.delete()
			deleted = await ctx.channel.purge(limit=number, after=message)
		message = await ctx.channel.send(f'Deleted {len(deleted)} message(s)')
		await asyncio.sleep(2.5)
		await message.delete()

	@commands.command(name="kick", aliases=['yeet', 'boot'])
	@commands.bot_has_permissions(kick_members=True)
	@commands.has_permissions(kick_members=True)
	@commands.guild_only()
	async def kick(self, ctx, member: discord.Member, *, reason=None):
		"""
		Does what it says, kicks them from the server.
		"""
		if member.top_role >= ctx.author.top_role:
			await ctx.message.delete()
			await ctx.send("This user can't be kicked due to hierarchy.")
		else:
			await ctx.message.delete()
			await member.kick(reason=f"{member.name} was kicked by {ctx.author} ({ctx.author.id}), for the reason: {reason}")
			await ctx.send(f"Kicked {member} for the reason: `{reason}`")
			try:
				await member.send(f"You were kicked from {ctx.guild} for the reason: `{reason}`")
			except:
				await ctx.send(f"Error: Could Not DM user")

	@commands.command(name="ban", aliases=['bean', 'murder'])
	@commands.bot_has_permissions(ban_members=True)
	@commands.has_permissions(ban_members=True)
	@commands.guild_only()
	async def ban(self, ctx, user: typing.Union[discord.User, discord.Member], *, reason=None):
		"""
		Does what it says, bans them from the server.
		"""
		async def banfunc(ctx, user: typing.Union[discord.User, discord.Member], reason=None):
			await ctx.message.delete()
			await user.ban(reason=f"{user.name} was banned by {ctx.author} ({ctx.author.id}), for the reason: {reason}")
			await ctx.send(f"🔨 Banned {user} for the reason: `{reason}`")
			try:
				await user.send(f"You were banned from {ctx.guild} for the reason: `{reason}`")
			except discord.Forbidden:
				await ctx.send("Unable to message user.")

		if isinstance(user, discord.Member):
			if user.top_role >= ctx.author.top_role or user.top_role >= ctx.me.top_role:
				await ctx.send("This user can't be banned due to hierarchy.")
			else:
				await banfunc(ctx, user, reason)
		else:
			await banfunc(ctx, user, reason)
	"""
# too lazy to work on this right now, ty if you want to fix this go right ahead
	@commands.command(name="massban")
	@commands.bot_has_permissions(ban_members=True)
	@commands.has_permissions(ban_members=True)
	@commands.guild_only()
	async def massban(self, ctx, *users: typing.Union[discord.User, discord.Member], *, reason=None):
		
#		Bans a list of users from the server.
		
		async def massbanfunc(ctx, user: typing.Union[discord.User, discord.Member], reason=None):
			await ctx.message.delete()
			await user.ban(reason=f"{user.name} was banned by {ctx.author} ({ctx.author.id}), for the reason: {reason}")
			await ctx.send(f"🔨 Banned {user} for the reason: `{reason}`")
			try:
				await user.send(f"You were banned from {ctx.guild} for the reason: `{reason}`")
			except discord.Forbidden:
				await ctx.send("Unable to message user.")

		if isinstance(user, discord.Member):
			if user.top_role >= ctx.author.top_role or user.top_role >= ctx.me.top_role:
				await ctx.send("This user can't be banned due to hierarchy.")
			else:
				await banfunc(ctx, user, reason)
		else:
			await banfunc(ctx, user, reason)
	"""

	@commands.command(name="unban")
	@commands.bot_has_permissions(ban_members=True)
	@commands.has_permissions(ban_members=True)
	@commands.guild_only()
	async def unban(self, ctx, user: discord.User, *, reason=None):
		"""
		Unbans a user from the server.
		"""
		await ctx.message.delete()
		await user.unban(reason=f"{user.name} was unbanned by {ctx.author} ({ctx.author.id}), for the reason: {reason}")
		await ctx.send(f"Unbanned {user} for the reason: `{reason}`")
		try:
			await user.send(f"You were unbanned from {ctx.guild} for the reason: `{reason}``")
		except:
			await ctx.send("Could not DM user.")


	@commands.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_roles=True)
	@commands.guild_only()
	async def mute(self, ctx, member: discord.Member):
		"""
		Mutes a member so they cannot speak in the server. This command uses the first role it finds named "muted", ignoring case.
		"""
		# sure this is longer, but its easier to read
		muterole = discord.utils.find(lambda r: r.name.lower() == "muted", ctx.guild.roles) or await ctx.guild.create_role(name="Muted", color=0x757575, reason="Could not automatically detect a role named \"Muted\", so creating one to use.")
		#muterole = next((x for x in ctx.guild.roles if x.name.lower() == "muted"), None) or await ctx.guild.create_role(name="Muted", color=0x757575, reason="Could not automatically detect a role named \"Muted\", so creating one to use.")
		member.add_roles(muterole, reason=f"Member muted by {str(ctx.author)}")
		channels = [x for x in ctx.guild.channels if x.permissions_for(member).send_messages]  # whoever is doing this, please stop doing == and != to None, False and True.
													# None evals to False, so `if True` will work, `if None` or `if False` won't execute that block.
		if channels != []:
			await ctx.send(f"I have detected that {str(member)} still has permission to talk in some channels, attempting to apply a fix.")
			for channel in channels:
				# consider making this a task rather than waiting for it
				await channel.set_permissions(muterole, send_messages=False, reason="Applying overwrites for Muted role")
		await ctx.send(f"Successfully muted {str(member)}.")

def setup(bot):
	bot.add_cog(Moderation(bot))
	print('[ModerationCog] Utils cog loaded')
