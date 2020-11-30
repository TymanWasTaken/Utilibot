import discord, random, asyncio, aiofiles, json, typing, postbin
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

async def islockable(guild, channel):
	if not guild:
		return False
	db = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(guild.id))
	if len(db) < 1:
		return False
	data = json.loads(db[0][0])
	if channel not in data:
		return False
	else:
		return data[channel]

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
			await ctx.send(f"✅ Successfully locked down <#{ch.id}> \n**Reason**: {reason}", delete_after=10)
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

	@commands.group(name="serverhardlockable", aliases=['shlockable', 'shlable'], invoke_without_command=True)
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True)
	@commands.guild_only()
	@commands.is_owner()
	async def serverhardlockable(self, ctx):
		"""
		Configure which channels will be locked by server hardlock/unhardlock.
		"""
		db = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
		embed=discord.Embed(title="Server Hardlockable Channels", description=f"**{ctx.guild}** has no configured channels.")
		if len(db) > 0:
			chanlist = []
			existingchannels = json.loads(db[0][0])
			for chan in existingchannels:
				chanlist.append(str(ctx.guild.get_channel(chan).mention))
			chanlist = ', '.join(chanlist)
			embed.description=f"{chanlist}"
		await ctx.send(embed=embed)

	@serverhardlockable.command()
	async def add(self, ctx, *channels: discord.TextChannel):
		"""
		Adds channels to the list of server hardlockable channels.
		"""
		if len(channels) < 1:
			return await ctx.send("Please provide some channels to add!")
		db = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
		existingchannels = []
		if db:
			existingchannels = json.loads(db[0][0])
			await self.bot.dbexec("DELETE FROM server_hardlockable_channels WHERE guildid=" + str(ctx.guild.id))
		newchannels = []
		for chan in channels:
			if chan.id not in existingchannels:
				existingchannels.append(chan.id)
				newchannels.append(chan.mention)
		for chanid in existingchannels:
			if not ctx.guild.get_channel(chanid):
				existingchannels.remove(chanid)
		await self.bot.dbexec(("INSERT INTO server_hardlockable_channels VALUES (?, ?)", (str(ctx.guild.id), str(existingchannels))))
		await ctx.send(f"Added the following channels to the list of hardlockable channels:\n{', '.join(newchannels)}")

	@serverhardlockable.command()
	async def remove(self, ctx, *channels: discord.TextChannel):
		"""
		Removes channels from the list of server hardlockable channels.
		"""
		db = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
		if not db:
			return await ctx.send(f"This server has no hardlockable channels. Use `{ctx.prefix}shlable add <channels>` to add some.")
		if len(channels) < 1:
			return await ctx.send("Please provide some channels to remove from the list!")
		existingchannels = json.loads(db[0][0])
		await self.bot.dbexec("DELETE FROM server_hardlockable_channels WHERE guildid=" + str(ctx.guild.id))
		removedchannels = []
		for chan in channels:
			if chan.id in existingchannels:
				existingchannels.remove(chan.id)
				removedchannels.append(chan.mention)
		for chanid in existingchannels:
			if not ctx.guild.get_channel(chanid):
				existingchannels.remove(chanid)
		if len(existingchannels) > 1:
			await self.bot.dbexec(("INSERT INTO server_hardlockable_channels VALUES (?, ?)", (str(ctx.guild.id), str(existingchannels))))
		if len(removedchannels) < 1:
			await ctx.send("There were no channels to remove.")
		else:
			await ctx.send(f"Removed the following channels from the list of hardlockable channels:\n{', '.join(removedchannels)}")

	@commands.command(name="serverhardlock", aliases=['serverlockdown', 'shl', 'sld'])
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True, manage_guild=True)
	@commands.guild_only()
	@commands.is_owner()
	async def serverhardlock(self, ctx, *, reason=f'None given.'):
		"""
		Locks the entire server by setting specified channels' send messages permissions for @everyone to false.
		"""
		channeldb = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
		islockeddb = await self.bot.dbquery("islocked", "status", "guildid=" + str(ctx.guild.id))
		if not channeldb:
			return await ctx.send(f"This server has not been configured. Please type `{ctx.prefix}help shlable` for instructions on how to configure server lockdown.")
		if islockeddb:
			return await ctx.send(f"{self.bot.const_emojis['no']} **{ctx.guild}** is already locked down!")
		channellist = json.loads(channeldb[0][0])
		locked = []
		m = await ctx.send("Locking server...")
		for chanid in channellist:
			chan = ctx.guild.get_channel(chanid)
			if not chan:
				channellist.remove(chanid)
				continue
			perms = chan.overwrites_for(ctx.guild.default_role)
			if perms.send_messages != False:
				perms.send_messages = False
				await chan.set_permissions(ctx.guild.default_role, overwrite=perms, reason=f"Server locked down by {ctx.author} ({ctx.author.id}).")
				locked.append(f"<#{chan.id}>")
				await chan.send(embed=discord.Embed(title=f"🔒 Server Locked! 🔒", description=f"Server locked by {ctx.author.mention}!\n**Reason:** {reason}", color=2937504), delete_after=600)
		embed = discord.Embed(title=f"🔒 Locked down the server!", description=f"**Channels Locked:**\n{' `||` '.join(locked)}", color=2937504)
		embed.add_field(name="Reason:", value=reason)
		if len(embed.description) > 2048:
			embed.description=f"List is too long to send!\nNumber of channels locked: {len(locked)}"
		await self.bot.dbexec("DELETE FROM server_hardlockable_channels WHERE guildid=" + str(ctx.guild.id))
		await self.bot.dbexec(("INSERT INTO server_hardlockable_channels VALUES (?, ?)", (str(ctx.guild.id), str(channellist))))
		await self.bot.dbexec(("INSERT INTO islocked VALUES (?, ?)", (str(ctx.guild.id), "true")))
		await m.delete()
		await ctx.send(content="Done!", embed=embed, delete_after=60)


	@commands.command(name="unserverhardlock", aliases=['unserverlockdown', 'ushl', 'usld'])
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True, manage_guild=True)
	@commands.guild_only()
	@commands.is_owner()
	async def serverunhardlock(self, ctx, *, reason='None given.'):
		"""
		Unlocks the entire server by setting all channels' send messages permissions for @everyone to neutral.
		"""
		db = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
		unlocked = []
		m = await ctx.send("Unlocking server...")
		for chan in ctx.guild.text_channels:
			perms = chan.overwrites_for(ctx.guild.default_role)
			if perms.send_messages == False:
				perms.send_messages = None
				await chan.set_permissions(ctx.guild.default_role, overwrite=perms, reason=f"Server unlocked by {ctx.author} ({ctx.author.id}).")
				unlocked.append(f"<#{chan.id}>")
				await chan.send(embed=discord.Embed(title="🔓 Server Unlocked! 🔓", description=f"Server unlocked by {ctx.author.mention}!\n**Reason:** {reason}", color=2937504), delete_after=600)
		embed = discord.Embed(title=f"🔓 Unlocked the server! 🔓", description=f"**Channels Unlocked:**\n{' `||` '.join(unlocked)}", color=2937504)
		embed.add_field(name="Reason:", value=reason)
		if len(embed.description) > 2048:
			embed.description=f"List is too long to send!\nNumber of channels unlocked: {len(unlocked)}"
		await m.delete()
		await ctx.send(content="Done!", embed=embed, delete_after=60)

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
	print('[LockingCog] Locking cog loaded')
