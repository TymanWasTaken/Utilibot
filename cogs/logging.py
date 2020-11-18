import discord, dpytils, postbin, aiofiles, json, typing, unicodedata
from discord.ext import commands
from datetime import datetime

utils = dpytils.utils()

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

async def islogenabled(guild, log):
	db = await readDB()
	if str(guild.id) not in db["logs"]:
		return False
	if log not in db["logs"][str(guild.id)]:
		return False
	else:
		return db["logs"][str(guild.id)][log]


class Logging(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.logs = {
		"messages":["edit", "delete", "purge"],
		"users":["nickname", "rolechanges", "status", "activity", "username", "discriminator", "avatar", "ban", "unban"],
		"voice":["voicejoin", "voiceleave", "voicemove"],
		"server":["serverupdates", "emojis"],
		"roles":["rolecreate", "roleupdate", "roledelete"],
		"reactions":["reactionadd", "reactionremove", "reactionclear"]
		}

	@commands.group(invoke_without_command=True)
	@commands.has_permissions(manage_guild=True)
	async def log(self, ctx):
		"""
		Shows logging settings for the current server.
		"""
		db = await readDB()
		if str(ctx.guild.id) not in db["logs"]:
			db["logs"][str(ctx.guild.id)] = {}
		await writeDB(db)
		logs = ""
		for log in db["logs"][str(ctx.guild.id)]:
			logs += f"{'✅' if db['logs'][str(ctx.guild.id)][log] else '❌'} {log}\n"
#		await ctx.send(f"""
#Enabled logs:
#{logs}""")
		await ctx.send("logging is temporarily disabled while we get log categories figured out")

	@log.command()
	@commands.has_permissions(manage_guild=True)
	async def enable(self, ctx, log: str):
		"""
		Enable one of the logs.
		"""
		if log not in self.logs:
			return await ctx.send("Not a valid log.")
		db = await readDB()
		if str(ctx.guild.id) not in db["logs"]:
			db["logs"][str(ctx.guild.id)] = {}
		db["logs"][str(ctx.guild.id)][log] = True
		await writeDB(db)
		await ctx.send(f"Enabled log {log}")

	@log.command()
	@commands.has_permissions(manage_guild=True)
	async def disable(self, ctx, log: str):
		"""
		Disable one of the logs.
		"""
		if log not in self.logs:
			return await ctx.send("Not a valid log.")
		db = await readDB()
		if str(ctx.guild.id) not in db["logs"]:
			db["logs"][str(ctx.guild.id)] = {}
		db["logs"][str(ctx.guild.id)][log] = False
		await writeDB(db)
		await ctx.send(f"Disabled log {log}")

	@log.command()
	@commands.has_permissions(manage_guild=True)
	async def enableall(self, ctx):
		"""
		Enable all of the logs.
		"""
		db = await readDB()
		for log in self.logs:
			if str(ctx.guild.id) not in db["logs"]:
				db["logs"][str(ctx.guild.id)] = {}
			db["logs"][str(ctx.guild.id)][log] = True
		await writeDB(db)
		await ctx.send(f"Enabled all logs.")

	@log.command()
	@commands.has_permissions(manage_guild=True)
	async def disableall(self, ctx):
		"""
		Disable all of the logs.
		"""
		db = await readDB()
		for log in self.logs:
			if str(ctx.guild.id) not in db["logs"]:
				db["logs"][str(ctx.guild.id)] = {}
			db["logs"][str(ctx.guild.id)][log] = False
		await writeDB(db)
		await ctx.send(f"Disabled all logs.")

	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		
		if before.content == after.content:
			return
		if not before.guild:
			return
		if not await islogenabled(before.guild, "edit"):
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
		embed = discord.Embed(title=f"Message Edited in #{before.channel.name}", color=0x1184ff, timestamp=datetime.now())
		embed.add_field(name="Before:", value=f"```{before_content}```", inline=False)
		embed.add_field(name="After:", value=f"```{after_content}```", inline=False)
		embed.set_author(name=before.author, icon_url=before.author.avatar_url)
		embed.set_footer(text=f"Author ID: {before.author.id}")
		try:
			await logchannel.send(embed=embed)
		except discord.HTTPException:
			before_content = await postbin.postAsync(before_content)
			after_content = await postbin.postAsync(before_content)
			embed = discord.Embed(title=f"Message Edited in #{before.channel.name}", color=0x1184ff, timestamp=datetime.now())
			embed.add_field(name="Before:", value=f"```{before_content}```", inline=False)
			embed.add_field(name="After:", value=f"```{after_content}```", inline=False)
			embed.set_author(name=before.author, icon_url=before.author.avatar_url)
			embed.set_footer(text=f"Author ID: {before.author.id}")
			await logchannel.send(embed=embed)
	
	@commands.Cog.listener()
	async def on_message_delete(self, message):
		if not message.guild:
			return
		if not await islogenabled(message.guild, "delete"):
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
		if not await islogenabled(messages[0].guild, "purge"):
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
			if not await islogenabled(before.guild, "nickname"):
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
			if not await islogenabled(before.guild, "rolechanges"):
				return
			embed.title="Member Roles Updated"
			if len(before.roles) < len(after.roles):
				embed.title="Role Added"
			elif len(before.roles) > len(after.roles):
				embed.title="Role Removed"
			embed.description="Lol idk how to detect specific role yet"
		elif before.status != after.status:
			if not await islogenabled(before.guild, "status"):
				return
			embed.title="Status Changed"
			embed.add_field(name="Before:", value=f"`{before.status}`")
			embed.add_field(name="After:", value=f"`{after.status}`")
		elif before.activity != after.activity:
			if not await islogenabled(before.guild, "activity"):
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
				if not await islogenabled(guild, "username"):
					return
				embed.title="Username Changed"
				embed.add_field(name="Before:", value=f"```{before.name}```", inline=False)
				embed.add_field(name="After:", value=f"```{after.name}```", inline=False)
			#Discriminator change
			elif before.discriminator != after.discriminator:
				if not await islogenabled(guild, "discriminator"):
					return
				embed.title="Discriminator Changed"
				embed.add_field(name="Before:", value=f"```{before.discriminator}```", inline=False)
				embed.add_field(name="After:", value=f"```{after.discriminator}```", inline=False)
			#Avatar change
			elif before.avatar_url != after.avatar_url:
				if not await islogenabled(guild, "avatar"):
					return
				embed.title="Avatar Updated"
				embed.add_field(name="Before:", value=f"[Link]({before.avatar_url})", inline=False)
				embed.add_field(name="After:", value=f"[Link]({after.avatar_url})", inline=False)
				embed.set_thumbnail(url=after.avatar_url)
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
			if not await islogenabled(member.guild, "voicejoin"):
				return
			embed.title = "Member Joined Voice Channel"
			embed.description = f"{str(member)} joined {after.channel.name}"
			embed.color = 5496236
		elif after.channel == None:
			if not await islogenabled(member.guild, "voiceleave"):
				return
			embed.title = "Member Left Voice Channel"
			embed.description = f"{str(member)} left {before.channel.name}"
			embed.color=0xe41212
		elif before.channel != after.channel:
			if not await islogenabled(member.guild, "voicemove"):
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
		if not await islogenabled(guild, "ban"):
			return
		logchannel = discord.utils.get(guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		embed=discord.Embed(title="🔨 Member Banned", description="📄lmao work in progress", color=0xe41212, timestamp=datetime.now())
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_member_unban(self, guild, user):
		if not await islogenabled(guild, "unban"):
			return
		logchannel = discord.utils.get(guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		embed=discord.Embed(title="🔓 Member Unbanned", description=f"📄lmao work in progress", color=5496236, timestamp=datetime.now())
		await logchannel.send(embed=embed)

# #Server Update
# 	@commands.Cog.listener()
# 	async def on_guild_update(self, before, after):
#		if not await islogenabled(before, "serverupdates"):
#			return
# 		logchannel = discord.utils.get(before.text_channels, name="utilibot-logs")
# 		if logchannel == None:
# 			return
# 		embed=discord.Embed(title="✏️ Guild Updated", description="lmao work in progress", color=0x1184ff, timestamp=datetime.now())
# 		await logchannel.send(embed=embed)

	# @commands.Cog.listener()
	# async def on_guild_emojis_update(self, guild, before, after):
#		if not await islogenabled(before, "emojis"):
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
		if not await islogenabled(role.guild, "rolecreate"):
			return
		logchannel = discord.utils.get(role.guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		embed=discord.Embed(title="➕ Role Created", description=f"Name: {role.name}\nColor: {role.color}", color=role.color, timestamp=datetime.now())
		embed.set_footer(text=f"Role ID: {role.id}")
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_guild_role_update(self, before, after):
		if not await islogenabled(before.guild, "roleupdate"):
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
			embed.add_field(name="Before:", value=f"Displayed Separately?: {before.hoist}")
			embed.add_field(name="After:", value=f"Displayed Separately?: {after.name}")
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_guild_role_delete(self, role):
		if not await islogenabled(role.guild, "roledelete"):
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
Number of Members with Role: {len(role.members)}
Created at: {role.created_at}""", color=role.color, timestamp=datetime.now())
		embed.set_footer(text=f"Role ID: {role.id}")
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if not await islogenabled(self.bot.get_guild(payload.guild_id), "reactionadd"):
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

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		if not await islogenabled(self.bot.get_guild(payload.guild_id), "reactionremove"):
			return
		message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
		if not message.guild:
			return
		user = message.guild.get_member(payload.user_id)
		reaction = payload.emoji
		logchannel = discord.utils.get(message.guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		if reaction.is_unicode_emoji():
			try:
				unicodereaction = unicodedata.name(payload.emoji.name.replace("\U0000fe0f", ""))
				link = f"https://emojipedia.org/{unicodereaction.lower().replace(' ', '-')}"
			except:
				link = None
		else:
			link = str(payload.emoji.url)
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

#	@commands.Cog.listener()
#	async def on_raw_reaction_clear(self, payload):
#		if not await islogenabled(self.bot.get_guild(payload.guild_id), "reactionclear"):
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
