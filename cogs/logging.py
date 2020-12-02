import discord, dpytils, postbin, aiofiles, json, typing, unicodedata, aiosqlite
from discord.ext import commands
from datetime import datetime

utils = dpytils.utils()


class Logging(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.logs = {
		"Messages":["edit", "delete", "purge"],
		"Users":["nickname", "userroles", "status", "activity", "username", "discriminator", "avatar", "ban", "unban"],
		"Join/Leave":["join", "leave"],
		"Voice":["voicejoin", "voiceleave", "voicemove"],
		"Server":["serverupdates", "emojis"],
		"Roles":["rolecreate", "roleupdate", "roledelete"],
		"Channels":["channelcreate", "channelupdate", "channeldelete"],
#		"Lock/Unlock": ['softlock', 'unsoftlock', 'hardlock', 'unhardlock', 'serversoftlock', 'unserversoftlock', 'serverhardlock', 'unserverhardlock'],
		"Reactions":["reactionadd", "reactionremove", "reactionclear"]
		}
		self.log_flat = {x for v in self.logs.values() for x in v}
		self.yes = f"<:yes:778489135870377994>"
		self.no = f"<:no:778489134741979186>"

	async def islogenabled(self, guild, log):
		if not guild:
			return False
		db = await self.bot.dbquery("logging", "data", "guildid=" + str(guild.id))
		if len(db) < 1:
			return False
		data = json.loads(db[0][0])
		if log not in data:
			return False
		else:
			return data[log]

	async def getlogs(self, guild):
		if not guild:
			return None
		db = await self.bot.dbquery("logging", "data", "guildid=" + str(guild.id))
		if len(db) < 1:
			return None
		data = json.loads(db[0][0])
		return data

	async def setlogs(self, guild, data):
		if not guild:
			return None
		try:
			await self.bot.dbexec(("INSERT INTO logging VALUES (?, ?)", (guild.id, json.dumps(data))))
		except aiosqlite.IntegrityError:
			await self.bot.dbexec(("DELETE FROM logging WHERE guildid=?", (guild.id,)))
			await self.bot.dbexec(("INSERT INTO logging VALUES (?, ?)", (guild.id, json.dumps(data))))

	async def getlogchannel(self, guild):
		results = await self.bot.dbquery('logchannel', 'channelid', 'guildid=' + str(guild.id))
		if len(results) < 1:
			return None
		try: 
			return guild.get_channel(int(results[0][0]))
		except: 
			await self.bot.dbexec("DELETE FROM logchannel WHERE guildid=" + str(guild.id))
			return None

	@commands.group(invoke_without_command=True)
	@commands.has_permissions(manage_guild=True)
	@commands.guild_only()
	async def log(self, ctx):
		"""
		Shows logging settings for the current server.
		"""
		logchannel = await self.bot.dbquery('logchannel', 'channelid', 'guildid=' + str(ctx.guild.id))
		if logchannel == []:
			return await ctx.send(f"You haven't configured a log channel for this server yet! Type `{ctx.prefix}log channel <channel>` to set it up.")
		else: 
			logchannel = logchannel[0][0]
		db = await self.getlogs(ctx.guild)
		if db == None:
			db = {}
		for log in list(db):
			if log not in self.log_flat:
				db.pop(log)
		await self.setlogs(ctx.guild, db)
		embed=discord.Embed(title="Enabled Logs:", color=6666219)
		for cat in self.logs:
			logs = ""
			for log in sorted(self.logs[cat]):
				logs += f"{self.yes if await self.islogenabled(ctx.guild, log) else self.no} `{log}`\n"
			embed.add_field(name=cat, value=logs, inline=False)
		embed.add_field(name="Log Channel", value=f"{f'<#{logchannel}>' if logchannel else 'None Set'}")
		await ctx.send(embed=embed)

	@log.command()
	@commands.has_permissions(manage_guild=True)
	async def channel(self, ctx, channel: discord.TextChannel):
		"""
		Sets the logging channel.
		"""
		if await self.bot.dbquery('logchannel', 'channelid', 'guildid=' + str(channel.guild.id)):
			await self.bot.dbexec(f"DELETE FROM logchannel WHERE guildid={ctx.guild.id}")
		await self.bot.dbexec(f"INSERT INTO logchannel VALUES ({ctx.guild.id}, {channel.id})")
		await ctx.send(f"Set the log channel to <#{channel.id}>!")

	@log.command()
	@commands.has_permissions(manage_guild=True)
	async def enable(self, ctx, log: str):
		"""
		Enable one of the logs.
		"""
		log = log.lower()
		if log not in self.log_flat:
			return await ctx.send("Not a valid log.")
		db = await self.getlogs(ctx.guild)
		if db == None:
			db = {}	
		if db[log] != None and db[log] == True:
			await ctx.send(f"`{log}` is already enabled!")
		else: 
			db[log] = True
			await self.setlogs(ctx.guild, db)
			await ctx.send(f"Enabled log `{log}`")

	@log.command()
	@commands.has_permissions(manage_guild=True)
	async def disable(self, ctx, log: str):
		"""
		Disable one of the logs.
		"""
		log = log.lower()
		if log not in self.log_flat:
			return await ctx.send("Not a valid log.")
		db = await self.getlogs(ctx.guild)
		if db == None:
			db = {}
		if db[log] == False:
			await ctx.send(f"`{log}` is already disabled!")
		else: 
			db[log] = False
			await self.setlogs(ctx.guild, db)
			await ctx.send(f"Disabled log `{log}`")

	@log.command()
	@commands.has_permissions(manage_guild=True)
	async def enableall(self, ctx):
		"""
		Enable all of the logs.
		"""
		db = await self.getlogs(ctx.guild)
		if db == None:
			db = {}
		for log in self.log_flat:
			db[log] = True
		await self.setlogs(ctx.guild, db)
		await ctx.send(f"Enabled all logs.")

	@log.command()
	@commands.has_permissions(manage_guild=True)
	async def disableall(self, ctx):
		"""
		Disable all of the logs.
		"""
		db = await self.getlogs(ctx.guild)
		if db == None:
			db = {}
		for log in self.log_flat:
			db[log] = False
		await self.setlogs(ctx.guild, db)
		await ctx.send(f"Disabled all logs.")

	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		if before.content == after.content:
			return
		if not before.guild:
			return
		if not await self.islogenabled(before.guild, "edit"):
			return
		logchannel = await self.getlogchannel(before.guild)
		if before.guild.id == 774443390879793205:
			logchannel = await self.bot.fetch_webhook(781614888429813771)
		if logchannel == None:
			return
		before_content = before.clean_content.replace('`', '​`​')
		after_content = after.clean_content.replace('`', '​`​')
		if before_content == "" and after.embeds:
			before_content = "Message contained embed only"
		if after_content == "" and after.embeds:
			after_content = "Message contained embed only"
		embed = discord.Embed(title=f"Message Edited in #{before.channel.name}", description=f"[Direct Link]({before.jump_url})", color=0x1184ff, timestamp=datetime.now())
		if len(before_content) <= 1016: 
			embed.add_field(name="Before:", value=f"```{before_content}```", inline=False)
		else:
			before_content = await postbin.postAsync(before_content)
			embed.add_field(name="Before:", value=before_content, inline=False)
		if len(after_content) <= 1016:
			embed.add_field(name="After:", value=f"```{after_content}```", inline=False)
		else:
			after_content = await postbin.postAsync(after_content)
			embed.add_field(name="After:", value=after_content, inline=False)
		embed.set_author(name=before.author, icon_url=before.author.avatar_url)
		embed.set_footer(text=f"Author ID: {before.author.id}")
		await logchannel.send(embed=embed)
	
	@commands.Cog.listener()
	async def on_message_delete(self, message):
		if not message.guild:
			return
		if not await self.islogenabled(message.guild, "delete"):
			return
		logchannel = await self.getlogchannel(message.guild)
		if logchannel == None:
			return
		if message.clean_content == "":
			return
		embed=discord.Embed(title=f"Message Deleted in #{message.channel.name}", description=f"```{message.clean_content.replace('`', '​`​')}```", color=0xe41212, timestamp=datetime.now())
		embed.set_author(name=message.author, icon_url=message.author.avatar_url)
		embed.set_footer(text=f"Author ID: {message.author.id}")
		if not (message.embeds and not message.content):
			await logchannel.send(embed=embed)
	
	@commands.Cog.listener()
	async def on_bulk_message_delete(self, messages):
		exmsg = messages[0]
		if not exmsg.guild:
			return
		if not await self.islogenabled(exmsg.guild, "purge"):
			return
		logchannel = await self.getlogchannel(exmsg.guild)
		if logchannel == None:
			return
		post = f"{len(messages)} messages deleted in #{exmsg.channel.name} in {exmsg.guild.name}:\n\n"
		for message in messages:
			post = f"{post}\n\n\n{message.author} ({message.author.id}): {message.content}"
		url = await postbin.postAsync(post)
		embed=discord.Embed(title=f"{len(messages)} Messages Purged in #{exmsg.channel.name}", description=f"View them here: {str(url).replace(',com','.com/raw')}", color=0xa50003, timestamp=datetime.now())
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		if not before.guild:
			return
		logchannel = await self.getlogchannel(before.guild)
		if logchannel == None:
			return
		embed=discord.Embed(color=0x1184ff, timestamp=datetime.now())
		embed.set_footer(text=f"User ID: {before.id}")
		embed.set_author(name=before, icon_url=before.avatar_url)
		# Nickname change
		if before.nick != after.nick:
			if not await self.islogenabled(before.guild, "nickname"):
				return
			embed.title="Nickname Changed"
			if before.nick == None:
				embed.title="Nickname Added"
			elif after.nick == None:
				embed.title="Nickname Removed"
			embed.add_field(name="Before:", value=f"```{before.nick}```", inline=False)
			embed.add_field(name="After:", value=f"```{after.nick}```", inline=False)
		# role change
		elif before.roles != after.roles:
			n = "\n"
			if not await self.islogenabled(before.guild, "rolechanges"):
				return
			embed.title="Member Roles Updated"
			if len(before.roles) < len(after.roles):
				embed.title="Role Added"
			elif len(before.roles) > len(after.roles):
				embed.title="Role Removed"
			embed.description=f"{n.join([r.mention for r in set(before.roles) ^ set(after.roles)])}"
		elif before.status != after.status:
			return
			if not await self.islogenabled(before.guild, "status"):
				return
			embed.title="Status Changed"
			embed.add_field(name="Before:", value=f"`{before.status}`")
			embed.add_field(name="After:", value=f"`{after.status}`")
		elif before.activity != after.activity:
			return
			if not await self.islogenabled(before.guild, "activity"):
				return
			embed.title="Activity Changed"
			if before.activity == None:
				embed.title="Activity Added"
			elif after.activity == None:
				embed.title="Activity Removed"
			if isinstance(before.activity, discord.CustomActivity):
				embed.add_field(name="Before:", value=f"```{before.activity.emoji} {before.activity.name}```", inline=False)
			else:
				embed.add_field(name="Before:", value=f"```I can't detect non-custom statuses yet :/```", inline=False)
			if isinstance(after.activity, discord.CustomActivity):
				embed.add_field(name="After:", value=f"```{after.activity.emoji} {after.activity.name}```", inline=False)
			else:
				embed.add_field(name="After:", value=f"```I can't detect non-custom statuses yet :/```", inline=False)
		if embed.title != embed.Empty:
			await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_user_update(self, before, after):
		for guild in self.bot.guilds:
			if before.id not in [m.id for m in guild.members]:
				continue
			logchannel = await self.getlogchannel(guild)
			if logchannel == None:
				continue
			embed=discord.Embed(color=0x1184ff, timestamp=datetime.now())
			embed.set_footer(text=f"User ID: {before.id}")
			embed.set_author(name=before, icon_url=before.avatar_url)
			bvalue = ""
			avalue = ""
			#Username change
			if before.name != after.name:
				if not await self.islogenabled(guild, "username"):
					return
				embed.title="Username Changed"
				bvalue=before.name
				avalue=after.name
			#Discriminator change
			elif before.discriminator != after.discriminator:
				if not await self.islogenabled(guild, "discriminator"):
					return
				embed.title="Discriminator Changed"
				bvalue=before.discriminator
				avalue=after.discriminator
			#Avatar change
			elif before.avatar_url != after.avatar_url:
				if not await self.islogenabled(guild, "avatar"):
					return
				embed.title="Avatar Updated"
				embed.description = f"[Avatar Link]({after.avatar_url})"
				embed.set_thumbnail(url=after.avatar_url)
			if (bvalue != "") and (avalue != ""):
				embed.add_field(name="Before:", value=bvalue, inline=False)
				embed.add_field(name="After:", value=avalue, inline=False)
			await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_member_join(self, member):
		logchannel = await self.getlogchannel(member.guild)
		if logchannel == None:
			return
		if not await self.islogenabled(member.guild, "join"):
			return
		embed=discord.Embed(timestamp=datetime.now(), color=2937504)
		embed.set_author(name=f"Member Joined {member.guild.name}", icon_url=member.avatar_url)
		embed.set_footer(text=f"{member} joined", icon_url=member.guild.icon_url)
		embed.add_field(name="User Info", value=f"""
		Ping: {member.mention}
		Username: [{member}](https://discord.com/users/{member.id})
		User ID: {member.id}""".replace("	", ""), inline=False)
		embed.add_field(name="Account Info", value=f"Account Created on: {member.created_at}\nAccount Age: {datetime.now() - member.created_at}", inline=False)
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		logchannel = await self.getlogchannel(member.guild)
		if logchannel == None:
			return
		if not await self.islogenabled(member.guild, "leave"):
			return
		embed=discord.Embed(timestamp=datetime.now(), color=10354688)
		embed.set_author(name=f"Member Left {member.guild.name}", icon_url=member.avatar_url)
		embed.set_footer(text=f"{member} left", icon_url=member.guild.icon_url)
		embed.add_field(name="User Info", value=f"""
		Ping: {member.mention}
		Username: [{member}](https://discord.com/users/{member.id})
		User ID: {member.id}""".replace("	", ""), inline=False)
		embed.add_field(name="Account Info", value=f"Account Created on: {member.created_at}\nAccount Age: {datetime.now() - member.created_at}", inline=False)
		await logchannel.send(embed=embed)


	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		if not member.guild:
			return
		logchannel = await self.getlogchannel(member.guild)
		if logchannel == None:
			return
		embed=discord.Embed(timestamp=datetime.now())
		embed.set_author(name=member, icon_url=member.avatar_url)
		embed.set_footer(text=f"User ID: {member.id}")
		if before.channel == None:
			if not await self.islogenabled(member.guild, "voicejoin"):
				return
			embed.title = "Member Joined Voice Channel"
			embed.description = f"{str(member)} joined {after.channel.name}"
			embed.color = 5496236
		elif after.channel == None:
			if not await self.islogenabled(member.guild, "voiceleave"):
				return
			embed.title = "Member Left Voice Channel"
			embed.description = f"{str(member)} left {before.channel.name}"
			embed.color=0xe41212
		elif before.channel != after.channel:
			if not await self.islogenabled(member.guild, "voicemove"):
				return
			if before.channel.id == after.channel.id:
				return
			embed.title = "Member Moved Voice Channels"
			embed.add_field(name="Before:", value=before.channel.name)
			embed.add_field(name="After:", value=after.channel.name)
			embed.color=0x1184ff
		else:
			return
		await logchannel.send(embed=embed)

#Ban/Unban
	@commands.Cog.listener()
	async def on_member_ban(self, guild, user: typing.Union[discord.User, discord.Member]):
		if not await self.islogenabled(guild, "ban"):
			return
		logchannel = await self.getlogchannel(guild)
		if logchannel == None:
			return
		embed=discord.Embed(title="🔨 Member Banned", description="📄lmao work in progress", color=0xe41212, timestamp=datetime.now())
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_member_unban(self, guild, user):
		if not await self.islogenabled(guild, "unban"):
			return
		logchannel = await self.getlogchannel(guild)
		if logchannel == None:
			return
		embed=discord.Embed(title="🔓 Member Unbanned", description=f"📄lmao work in progress", color=5496236, timestamp=datetime.now())
		await logchannel.send(embed=embed)

#Server Update
	@commands.Cog.listener()
	async def on_guild_update(self, before, after):
		if not await self.islogenabled(before, "serverupdates"):
			return
		logchannel = await self.getlogchannel(before)
		if logchannel == None:
			return
		embed=discord.Embed(title="✏️ Guild Updated", color=0x1184ff, timestamp=datetime.now())
		bvalue = ""
		avalue = ""
		if before.name != after.name:
			embed.set_thumbnail(url=before.icon_url)
			embed.title="Server Name Changed"
			bvalue=before.name
			avalue=after.name
		elif before.icon_url != after.icon_url:
			embed.title="Server Icon Changed"
			embed.description=f"[Link to New Icon]({after.icon_url})"
			embed.set_image(image=after.icon_url)
		elif before.region != after.region:
			embed.title="Server Region Changed"
			bvalue=before.region
			avalue=after.region
		if embed.title == embed.Empty:
			return
		if (bvalue != "") and (avalue != ""):
			embed.add_field(name="Before:", value=bvalue, inline=False)
			embed.add_field(name="After:", value=avalue, inline=False)
		await logchannel.send(embed=embed)

	# @commands.Cog.listener()
	# async def on_guild_emojis_update(self, guild, before, after):
#		if not await self.islogenabled(before, "emojis"):
#			return
#		logchannel = await self.getlogchannel(guild)
	# 	if logchannel == None:
	# 		return
	# 	embed=discord.Embed(title="Emoji Updated", description="lmao work in progress", color=0x1184ff, timestamp=datetime.now())
	# 	if len(before.emojis) > len(after.emojis):
	# 		embed.title="Emoji Deleted"
	# 		embed.color=0xe41212
	# 	elif len(before.emojis) < len(after.emojis):
	# 		embed.title="Emoji Created"
	# 		embed.color=5496236
	# 	await logchannel.send(embed=embed)


#Role Logging
	@commands.Cog.listener()
	async def on_guild_role_create(self, role):
		if not await self.islogenabled(role.guild, "rolecreate"):
			return
		logchannel = await self.getlogchannel(role.guild)
		if logchannel == None:
			return
		embed=discord.Embed(title="➕ Role Created", description=f"Name: {role.name}\nColor: {role.color}", color=role.color, timestamp=datetime.now())
		embed.set_footer(text=f"Role ID: {role.id}")
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_guild_role_update(self, before, after):
		if not await self.islogenabled(before.guild, "roleupdate"):
			return
		logchannel = await self.getlogchannel(before.guild)
		if logchannel == None:
			return
		embed=discord.Embed(title="✏️ Role Updated", description=f"Role Updated: {before.mention}", color=after.color, timestamp=datetime.now())
		bvalue = ""
		avalue = ""
		embed.set_footer(text=f"Role ID: {before.id}")
		if before.color != after.color:
			bvalue=f"Color: {before.color}"
			avalue=f"Color: {after.color}"
		elif before.name != after.name:
			bvalue=f"Name: {before.name}"
			avalue=f"Name: {after.name}"
		elif before.hoist != after.hoist:
			bvalue=f"Displayed Separately?: {self.yes if before.hoist else self.no}"
			avalue=f"Displayed Separately?: {self.yes if after.hoist else self.no}"
		elif before.position != after.position:
			return
#			bvalue=f"Position: {before.position}"
#			avalue=f"Position: {after.position}"
		elif before.permissions != after.permissions:
#			embed.add_field(name="Before:", value=f"Permissions: {dict(before.permissions)}")
#			embed.add_field(name="After:", value=f"Permissions: {dict(after.permissions)}")
			embed.add_field(name="NOTE:", value="This log is a work in progress, eventually it will show which permissions changed :)", inline=False)
		if (bvalue != "") and (avalue != ""):
			embed.add_field(name="Before:", value=bvalue, inline=False)
			embed.add_field(name="After:", value=avalue, inline=False)
		else:
			return
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_guild_role_delete(self, role):
		if not await self.islogenabled(role.guild, "roledelete"):
			return
		logchannel = await self.getlogchannel(role.guild)
		if logchannel == None:
			return
		embed=discord.Embed(title="❌ Role Deleted", description=f"""
Name: {role.name}
Color: {role.color}
Mentionable: {role.mentionable}
Displayed separately: {role.hoist}
Position: {role.position}
Created at: {role.created_at}""", color=role.color, timestamp=datetime.now())
		embed.set_footer(text=f"Role ID: {role.id}")
		await logchannel.send(embed=embed)
				    
	@commands.Cog.listener()
	async def on_guild_channel_create(self, channel):
		if not await self.islogenabled(channel.guild, "channelcreate"):
			return
		logchannel = await self.getlogchannel(channel.guild)
		if logchannel == None:
			return
		embed=discord.Embed(title=f"{channel.type} Channel Created".capitalize(), description=f"**Name:** {channel.name}\n**Category:** {channel.category}", color=5496236)
		embed.set_footer(text=f"Channel ID: {channel.id}")
		await logchannel.send(embed=embed)
				    
	@commands.Cog.listener()
	async def on_guild_channel_update(self, before, after):
		if not await self.islogenabled(before.guild, "channelupdate"):
			return
		logchannel = await self.getlogchannel(before.guild)
		if logchannel == None:
			return
		embed=discord.Embed(title=f"{after.type} Channel Updated".capitalize(), color=0x1184ff)
		embed.set_footer(text=f"Channel ID: {before.id}")
		bvalue = ""
		avalue = ""
		if before.name != after.name:
			bvalue=f"**Name:** `{before.name}`"
			avalue=f"**Name:** `{after.name}`"
		elif before.type == discord.ChannelType.text and before.topic != after.topic:
			bvalue=f"**Topic:** `{before.topic}`"
			avalue=f"**Topic:** `{after.topic}`"
		elif before.type != after.type:
			bvalue=f"**Type:** `{str(before.type).capitalize()}`"
			avalue=f"**Type:** `{str(after.type).capitalize()}`"
		elif before.category != after.category:
			if not channel.guild.get_channel(before.parent_id):
				return
			bvalue=f"**Category:** `{before.category}`"
			avalue=f"**Category:** `{after.category}`"
		if (bvalue == "") or (avalue == ""):
			return
		embed.add_field(name="Before:", value=bvalue, inline=False)
		embed.add_field(name="After:", value=avalue, inline=False)
		await logchannel.send(embed=embed)
				    
	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel):
		if not await self.islogenabled(channel.guild, "channeldelete"):
			return
		logchannel = await self.getlogchannel(channel.guild)
		if logchannel == None:
			return
		embed=discord.Embed(title=f"{channel.type} Channel Deleted".capitalize(), description=f"**Name:** {channel.name}\n**Category:** {channel.category}", color=0xe41212)
		embed.set_footer(text=f"Channel ID: {channel.id}")
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if not await self.islogenabled(self.bot.get_guild(payload.guild_id), "reactionadd"):
			return
		message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
		if not message.guild:
			return
		user = message.guild.get_member(payload.user_id)
		reaction = payload.emoji
		logchannel = await self.getlogchannel(message.guild)
		if logchannel == None:
			return
		embed=discord.Embed(title=f"Reaction Added by {user.nick or user.name}", color=563482, timestamp=datetime.now())
		if reaction.is_unicode_emoji():
			try:
				unicodereaction = unicodedata.name(reaction.name.replace("\U0000fe0f", ""))
				link = f"https://emojipedia.org/{unicodereaction.lower().replace(' ', '-')}"
			except:
				link = None
		else:
			link = str(reaction.url)
		embed.description=f"""
**User:** {user} (`{user.id}`)
**Message:** [This Message]({message.jump_url}) in {message.channel.mention} (`#{message.channel.name}`)
**Author:** {message.author} (`{message.author.id}`)
**Message Sent At:** {message.created_at}
**Reaction:** {reaction} (`{reaction}`)
{f"**Image Link:** [Link to Emoji]({link})" if link else ""}
"""
		embed.set_footer(text=user, icon_url=user.avatar_url)
		if reaction.is_custom_emoji():
			embed.set_thumbnail(url=link)
		await logchannel.send(embed=embed)
		if message.channel.id == 755982484444938290 and (user.id == message.author.id):
			await message.remove_reaction(reaction, user)

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		if not await self.islogenabled(self.bot.get_guild(payload.guild_id), "reactionremove"):
			return
		message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
		user = message.guild.get_member(payload.user_id)
		reaction = payload.emoji
		if not message.guild:
			return
		logchannel = await self.getlogchannel(message.guild)
		if logchannel == None:
			return
		if reaction.is_unicode_emoji():
			try:
				unicodereaction = unicodedata.name(reaction.name.replace("\U0000fe0f", ""))
				link = f"https://emojipedia.org/{unicodereaction.lower().replace(' ', '-')}"
			except:
				link = None
		else:
			link = str(reaction.url)
		embed=discord.Embed(title=f"Reaction Removed by {user.nick or user.name}", color=11337728, timestamp=datetime.now())
		embed.description=f"""
**User:** {user} (`{user.id}`)
**Message:** [This Message]({message.jump_url}) in {message.channel.mention} (`#{message.channel.name}`)
**Author:** {message.author} (`{message.author.id}`)
**Message Sent At:** {message.created_at}
**Reaction:** {reaction} (`{reaction}`)
{f"**Image Link:** [Link to Emoji]({link})" if link else ""}
"""
		embed.set_footer(text=user, icon_url=user.avatar_url)
		if reaction.is_custom_emoji():
			embed.set_thumbnail(url=link)
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_reaction_clear(self, message, reactions):
		if not await self.islogenabled(self.bot.get_guild(message.guild.id), "reactionclear"):
			return
		reactlist = ", ".join(reactions)
		rawreactlist = "`, `".join(reactions)
		logchannel = await self.getlogchannel(message.guild)
		embed=discord.Embed(title="Reactions Cleared", color=0xa50003, timestamp=datetime.now())
		embed.description=f"""
**Message:** [This Message]({message.jump_url}) in {message.channel.mention} (`#{message.channel.name}`)
**Author:** {message.author} (`{message.author.id}`)
**Message Sent At:** {message.created_at}
**Reactions Cleared:** {reactlist} || {rawreactlist}
"""
		await logchannel.send(embed=embed)


def setup(bot):
	bot.add_cog(Logging(bot))
	print('[LoggingCog] Logging cog loaded')
