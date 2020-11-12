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

class Locking(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

# Things that need to be added - shlable db, 'duration' flag/arg
# Hardlock- Changes perms.
	@commands.command(name="hardlock", aliases=['lockdown', 'hl', 'ld'])
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True)
	@commands.guild_only()
	async def hardlock(self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel]=None, *, reason="None given"):
		"""
		Locks down a channel by denying @everyone send messages permission.
		"""
		ch = channel or ctx.channel
		perms = ch.overwrites_for(ctx.guild.default_role)
		if perms.send_messages == False:
			await ctx.send(f"❌ <#{ch.id}> is already locked!")
		else:
			perms.send_messages = False
			await ch.set_permissions(ctx.guild.default_role, overwrite=perms, reason=f"Channel locked by {ctx.author} ({ctx.author.id}.")
			await ctx.send(f"Successfully locked down <#{ch.id}> \n**Reason**: {reason}", delete_after=10)
				await ch.send(embed=discord.Embed(title=f"🔒 Channel Locked 🔒", description=f"This channel was locked by {ctx.author.mention}!\n**Reason:** {reason}", color=2937504), delete_after=600)
		
	@commands.command(name="unhardlock", aliases=['unlockdown', 'uhl', 'uld'])
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True)
	@commands.guild_only()
	async def unhardlock(self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel]=None, *, reason="None given"):
		"""
		Unlocks a channel by setting @everyone's send message permissions to neutral.
		"""
		ch = channel or ctx.channel
		perms = ch.overwrites_for(ctx.guild.default_role)
		if perms.send_messages != False:
			await ctx.send(f"❌ <#{ch.id}> is not locked!")
		else:
			perms.send_messages = None
			await ch.set_permissions(ctx.guild.default_role, overwrite=perms, reason=f"Channel unlocked by {ctx.author} ({ctx.author.id}.")
			await ctx.send(f"✅ Successfully unlocked <#{ch.id}>!\n**Reason:** {reason}", delete_after=10)
				await ch.send(embed=discord.Embed(title=f"🔓 Channel Unlocked 🔓", description=f"This channel was unlocked by {ctx.author.mention}!\n**Reason:** {reason}", color=2937504), delete_after=600)

	@commands.command(name="serverhardlockable", aliases=['shlockable', 'shlable'])
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True)
	@commands.guild_only()
	@commands.is_owner()
	async def serverhardlockable(self, ctx, *channels: discord.TextChannel, action=bool):
		"""
		Adds (text) channels to the list of channels that can be affected by server hardlock/unhardlock.
		"""
		if len(channels) == 0:
			await ctx.send(f"Please provide 1 or more channels to add to the list!\nCurrent list: ")
		else:
			if action == True:
				#this will be for adding to the db'
				pass
			else:
				#this will be for removing from db
				pass
			await ctx.send("lol that didn't do anything (yet) :joy:")


	@commands.command(name="serverhardlock", aliases=['serverlockdown', 'shl', 'sld'])
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True, manage_guild=True)
	@commands.guild_only()
	@commands.is_owner()
	async def serverhardlock(self, ctx, *, reason=f'None given.'):
		"""
		Locks the entire server by setting all channels' send messages permissions for @everyone to false.
		"""
		locked = ""
		for chan in ctx.guild.text_channels:
			perms = chan.overwrites_for(ctx.guild.default_role)
			if perms.send_messages == False:
				pass
			else:
				perms.send_messages = False
				await chan.set_permissions(ctx.guild.default_role, overwrite=perms, reason=f"Server locked down by {ctx.author} ({ctx.author.id}.")
				locked = f"{locked} `||` <#{chan.id}>"
				if ctx.channel.id != chan.id:
					await chan.send(embed=discord.Embed(title=f"🔒 Server Locked! 🔒", description=f"Server locked by {ctx.author}!\n**Reason:** {reason}", color=2937504), delete_after=600)
		await ctx.send(f"🔒 Locked down the server!\nChannels locked: {locked}\n**Reason:** {reason}")


	@commands.command(name="unserverhardlock", aliases=['unserverlockdown', 'ushl', 'usld'])
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True, manage_guild=True)
	@commands.guild_only()
	@commands.is_owner()
	async def serverunhardlock(self, ctx, *, reason='None given.'):
		"""
		Unlocks the entire server by setting all channels' send messages permissions for @everyone to neutral.
		"""
		unlocked = ""
		for chan in ctx.guild.text_channels:
			perms = chan.overwrites_for(ctx.guild.default_role)
			if perms.send_messages != False:
				pass
			else:
				perms.send_messages = None
				await chan.set_permissions(ctx.guild.default_role, overwrite=perms, reason=f"Server unlocked by {ctx.author} ({ctx.author.id}.")
				unlocked = f"{unlocked} `||` <#{chan.id}>"
				if ctx.channel.id != chan.id:
					await chan.send(embed=discord.Embed(title="🔓 Server Unlocked! 🔓", description=f"🔓 Server unlocked by {ctx.author.mention}!\n**Reason:** {reason}", color=2937504), delete_after=600)
		await ctx.send(f"🔓 Unlocked the server!\nChannels unlocked: {unlocked}\n**Reason:** {reason}")

# Softlock- Deletes messages.
	@commands.command(name="softlock", aliases=['lock', 'sl'])
	@commands.bot_has_permissions(manage_messages=True)
	@commands.has_permissions(manage_messages=True)
	@commands.guild_only()
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
			await ctx.send(f"✅ Successfully softlocked <#{ch.id}>.")
		else:
			await ctx.send(f"❌ <#{ch.id}> is already softlocked.")

	@commands.command(aliases=['wh'])
	@commands.bot_has_permissions(manage_messages=True)
	@commands.has_permissions(manage_messages=True)
	@commands.guild_only()
	async def whitelist(self, ctx, user: discord.Member):
		"""
		Whitelists a user from the softlock in the current channel, allowing them to speak but not unlock.
		"""
		db = await readDB()
		if not str(ctx.channel.id) in db["softlocked_channels"]:
			return await ctx.send("❌ This channel is not softlocked")
		elif not db["softlocked_channels"][str(ctx.channel.id)]["user"] == str(ctx.author.id):
			return await ctx.send("❌ You did not softlock this channel")
		else:
			db["softlocked_channels"][str(ctx.channel.id)]["whitelist"].append(user.id)
			await writeDB(db)
			return await ctx.send(f"✅ Successfully whitelisted {str(user)}")

	@commands.command(name="unsoftlock", aliases=['unlock', 'usl'])
	@commands.bot_has_permissions(manage_messages=True)
	@commands.has_permissions(manage_messages=True)
	@commands.guild_only()
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
				await ctx.send(f"✅ Successfully unsoftlocked <#{ch.id}>.")
			else:
				await ctx.send("❌ You cannot unlock this, as you are not the one who locked it.")
		else:
			await ctx.send(f"❌ <#{ch.id}> is not softlocked.")

def setup(bot):
	bot.add_cog(Locking(bot))
	print('[LockingCog] Utils cog loaded')
