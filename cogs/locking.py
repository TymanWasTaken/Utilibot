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


class Locking(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.emojis = bot.const_emojis

	async def doeschannelexist(self, guild):
		if not guild:
			return
		channeldb = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(guild.id))
		if not channeldb:
			return
		channellist = json.loads(channeldb[0][0])
		for chanid in channellist:
			if not guild.get_channel(chanid):
				channellist.remove(chanid)
		await self.bot.dbexec("DELETE FROM server_hardlockable_channels WHERE guildid=" + str(guild.id))
		await self.bot.dbexec(("INSERT INTO server_hardlockable_channels VALUES (?, ?)", (str(guild.id), str(channellist))))

# Hardlock- Changes perms.
	@commands.command(name="hardlock", aliases=['lockdown', 'hl', 'ld'])
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True)
	@commands.guild_only()
	async def hardlock(self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel]=None, *, reason=None):
		"""
		Locks down a channel by denying @everyone send messages permission.
		"""
		ch = channel or ctx.channel
		perms = ch.overwrites_for(ctx.guild.default_role)
		if perms.send_messages == False:
			await ctx.send(f"{self.emojis['no']} <#{ch.id}> is already locked!")
		else:
			perms.send_messages = False
			await ch.set_permissions(ctx.guild.default_role, overwrite=perms, reason=f"Channel locked by {ctx.author} ({ctx.author.id}.")
			await ctx.send(f"{self.emojis['yes']} Successfully locked down <#{ch.id}>!\n{f'**Reason:** {reason}' if reason else ''}", delete_after=10)
			await ch.send(embed=discord.Embed(title=f"🔒 Channel Locked 🔒", description=f"This channel was locked by {ctx.author.mention}!\n{f'**Reason:** {reason}' if reason else ''}", color=2937504), delete_after=600)
		
	@commands.command(name="unhardlock", aliases=['unlockdown', 'uhl', 'uld'])
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True)
	@commands.guild_only()
	async def unhardlock(self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel]=None, *, reason=None):
		"""
		Unlocks a channel by setting @everyone's send message permissions to neutral.
		"""
		ch = channel or ctx.channel
		perms = ch.overwrites_for(ctx.guild.default_role)
		if perms.send_messages != False:
			await ctx.send(f"{self.emojis['no']} <#{ch.id}> is not locked!")
		else:
			perms.send_messages = None
			await ch.set_permissions(ctx.guild.default_role, overwrite=perms, reason=f"Channel unlocked by {ctx.author} ({ctx.author.id}.")
			await ctx.send(f"{self.emojis['yes']} Successfully unlocked <#{ch.id}>!\n{f'**Reason:** {reason}' if reason else ''}", delete_after=10)
			await ch.send(embed=discord.Embed(title=f"🔓 Channel Unlocked 🔓", description=f"This channel was unlocked by {ctx.author.mention}!\n{f'**Reason:** {reason}' if reason else ''}", color=2937504), delete_after=600)

	@commands.group(name="serverhardlockable", aliases=['shlockable', 'shlable'], invoke_without_command=True)
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True)
	@commands.guild_only()
	@commands.is_owner()
	async def serverhardlockable(self, ctx):
		"""
		Configure which channels will be locked by server hardlock/unhardlock.
		"""
		await self.doeschannelexist(ctx.guild)
		db = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
		embed=discord.Embed(title="Server Hardlockable Channels", description=f"**{ctx.guild}** has no configured channels.")
		if len(db) > 0:
			chanlist = []
			existingchannels = json.loads(db[0][0])
			for chan in existingchannels:
				chanlist.append(str(ctx.guild.get_channel(chan).mention))
			chanlist = '`||`'.join(chanlist)
			embed.description=f"{chanlist}"
		await ctx.send(embed=embed)

	@serverhardlockable.command()
	async def add(self, ctx, *channels: discord.TextChannel):
		"""
		Adds channels to the list of server hardlockable channels.
		"""
		if len(channels) < 1:
			return await ctx.send(f"{self.emojis['no']} Please provide some channels to add to the list!")
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
		await self.bot.dbexec(("INSERT INTO server_hardlockable_channels VALUES (?, ?)", (str(ctx.guild.id), str(existingchannels))))
		await ctx.send(f"{self.emojis['yes']} Added the following channels to the list of hardlockable channels:\n{'`||`'.join(newchannels)}")
		await self.doeschannelexist(ctx.guild)
			       
	@serverhardlockable.command()
	async def addall(self, ctx):
		"""
		Adds all channels in the server to the list of server hardlockable channels.
		"""
		db = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
		existingchannels = []
		if db:
			existingchannels = json.loads(db[0][0])
			await self.bot.dbexec("DELETE FROM server_hardlockable_channels WHERE guildid=" + str(ctx.guild.id))
		for chan in ctx.guild.text_channels:
			if chan.id not in existingchannels:
				existingchannels.append(chan.id)
		await self.bot.dbexec(("INSERT INTO server_hardlockable_channels VALUES (?, ?)", (str(ctx.guild.id), str(existingchannels))))
		await ctx.send(f"{self.emojis['yes']} Added all server channels to the list of hardlockable channels.")
		await self.doeschannelexist(ctx.guild)
	
	@serverhardlockable.command()
	async def remove(self, ctx, *channels: discord.TextChannel):
		"""
		Removes channels from the list of server hardlockable channels.
		"""
		db = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
		if not db:
			return await ctx.send(f"{self.emojis['no']} This server has no hardlockable channels. Use `{ctx.prefix}shlable add <channels>` to add some.")
		if len(channels) < 1:
			return await ctx.send("{self.emojis['no']} Please provide some channels to remove from the list!")
		existingchannels = json.loads(db[0][0])
		await self.bot.dbexec("DELETE FROM server_hardlockable_channels WHERE guildid=" + str(ctx.guild.id))
		removedchannels = []
		for chan in channels:
			if chan.id in existingchannels:
				existingchannels.remove(chan.id)
				removedchannels.append(chan.mention)
		if len(existingchannels) > 1:
			await self.bot.dbexec(("INSERT INTO server_hardlockable_channels VALUES (?, ?)", (str(ctx.guild.id), str(existingchannels))))
		if len(removedchannels) < 1:
			await ctx.send("There were no channels to remove.")
		else:
			await ctx.send(f"{self.emojis['yes']} Removed the following channels from the list of hardlockable channels:\n{'`||`'.join(removedchannels)}")
		await self.doeschannelexist(ctx.guild)

	@serverhardlockable.command()
	async def removeall(self, ctx):
		db = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
		if db:
			await self.bot.dbexec("DELETE FROM server_hardlockable_channels WHERE guildid=" + str(ctx.guild.id))
		await ctx.send(f"{self.emojis['yes']} Reset server hardlockable channels!")
		await self.doeschannelexist(ctx.guild)
		
	@commands.command(name="serverhardlock", aliases=['serverlockdown', 'shl', 'sld'])
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True, manage_guild=True)
	@commands.guild_only()
	async def serverhardlock(self, ctx, *, reason=None):
		"""
		Locks the entire server by setting specified channels' send messages permissions for @everyone to false.
		"""
		async with ctx.channel.typing():
			await self.doeschannelexist(ctx.guild)
			channeldb = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
			islockeddb = await self.bot.dbquery("islocked", "status", "guildid=" + str(ctx.guild.id))
			if not channeldb:
				return await ctx.send(f"{self.emojis['no']} This server has not been configured. Please type `{ctx.prefix}help shlable` for instructions on how to configure server lockdown.")
			if islockeddb:
				return await ctx.send(f"{self.emojis['no']} **{ctx.guild}** is already locked down!")
			channellist = json.loads(channeldb[0][0])
			locked = []
			m = await ctx.send("Locking server...")
			for chanid in channellist:
				chan = ctx.guild.get_channel(chanid)
				perms = chan.overwrites_for(ctx.guild.default_role)
				if perms.send_messages != False:
					perms.send_messages = False
					await chan.set_permissions(ctx.guild.default_role, overwrite=perms, reason=f"Server locked down by {ctx.author} ({ctx.author.id}).")
					locked.append(f"<#{chan.id}>")
					await chan.send(embed=discord.Embed(title=f"🔒 Server Locked! 🔒", description=f"Server locked by {ctx.author.mention}!\n{f'**Reason:** {reason}' if reason else ''}", color=2937504), delete_after=600)
			embed = discord.Embed(title=f"{self.emojis['yes']} Locked down the server!", description=f"🔒 **Channels Locked:**\n{' `||` '.join(locked)}", color=2937504)
			if reason != None: embed.add_field(name="Reason:", value=reason)
			if len(embed.description) > 2048:
				embed.description=f"List is too long to send!\nNumber of channels locked: {len(locked)}"
			await self.bot.dbexec(("INSERT INTO islocked VALUES (?, ?)", (str(ctx.guild.id), "true")))
			await m.delete()
			if len(locked) < 1:
				await ctx.send("No channels locked.", delete_after=60)
			else:
				await ctx.send(content="Done!", embed=embed, delete_after=60)


	@commands.command(name="unserverhardlock", aliases=['unserverlockdown', 'ushl', 'usld'])
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True, manage_guild=True)
	@commands.guild_only()
	async def unserverhardlock(self, ctx, *, reason=None):
		"""
		Unlocks the entire server by setting all channels' send messages permissions for @everyone to neutral.
		"""
		async with ctx.channel.typing():
			await self.doeschannelexist(ctx.guild)
			channeldb = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
			islockeddb = await self.bot.dbquery("islocked", "status", "guildid=" + str(ctx.guild.id))
			if not channeldb:
				return await ctx.send(f"{self.emojis['no']} This server has not been configured. Please type `{ctx.prefix}help shlable` for instructions on how to configure server lockdown.")
			if not islockeddb:
				return await ctx.send(f"{self.emojis['no']} **{ctx.guild}** is not locked down!")
			channellist = json.loads(channeldb[0][0])
			unlocked = []
			m = await ctx.send("Unlocking server...")
			for chanid in channellist:
				chan = ctx.guild.get_channel(chanid)
				perms = chan.overwrites_for(ctx.guild.default_role)
				if perms.send_messages == False:
					perms.send_messages = None
					await chan.set_permissions(ctx.guild.default_role, overwrite=perms, reason=f"Server unlocked by {ctx.author} ({ctx.author.id}).")
					unlocked.append(f"<#{chan.id}>")
					await chan.send(embed=discord.Embed(title="🔓 Server Unlocked! 🔓", description=f"Server unlocked by {ctx.author.mention}!\n{f'**Reason:** {reason}' if reason else ''}", color=2937504), delete_after=600)
			embed = discord.Embed(title=f"{self.emojis['yes']} Unlocked the server!", description=f"🔓 **Channels Unlocked:**\n{' `||` '.join(unlocked)}", color=2937504)
			if reason: embed.add_field(name="Reason:", value=reason)
			if len(embed.description) > 2048:
				embed.description=f"List is too long to send!\nNumber of channels unlocked: {len(unlocked)}"
			await self.bot.dbexec("DELETE FROM islocked WHERE guildid=" + str(ctx.guild.id))
			await m.delete()
			if len(unlocked) < 1:
				await ctx.send("No channels unlocked.", delete_after=60)
			else:
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
		ch = channel or ctx.channel
		db = await bot.dbquery("softlocked_channels", "data", "channelid=" +str(ch.id))
		if db:
			await ctx.send(f"{self.emojis['no'] {ch.mention} is already softlocked!")
		else:
			data = {
				"user": str(ctx.author.id),
				"whitelisted": []
			}
			await self.bot.dbexec(("INSERT INTO softlocked_channels VALUES (?, ?)", (str(ch.id), str(data))))
			await ctx.send(f"{self.emojis['yes']} Successfully softlocked {ch.mention}!\n{f'**Reason:** {reason}' if reason else ''}", delete_after=10)
			await ch.send(embed=discord.Embed(title=f"🔒 Channel Softlocked 🔒", description=f"This channel was softlocked by {ctx.author.mention}!\n{f'**Reason:** {reason}' if reason else ''}", color=self.bot.colors['lightred']), delete_after=600)

	@commands.command(aliases=['wh'])
	@commands.bot_has_permissions(manage_messages=True)
	@commands.has_permissions(manage_messages=True)
	@commands.guild_only()
	async def whitelist(self, ctx, user: discord.Member, channel: discord.TextChannel=None):
		"""
		Whitelists a user from the softlock in the current channel, allowing them to speak but not unlock.
		"""
		ch = channel or ctx.channel
		db = await bot.dbquery("softlocked_channels", "data", "channelid=" +str(ch.id))
		if db:
			db = json.loads(db[0][0])
			if db['user'] != str(ctx.author.id):
				await ctx.send(f"{self.emojis['no']} You didn't soflock this channel, so you can't whitelist people!")
			else:
				whitelisted = db['whitelisted']
				whitelisted.append(user.id)
				db['whitelisted'] = whitelisted
				await self.bot.dbexec("DELETE FROM softlocked_channels WHERE channelid=" +str(ch.id))
				await self.bot.dbexec(("INSERT INTO softlocked_channels VALUES (?, ?)", (str(ch.id), str(db))))
				await ctx.send(f"{self.emojis['yes']} Successfully whitelisted {user.mention}!")
		else:
			await ctx.send(f"{self.emojis['no']} {ch.mention} is not softlocked!") 

	@commands.command(name="unsoftlock", aliases=['unlock', 'usl'])
	@commands.bot_has_permissions(manage_messages=True)
	@commands.has_permissions(manage_messages=True)
	@commands.guild_only()
	async def unsoftlock(self, ctx, channel: discord.TextChannel=None):
		"""
		Unsoftlocks a channel.
		"""
		ch = channel or ctx.channel
		db = await bot.dbquery("softlocked_channels", "data", "channelid=" +str(ch.id))
		if db:
			await bot.dbexec("DELETE FROM softlocked_channels WHERE channelid=" +str(ch.id))
			await ctx.send(f"{self.emojis['yes']} Successfully unsoftlocked {ch.mention}!")
			await ch.send(embed=discord.Embed(title=f"🔓 Channel Unsoftlocked 🔓", description=f"This channel was unsoftlocked by {ctx.author.mention}!\n{f'**Reason:** {reason}' if reason else ''}", color=self.bot.colors['teal']), delete_after=600)
		else:
			await ctx.send(f"{self.emojis['no']} {ch.mention} is not soflocked!")

def setup(bot):
	bot.add_cog(Locking(bot))
	print('[LockingCog] Locking cog loaded')
