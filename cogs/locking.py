import discord, random, asyncio, aiofiles, json, typing, postbin
from discord.ext import commands


class Locking(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

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
			await ctx.send(f"{self.bot.const_emojis['no']} {ch.mention} is already locked!")
		else:
			perms.send_messages = False
			await ch.set_permissions(ctx.guild.default_role, overwrite=perms, reason=f"Channel locked by {ctx.author} ({ctx.author.id}.")
			await ctx.send(f"{self.bot.const_emojis['yes']} Successfully locked down {ch.mention}!\n{f'**Reason:** {reason}' if reason else ''}", delete_after=10)
			await ch.send(embed=discord.Embed(title=f"🔒 Channel Locked 🔒", description=f"This channel was locked by {ctx.author.mention}!\n{f'**Reason:** {reason}' if reason else ''}", color=self.bot.colors['lightred']), delete_after=600)
		
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
			await ctx.send(f"{self.bot.const_emojis['no']} {ch.mention} is not locked!")
		else:
			perms.send_messages = None
			await ch.set_permissions(ctx.guild.default_role, overwrite=perms, reason=f"Channel unlocked by {ctx.author} ({ctx.author.id}.")
			await ctx.send(f"{self.bot.const_emojis['yes']} Successfully unlocked {ch.mention}!\n{f'**Reason:** {reason}' if reason else ''}", delete_after=10)
			await ch.send(embed=discord.Embed(title=f"🔓 Channel Unlocked 🔓", description=f"This channel was unlocked by {ctx.author.mention}!\n{f'**Reason:** {reason}' if reason else ''}", color=self.bot.colors['teal']), delete_after=600)

	@commands.group(name="serverhardlockable", aliases=['shlockable', 'shlable'], invoke_without_command=True)
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True)
	@commands.guild_only()
	async def serverhardlockable(self, ctx):
		"""
		Configure which channels will be locked by server hardlock/unhardlock.
		"""
		await self.doeschannelexist(ctx.guild)
		db = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
		embed=discord.Embed(title=f"__{ctx.guild}__'s Server Hardlockable Channels", description="There are no configured channels!", color=self.bot.colors['darkgreen'])
		if len(db) > 0:
			chanlist = []
			fallbacklist = []
			existingchannels = json.loads(db[0][0])
			for chan in existingchannels:
				chanlist.append(str(ctx.guild.get_channel(chan).mention))
				fallbacklist.append(f"#{ctx.guild.get_channel(chan).name}")
			chanlist = ' `||` '.join(chanlist)
			embed.description=f"{chanlist}"
		if len(embed.description) >= 2048:
			n = "\n"
			embed.description = f"Current list of channels is too long to send, view it here:\n{await postbin.postAsync(n.join(fallbacklist))}\nConfigured channels: {len(existingchannels)}"
		await ctx.send(embed=embed)

	@serverhardlockable.command()
	async def add(self, ctx, *channels: discord.TextChannel):
		"""
		Adds channels to the list of server hardlockable channels.
		"""
		if len(channels) < 1:
			return await ctx.send(f"{self.bot.const_emojis['no']} Please provide some channels to add to the list!")
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
		await ctx.send(f"{self.bot.const_emojis['yes']} Added the following channels to the list of hardlockable channels:\n{'`||`'.join(newchannels)}")
		await self.doeschannelexist(ctx.guild)

	@serverhardlockable.command(aliases=['categoryaddall'])
	async def addcategory(self, ctx, *categories: typing.Optional[discord.CategoryChannel]):
		"""
		Adds all channels in the specified categories to the list of server hardlockable channels.
		"""
		cats = categories or [ctx.channel.category]
		db = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
		existingchannels = []
		if db:
			existingchannels = json.loads(db[0][0])
			await self.bot.dbexec("DELETE FROM server_hardlockable_channels WHERE guildid=" + str(ctx.guild.id))
		newchannels = []
		for cat in cats:
			for chan in cat.text_channels:
				if chan.id not in existingchannels:
					existingchannels.append(chan.id)
					newchannels.append(chan.mention)
		await self.bot.dbexec(("INSERT INTO server_hardlockable_channels VALUES (?, ?)", (str(ctx.guild.id), str(existingchannels))))
		if len(newchannels) < 1:
			return await ctx.send(f"{self.bot.const_emojis['no']} There were no channels to add!")
		await ctx.send(f"{self.bot.const_emojis['yes']} Added the following channels to the list of hardlockable channels:\n{'`||`'.join(newchannels)}")
		await self.doeschannelexist(ctx.guild)

			       
	@serverhardlockable.command()
	async def addall(self, ctx):
		"""
		Adds all text channels in the server to the list of server hardlockable channels.
		"""
		db = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
		existingchannels = []
		added = 0
		if db:
			existingchannels = json.loads(db[0][0])
			await self.bot.dbexec("DELETE FROM server_hardlockable_channels WHERE guildid=" + str(ctx.guild.id))
		for chan in ctx.guild.text_channels:
			if chan.id not in existingchannels:
				existingchannels.append(chan.id)
				added += 1
		await self.bot.dbexec(("INSERT INTO server_hardlockable_channels VALUES (?, ?)", (str(ctx.guild.id), str(existingchannels))))
		if added == 0:
			return await ctx.send(f"{self.bot.const_emojis['no']} There were no channels to add!")
		await ctx.send(f"{self.bot.const_emojis['yes']} Added all server channels to the list of hardlockable channels.")
		await self.doeschannelexist(ctx.guild)
	
	@serverhardlockable.command()
	async def remove(self, ctx, *channels: discord.TextChannel):
		"""
		Removes channels from the list of server hardlockable channels.
		"""
		db = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
		if not db:
			return await ctx.send(f"{self.bot.const_emojis['no']} This server has no hardlockable channels. Use `{ctx.prefix}shlable add <channels>` to add some.")
		if len(channels) < 1:
			return await ctx.send(f"{self.bot.const_emojis['no']} Please provide some channels to remove from the list!")
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
			await ctx.send(f"{self.bot.const_emojis['yes']} Removed the following channels from the list of hardlockable channels:\n{'`||`'.join(removedchannels)}")
		await self.doeschannelexist(ctx.guild)

	@serverhardlockable.command(aliases=['categoryremoveall'])
	async def removecategory(self, ctx, *categories: typing.Optional[discord.CategoryChannel]):
		"""
		Removes all channels in the specified category from the list of server hardlockable channels.
		"""
		cats = categories or [ctx.channel.category]
		db = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
		existingchannels = []
		if not db:
			return await ctx.send(f"{self.bot.const_emojis['no']} This server has no hardlockable channels. Use `{ctx.prefix}shlable add <channels>` to add some.")
		existingchannels = json.loads(db[0][0])
		await self.bot.dbexec("DELETE FROM server_hardlockable_channels WHERE guildid=" + str(ctx.guild.id))
		removedchannels = []
		for cat in cats:
			for chan in cat.text_channels:
				if chan.id in existingchannels:
					existingchannels.remove(chan.id)
					removedchannels.append(chan.mention)
		if len(existingchannels) > 1:
			await self.bot.dbexec(("INSERT INTO server_hardlockable_channels VALUES (?, ?)", (str(ctx.guild.id), str(existingchannels))))
		if len(removedchannels) < 1:
			await ctx.send(f"{self.bot.const_emojis['no']} There were no channels to remove!")
		else:
			await ctx.send(f"{self.bot.const_emojis['yes']} Removed the following channels from the list of hardlockable channels:\n{'`||`'.join(removedchannels)}")
		await self.doeschannelexist(ctx.guild)

	@serverhardlockable.command()
	async def removeall(self, ctx):
		"""
		Removes all configured server hardlockable channels.
		"""
		db = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
		if not db:
			return await ctx.send(f"{self.bot.const_emojis['no']} This server has no hardlockable channels!")
		await self.bot.dbexec("DELETE FROM server_hardlockable_channels WHERE guildid=" + str(ctx.guild.id))
		await ctx.send(f"{self.bot.const_emojis['yes']} Reset server hardlockable channels!")
		await self.doeschannelexist(ctx.guild)
		
	@commands.command(name="serverhardlock", aliases=['serverlockdown', 'shl', 'sld'])
	@commands.bot_has_permissions(manage_channels=True)
	@commands.has_permissions(manage_channels=True, manage_guild=True)
	@commands.guild_only()
	async def serverhardlock(self, ctx, *, reason=None):
		"""
		Locks the entire server by setting configured channels' send messages permissions for @everyone to false.
		"""
		async with ctx.channel.typing():
			await self.doeschannelexist(ctx.guild)
			channeldb = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
			islockeddb = await self.bot.dbquery("islocked", "status", "guildid=" + str(ctx.guild.id))
			if not channeldb:
				return await ctx.send(f"{self.bot.const_emojis['no']} This server has not been configured. Please type `{ctx.prefix}help shlable` for instructions on how to configure server lockdown.")
			if islockeddb:
				return await ctx.send(f"{self.bot.const_emojis['no']} **{ctx.guild}** is already locked down!")
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
					embed=discord.Embed(title=f"🔒 Server Locked! 🔒", description=f"Server locked down by {ctx.author.nick or ctx.author.name}\n{f'**Reason:** {reason}' if reason else ''}", color=self.bot.colors['lightred'])
					embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
					await chan.send(embed=embed)
			embed = discord.Embed(title=f"{self.bot.const_emojis['yes']} Locked down the server!", description=f"🔒 **Channels Locked:**\n{' `||` '.join(locked)}", color=self.bot.colors['lightred'])
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
		Unlocks the entire server by setting configured channels' send messages permissions for @everyone to neutral.
		"""
		async with ctx.channel.typing():
			await self.doeschannelexist(ctx.guild)
			channeldb = await self.bot.dbquery("server_hardlockable_channels", "data", "guildid=" + str(ctx.guild.id))
			islockeddb = await self.bot.dbquery("islocked", "status", "guildid=" + str(ctx.guild.id))
			if not channeldb:
				return await ctx.send(f"{self.bot.const_emojis['no']} This server has not been configured. Please type `{ctx.prefix}help shlable` for instructions on how to configure server lockdown.")
			if not islockeddb:
				return await ctx.send(f"{self.bot.const_emojis['no']} **{ctx.guild}** is not locked down!")
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
					embed=discord.Embed(title="🔓 Server Unlocked! 🔓", description=f"Server lockdown ended by {ctx.author.nick or ctx.author.name}!\n{f'**Reason:** {reason}' if reason else ''}", color=self.bot.colors['teal'])
					embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
					await chan.send(embed=embed, delete_after=3600)
			embed = discord.Embed(title=f"{self.bot.const_emojis['yes']} Unlocked the server!", description=f"🔓 **Channels Unlocked:**\n{' `||` '.join(unlocked)}", color=self.bot.colors['teal'])
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
		db = await self.bot.dbquery("softlocked_channels", "data", "channelid=" +str(ch.id))
		if db:
			await ctx.send(f"{self.bot.const_emojis['no']} {ch.mention} is already softlocked!")
		else:
			data = {}
			whitelisted = [ctx.author.id]
			data["whitelisted"] = whitelisted
			await self.bot.dbexec(("INSERT INTO softlocked_channels VALUES (?, ?)", (str(ch.id), str(data))))
			await ctx.send(f"{self.bot.const_emojis['yes']} Successfully softlocked {ch.mention}!\n{f'**Reason:** {reason}' if reason else ''}", delete_after=10)
			await ch.send(embed=discord.Embed(title=f"🔒 Channel Softlocked 🔒", description=f"This channel was softlocked by {ctx.author.mention}!\n{f'**Reason:** {reason}' if reason else ''}", color=self.bot.colors['lightred']))

	@commands.command(aliases=['wh'])
	@commands.bot_has_permissions(manage_messages=True)
	@commands.has_permissions(manage_messages=True)
	@commands.guild_only()
	@commands.is_owner()
	async def whitelist(self, ctx, user: discord.Member, channel: discord.TextChannel=None):
		"""
		Whitelists a user from the softlock in the current channel, allowing them to speak but not unlock.
		"""
		ch = channel or ctx.channel
		db = await self.bot.dbquery("softlocked_channels", "data", "channelid=" +str(ch.id))
		if db:
			data = json.loads((db[0][0]).replace("'", '"'))
			whitelisted = data["whitelisted"]
			if ctx.author.id not in whitelisted and not getattr(ctx.author.guild_permissions, "administrator"):
				return await ctx.send(f"{self.bot.const_emojis['no']} You're not whitelisted to speak in this channel and you don't have admin, so you can't whitelist others!")
			whitelisted.append(user.id)
			data["whitelisted"] = whitelisted
			await self.bot.dbexec("DELETE FROM softlocked_channels WHERE channelid=" +str(ch.id))
			await self.bot.dbexec(("INSERT INTO softlocked_channels VALUES (?, ?)", (str(ch.id), str(data))))
			await ctx.send(f"{self.bot.const_emojis['yes']} Successfully whitelisted {user.mention}!")
		else:
			await ctx.send(f"{self.bot.const_emojis['no']} {ch.mention} is not softlocked!")

	@commands.command(name="unsoftlock", aliases=['unlock', 'usl'])
	@commands.bot_has_permissions(manage_messages=True)
	@commands.has_permissions(manage_messages=True)
	@commands.guild_only()
	@commands.is_owner()
	async def unsoftlock(self, ctx, channel: discord.TextChannel=None, reason=None):
		"""
		Unsoftlocks a channel.
		"""
		ch = channel or ctx.channel
		db = await self.bot.dbquery("softlocked_channels", "data", "channelid=" +str(ch.id))
		if db:
			await self.bot.dbexec("DELETE FROM softlocked_channels WHERE channelid=" +str(ch.id))
			await ctx.send(f"{self.bot.const_emojis['yes']} Successfully unsoftlocked {ch.mention}!", delete_after=10)
			await ch.send(embed=discord.Embed(title=f"🔓 Channel Unsoftlocked 🔓", description=f"This channel was unsoftlocked by {ctx.author.mention}!\n{f'**Reason:** {reason}' if reason else ''}", color=self.bot.colors['teal']))
		else:
			await ctx.send(f"{self.bot.const_emojis['no']} {ch.mention} is not soflocked!")
				       
	@commands.command(name="serversoftlock", aliases=['ssl'])
	@commands.has_permissions(manage_messages=True, manage_guild=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.guild_only()
	@commands.is_owner()
	async def serversoftlock(self, ctx, reason=None):
		locked = 0
		data = {}
		whitelisted = [ctx.author.id]
		data["whitelisted"] = whitelisted
		for chan in ctx.guild.text_channels:
			db = await self.bot.dbquery("softlocked_channels", "data", "channelid=" +str(chan.id))
			if not db:
				await self.bot.dbexec(("INSERT INTO softlocked_channels VALUES (?, ?)", (str(chan.id), str(data))))
				locked += 1
		if locked < 1:
			await ctx.send(f"{self.bot.const_emojis['no']} **{ctx.guild}** is already softlocked!")
		else:
			await ctx.send(embed=discord.Embed(title=f"🔓 Server Softlocked 🔓", description=f"{self.bot.const_emojis['yes']} **{ctx.guild}** has been softlocked by {ctx.author.mention}!\n{f'**Reason:** {reason}' if reason else ''}", color=self.bot.colors['lightred']))


	@commands.command(name="unserversoftlock", aliases=['ussl'])
	@commands.has_permissions(manage_messages=True, manage_guild=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.guild_only()
	@commands.is_owner()
	async def unserversoftlock(self, ctx, reason=None):
		unlocked = 0
		for chan in ctx.guild.text_channels:
			db = await self.bot.dbquery("softlocked_channels", "data", "channelid=" +str(chan.id))
			if db:
				await self.bot.dbexec(("DELETE FROM softlocked_channels WHERE channelid=" +str(chan.id)))
				unlocked += 1
		if unlocked < 1:
			await ctx.send(f"{self.bot.const_emojis['no']} **{ctx.guild}** is not softlocked!")
		else:
			await ctx.send(embed=discord.Embed(title=f"🔓 Server Unsoftlocked 🔓", description=f"{self.bot.const_emojis['yes']} **{ctx.guild}** has been unsoftlocked by {ctx.author.mention}!\n{f'**Reason:** {reason}' if reason else ''}", color=self.bot.colors['teal']))


def setup(bot):
	bot.add_cog(Locking(bot))
	print('[LockingCog] Locking cog loaded')
