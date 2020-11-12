import discord, random, asyncio, aiofiles, json, typing
from discord.ext import commands
async def readDB():
	try:
		async with aiofiles.open('/home/tyman/code/utilibot/data.json', mode='r') as f:
			return json.loads(await f.read())
	except Exception as e:
		print(f"An error occured, {e}")

async def writeDB(data: dict):
	try:
		async with aiofiles.open('/home/tyman/code/utilibot/data.json', mode='r') as f_main:
			async with aiofiles.open('/home/tyman/code/utilibot/data.json.bak', mode='w') as f_bak:
				await f_bak.write(await f_main.read())
		async with aiofiles.open('/home/tyman/code/utilibot/data.json', mode='w') as f:
			d = json.dumps(data)
			await f.write(d)
	except Exception as e:
		print(f"An error occured, {e}")

# PurgeError
class PurgeError(Exception):
	pass

# purge checks
def is_bot(m):
	return 	m.author.bot
def is_not_bot(m):
	return 	not(m.author.bot)
async def purge_messages(number, channel, mode, check=None):
	if check is None:
		return await channel.purge(limit=number)
	diff_message = 0
	total_message = 0
	async for message in channel.history(limit=None):
		if diff_message == number:
			break
		if check(message):
			diff_message += 1
		total_message += 1
	else:
		e = PurgeError(f'Could not find enough messages with mode {mode}')
		raise e

	return await channel.purge(limit=total_message, check=check)


class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.guild_only()
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

#	@purge.command()
#	@commands.has_permissions(manage_messages=True)
#	@commands.bot_has_permissions(manage_messages=True)
#	@commands.guild_only()
#	async def user(self, ctx, user: discord.Member, number:int =10):
#		"""
#		Purge a specified amount of messages from the current channel. It will only delete messages made by the mentioned user.
#
#		Number = The number of messages to delete.
#		"""
#		is_user = lambda msg: msg.author == user
#		async with ctx.typing():
#			await ctx.message.delete()
#			deleted = await ctx.channel.purge(limit=number, check=is_user)
#		message = await ctx.channel.send(f'Deleted {len(deleted)} message(s)')
#		await message.delete()

	@commands.command(name="kick")
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


	@commands.command(name="ban")
	@commands.bot_has_permissions(ban_members=True)
	@commands.has_permissions(ban_members=True)
	@commands.guild_only()
	async def ban(self, ctx, user: discord.User, *, reason=None):
		"""
		Does what it says, bans them from the server.
		"""
		def banfunc:
				await ctx.message.delete()
				await user.ban(reason=f"{user.name} was banned by {ctx.author} ({ctx.author.id}), for the reason: {reason}")
				await ctx.send(f"🔨 Banned {user} for the reason: `{reason}`")
				try:
					await user.send(f"🔨 You were banned from {ctx.guild} for the reason: `{reason}`")
				except:
					await ctx.send(f"Error: Could Not DM user")
		if user in ctx.guild.members:
			if user.top_role >= ctx.author.top_role:
				await ctx.send("This user can't be banned due to hierarchy.")
			else:
				banfunc
		else:
			banfunc



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
		await ctx.send(f"🔓 Unbanned {member} for the reason: `{reason}`")
		try:
			await user.send(f"🔓 You were unbanned from {ctx.guild} for the reason: `{reason}``")
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
		muterole = next((x for x in ctx.guild.roles if x.name.lower() == "muted"), None) or await ctx.guild.create_role(name="Muted", color=0x757575, reason="Could not automatically detect a role named \"Muted\", so creating one to use.")
		member.add_roles(muterole, reason=f"Member muted by {str(ctx.author)}")
		channels = [x for x in ctx.guild.channels if x.permissions_for(member).send_messages == True]
		if channels != []:
			await ctx.send(f"I have detected that {str(member)} still has permission to talk in some channels, attempting to apply a fix.")
			for channel in channels:
				await channel.set_permissions(muterole, send_messages=False, reason="Applying overwrites for Muted role")
		await ctx.send(f"Successfully muted {str(member)}.")

def setup(bot):
	bot.add_cog(Moderation(bot))
	print('[ModerationCog] Utils cog loaded')
