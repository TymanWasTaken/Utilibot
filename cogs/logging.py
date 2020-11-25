import discord, dpytils, postbin, aiofiles, json, typing, unicodedata, aiosqlite
from discord.ext import commands
from datetime import datetime

utils = dpytils.utils()

class Logging(commands.Cog):
	def __init__(self, bot):
		self.yes = bot.get_emoji(778489135870377994)
		self.no = bot.get_emoji(778489134741979186)
		self.bot = bot
		self.logs = {
		"messages":["edit", "delete", "purge"],
		"users":["nickname", "userroles", "status", "activity", "username", "discriminator", "avatar", "ban", "unban"],
		"joinleave":["join", "leave"],
		"voice":["voicejoin", "voiceleave", "voicemove"],
		"server":["serverupdates", "emojis"],
		"roles":["rolecreate", "roleupdate", "roledelete"],
		"reactions":["reactionadd", "reactionremove", "reactionclear"]
		}
		self.log_flat = {x for v in self.logs.values() for x in v}

	async def islogenabled(self, guild, log):
		if not guild:
			return False
		db = await self.bot.dbquery("logging", "guildid=" + str(guild.id))
		if len(db) < 1:
			return False
		data = json.loads(db[0][1])
		if log not in data:
			return False
		else:
			return data[log]

	async def getlogs(self, guild):
		if not guild:
			return None
		db = await self.bot.dbquery("logging", "guildid=" + str(guild.id))
		if len(db) < 1:
			return None
		data = json.loads(db[0][1])
		return data

	async def setlogs(self, guild, data):
		if not guild:
			return None
		try:
			await self.bot.dbexec(("INSERT INTO logging VALUES (?, ?)", (guild.id, json.dumps(data))))
		except aiosqlite.IntegrityError:
			await self.bot.dbexec(("DELETE FROM logging WHERE guildid=?", (guild.id,)))
			await self.bot.dbexec(("INSERT INTO logging VALUES (?, ?)", (guild.id, json.dumps(data))))

	@commands.group(invoke_without_command=True)
	@commands.has_permissions(manage_guild=True)
	@commands.guild_only()
	async def log(self, ctx):
		"""
		Shows logging settings for the current server.
		"""
		db = await self.getlogs(ctx.guild)
		if db == None:
			db = {}
		for log in list(db):
			if log not in self.log_flat:
				db.pop(log)
		await self.setlogs(ctx.guild, db)
		logs = ""
		for log in sorted(self.log_flat):
			logs += f"{self.yes if await self.islogenabled(ctx.guild, log) else self.no} `{log}`\n"
		await ctx.send(f"""
Enabled logs:
{logs}""")

	@log.command()
	@commands.has_permissions(manage_guild=True)
	async def enable(self, ctx, log: str):
		"""
		Enable one of the logs.
		"""
		if log not in self.log_flat:
			return await ctx.send("Not a valid log.")
		db = await self.getlogs(ctx.guild)
		if db == None:
			db = {}
		db[log] = True
		await self.setlogs(ctx.guild, db)
		await ctx.send(f"Enabled log `{log}`")

	@log.command()
	@commands.has_permissions(manage_guild=True)
	async def disable(self, ctx, log: str):
		"""
		Disable one of the logs.
		"""
		if log not in self.log_flat:
			return await ctx.send("Not a valid log.")
		db = await self.getlogs(ctx.guild)
		if db == None:
			db = {}
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
		logchannel = discord.utils.get(before.guild.text_channels, name="utilibot-logs")
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
		logchannel = discord.utils.get(message.guild.text_channels, name="utilibot-logs")
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
		if not messages[0].guild:
			return
		if not await self.islogenabled(messages[0].guild, "purge"):
			return
		obj = messages[0]
		logchannel = discord.utils.get(obj.guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		post = f"{len(messages)} messages deleted in #{obj.channel.name} in {obj.guild.name}:\n\n"
		for message in messages:
			post = f"{post}\n\n\n{message.author} ({message.author.id}): {message.content}"
		url = await postbin.postAsync(post)
		embed=discord.Embed(title=f"{len(messages)} Messages Purged in #{obj.channel.name}", description=f"View them here: {str(url).replace(',com','.com/raw')}", color=0xa50003, timestamp=datetime.now())
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		if not before.guild:
			return
		logchannel = discord.utils.get(before.guild.text_channels, name="utilibot-logs")
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
			if not await self.islogenabled(before.guild, "status"):
				return
			embed.title="Status Changed"
			embed.add_field(name="Before:", value=f"`{before.status}`")
			embed.add_field(name="After:", value=f"`{after.status}`")
		elif before.activity != after.activity:
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
			for channel in guild.text_channels:
				if channel.name == "utilibot-logs":
					logchannel = channel
					break
			else:
				logchannel = None
			if logchannel == None:
				continue
			embed=discord.Embed(color=0x1184ff, timestamp=datetime.now())
			embed.set_footer(text=f"User ID: {before.id}")
			embed.set_author(name=before, icon_url=before.avatar_url)
			#Username change
			if before.name != after.name:
				if not await self.islogenabled(guild, "username"):
					return
				embed.title="Username Changed"
				embed.add_field(name="Before:", value=f"```{before.name}```", inline=False)
				embed.add_field(name="After:", value=f"```{after.name}```", inline=False)
			#Discriminator change
			elif before.discriminator != after.discriminator:
				if not await self.islogenabled(guild, "discriminator"):
					return
				embed.title="Discriminator Changed"
				embed.add_field(name="Before:", value=f"```{before.discriminator}```", inline=False)
				embed.add_field(name="After:", value=f"```{after.discriminator}```", inline=False)
			#Avatar change
			elif before.avatar_url != after.avatar_url:
				if not await self.islogenabled(guild, "avatar"):
					return
				embed.title="Avatar Updated"
				embed.description = f"[Avatar Link]({after.avatar_url})"
				embed.set_thumbnail(url=after.avatar_url)
			await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_member_join(self, member):
		logchannel = discord.utils.get(member.guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		embed=discord.Embed(timestamp=datetime.now(), color=2937504)
		embed.set_author(name=f"Member Joined {ctx.guild.name}", icon_url=member.avatar_url)
		embed.set_footer(text=f"{member} joined", icon_url=member.guild.avatar_url)
		embed.add_field(name="User Info", value=f"""
		Ping: {member.mention}
		Username: [{user}](https://discord.com/users/{user.id})
		User ID: {user.id}""", inline=False)
		embed.add_field(name="Account Info", value=f"""
		Account Created on: {member.created_at}
		Account Age: {datetime.now() - member.created_at}""", inline=False)
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		logchannel = discord.utils.get(member.guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		embed=discord.Embed(timestamp=datetime.now(), color=10354688)
		embed.set_author(name=f"Member Left {ctx.guild.name}", icon_url=member.avatar_url)
		embed.set_footer(text=f"{member} left", icon_url=member.guild.icon_url)
		embed.add_field(name="User Info", value=f"""
		Ping: {member.mention}
		Username: [{user}](https://discord.com/users/{user.id})
		User ID: {user.id}""", inline=False)
		embed.add_field(name="Account Info", value=f"""
		Account Created on: {member.created_at}
		Account Age: {datetime.now() - member.created_at}""", inline=False)
		await logchannel.send(embed=embed)


	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		if not member.guild:
			return
		logchannel = discord.utils.get(member.guild.text_channels, name="utilibot-logs")
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
		embed.set_image(image=after.icon_url)
		if embed.title == embed.Empty:
			return
		await logchannel.send(embed=embed)

	# @commands.Cog.listener()
	# async def on_guild_emojis_update(self, guild, before, after):
#		if not await self.islogenabled(before, "emojis"):
#			return
	# 	logchannel = discord.utils.get(guild.text_channels, name="utilibot-logs")
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
		logchannel = discord.utils.get(role.guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		embed=discord.Embed(title="➕ Role Created", description=f"Name: {role.name}\nColor: {role.color}", color=role.color, timestamp=datetime.now())
		embed.set_footer(text=f"Role ID: {role.id}")
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_guild_role_update(self, before, after):
		if not await self.islogenabled(before.guild, "roleupdate"):
			return
		logchannel = discord.utils.get(before.guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		embed=discord.Embed(title="✏️ Role Updated", color=after.color, timestamp=datetime.now())
		embed.set_footer(text=f"Role ID: {before.id}")
		if before.color != after.color:
			embed.add_field(name="Before:", value=f"Color: {before.color}")
			embed.add_field(name="After:", value=f"Color: {after.color}")
		elif before.name != after.name:
			embed.add_field(name="Before:", value=f"Name: {before.name}")
			embed.add_field(name="After:", value=f"Name: {after.name}")
		elif before.hoist != after.hoist:
			embed.add_field(name="Before:", value=f"Displayed Separately?: {self.yes if before.hoist else self.no}")
			embed.add_field(name="After:", value=f"Displayed Separately?: {self.yes if after.hoist else self.no}")
		elif before.position != after.position:
			embed.add_field(name="Before:", value=f"Position: {before.position}")
			embed.add_field(name="After:", value=f"Position: {after.position}")
		elif before.permissions != after.permissions:
			embed.add_field(name="Before:", value=f"Permissions: {dict(before.permissions)}")
			embed.add_field(name="After:", value=f"Permissions: {dict(after.permissions)}")
			embed.add_field(name="NOTE:", value="This log is a work in progress, eventually it will show which permissions changed :)", inline=False)
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_guild_role_delete(self, role):
		if not await self.islogenabled(role.guild, "roledelete"):
			return
		logchannel = discord.utils.get(role.guild.text_channels, name="utilibot-logs")
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
	async def on_raw_reaction_add(self, payload):
		if not await self.islogenabled(self.bot.get_guild(payload.guild_id), "reactionadd"):
			return
		message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
		if not message.guild:
			return
		user = message.guild.get_member(payload.user_id)
		reaction = payload.emoji
		logchannel = discord.utils.get(message.guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		embed=discord.Embed(title=f"Reaction Added by {user.nick or user.name}", color=563482, timestamp=datetime.now())
		if reaction.is_unicode_emoji():
			try:
				unicodereaction = unicodedata.name(payload.emoji.name.replace("\U0000fe0f", ""))
				link = f"https://emojipedia.org/{unicodereaction.lower().replace(' ', '-')}"
			except:
				link = None
		else:
			link = str(payload.emoji.url)
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
			await message.remove_reaction(payload.emoji, user)

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		if not await self.islogenabled(self.bot.get_guild(payload.guild_id), "reactionremove"):
			return
		user = message.guild.get_member(payload.user_id)
		message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
		if not message.guild:
			return

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

#	@commands.Cog.listener()
#	async def on_raw_reaction_clear(self, payload):
#		if not await self.islogenabled(self.bot.get_guild(payload.guild_id), "reactionclear"):
#			return
#		message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
#		user = message.guild.get_member(payload.user_id)
#		reactions = payload.emojis
#		logchannel = discord.utils.get(message.guild.text_channels, name="utilibot-logs")
#		embed=discord.Embed(title="Reactions Cleared", color=0xa50003, timestamp=datetime.now())
#		embed.description=f"""
#**Message:** [This Message]({message.jump_url}) in {message.channel.mention} (`#{message.channel.name}`)
#**Author:** {message.author} (`{message.author.id}`)
#**Message Sent At:** {message.created_at}
#**Reactions Cleared:** {reactions.join(" ")} (`{reactions.join("` `")}`)
#"""
#		await logchannel.send(embed=embed)


def setup(bot):
	bot.add_cog(Logging(bot))
	print('[LoggingCog] Logging cog loaded')
