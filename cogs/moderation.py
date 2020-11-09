import discord, random, asyncio, aiofiles, json
from discord.ext import commands

# PurgeError
class PurgeError(Exception):
	pass

# purge checks
def is_bot(m):
	return 	m.author.bot
def is_not_bot(m):
	return 	not(m.author.bot)

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
	async def user(self, ctx, user: discord.Member, number:int =10):
		"""
		Purge a specified amount of messages from the current channel. It will only delete messages made by the mentioned user.

		Number = The number of messages to delete.
		"""
		is_user = lambda msg: msg.author == user
		async with ctx.typing():
			await ctx.message.delete()
			deleted = await ctx.channel.purge(limit=number, check=is_user)
		message = await ctx.channel.send(f'Deleted {len(deleted)} message(s)')
		await asyncio.sleep(2.5)
		await message.delete()

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
			await ctx.send("This user can't be kicked due to hierachry.")
		else:
			await ctx.message.delete()
			try:
				await member.send(f"You were kicked from {ctx.guild} for the reason: `{reason}`")
				await member.kick(reason=f"{member.name} was kicked by {ctx.author.name}, for the reason: {reason}")
				await ctx.send(f"Kicked {member} for the reason: `{reason}`")
			except:
				await ctx.send(f"Eror: Could Not DM user")
				await member.kick(reason=f"{member.name} was kicked by {ctx.author.name}, for the reason: {reason}")
				await ctx.send(f"Kicked {member} for the reason: `{reason}`")

	@commands.command(name="hardlock", aliases=['lockdown', 'hl', 'ld'])
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True)
	async def hardlock(self, ctx):
		"""
		Locks down a channel by denying @everyone send messages permission.
		"""
		perms = ctx.channel.overwrites_for(ctx.guild.default_role)
		perms.send_messages = False
		await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=perms, reason=f"Channel locked by {ctx.author.name}#{ctx.author.discriminator}!")
		await ctx.send(f"Successfully locked down <#{ctx.channel.id}> by removing send messages permission for @everyone.", allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))
		
	@commands.command(name="unhardlock", aliases=['unlockdown', 'uhl', 'uld'])
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True)
	async def unhardlock(self, ctx):
		"""
		Unlocks a channel by setting @everyone's send message permissions to neutral
		"""
		perms = ctx.channel.overwrites_for(ctx.guild.default_role)
		perms.send_messages = None
		await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=perms, reason=f"Channel unlocked by {ctx.author.name}#{ctx.author.discriminator}!")
		await ctx.send(f"Successfully unlocked <#{ctx.channel.id}>!)

	@commands.command(name="softlock", aliases=['lock', 'sl'])
	@commands.bot_has_permissions(manage_messages=True)
	@commands.has_permissions(manage_messages=True)
	async def softlock(self, ctx, channel: discord.TextChannel=None, *, reason=None):
		"""
		Locks down a channel by deleting messages that people send.
		"""
		db = await readDB()
		ch = channel or ctx.channel
		if not str(ch.id) in db["softlocked_channels"]:
			db["softlocked_channels"][str(ch.id)] = {
				"user": str(ctx.author.id),
				"reason": reason or "No reason provided.",
				"whitelist": []
			}
			await writeDB(db)
			await ctx.send("Successfully softlocked.")
		else:
			await ctx.send("Channel is already softlocked.")

	@commands.command(aliases=['wh'])
	@commands.bot_has_permissions(manage_messages=True)
	@commands.has_permissions(manage_messages=True)
	async def whitelist(self, ctx, user: discord.Member):
		"""
		Whitelists a user from the softlock in the current channel, allowing them to speak but not unlock.
		"""
		db = await readDB()
		if not str(ctx.channel.id) in db["softlocked_channels"]:
			return await ctx.send("This channel is not softlocked")
		elif not db["softlocked_channels"][str(ctx.channel.id)]["user"] == str(ctx.author.id):
			return await ctx.send("You did not softlock this channel")
		else:
			db["softlocked_channels"][str(ctx.channel.id)]["whitelist"].append(user.id)
			await writeDB(db)
			return await ctx.send(f"Successfully whitelisted {str(user)}")

	@commands.command(name="unsoftlock", aliases=['unlock', 'usl'])
	@commands.bot_has_permissions(manage_messages=True)
	@commands.has_permissions(manage_messages=True)
	async def unsoftlock(self, ctx, channel: discord.TextChannel=None):
		"""
		Unsoftlocks a channel.
		"""
		db = await readDB()
		ch = channel or ctx.channel
		if str(ch.id) in db["softlocked_channels"]:
			if db["softlocked_channels"][str(ch.id)]["user"] == str(ctx.author.id):
				del db["softlocked_channels"][str(ch.id)]
				await writeDB(db)
				await ctx.send("Successfully unsoftlocked.")
			else:
				await ctx.send("You cannot unlock this, as you are not the one who locked it.")
		else:
			await ctx.send("Channel is not softlocked.")
	
	@commands.command(name="ban")
	@commands.bot_has_permissions(ban_members=True)
	@commands.has_permissions(ban_members=True)
	@commands.guild_only()
	async def ban(self, ctx, member: discord.Member, *, reason=None):
		"""
		Does what it says, bans them from the server.
		"""
		if member.top_role >= ctx.author.top_role:
			await ctx.send("This user can't be banned due to hierachry.")
		else:
			await ctx.message.delete()
			try:
				await member.send(f"You were banned from {ctx.guild} for the reason: `{reason}`")
				await member.ban(reason=f"{member.name} was banned by {ctx.author.name}, for the reason: {reason}")
				await ctx.send(f"Banned {member} for the reason: `{reason}`")
			except:
				await ctx.send(f"Error: Could Not DM user")
				await member.ban(reason=f"{member.name} was banned by {ctx.author.name}, for the reason: {reason}")
				await ctx.send(f"Banned {member} for the reason: `{reason}`")
	
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
				await channel.set_permissions(muterole, send_messages=False, reason="Applying overrites for muted role")
		await ctx.send(f"Successfully muted {str(member)}.")

def setup(bot):
	bot.add_cog(Moderation(bot))
	print('[ModerationCog] Utils cog loaded')
