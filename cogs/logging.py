import discord, dpytils, postbin, aiofiles, json, typing
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

class Logging(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(invoke_without_command=True)
	async def log(self, ctx):
		"""
		Will config logging eventually.
		"""
		await ctx.send("Logging coming soon™!")

	@log.command()
	@commands.has_permissions(manage_guild=True)
	async def enable(self, ctx, log: str):
		"""
		Enable one of the logs.
		"""
		if log not in ["status", "activity", "nickname", "deletes", "edits", "avatar", "name"]:
			return await ctx.send("Not a valid log.")
		db = await readDB()
		if str(ctx.guild.id) not in db["logs"]:
			db["logs"][str(ctx.guild.id)] = {}
		db["logs"][str(ctx.guild.id)][log] = True
		await writeDB(db)

	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		if before.content == after.content:
			return
		if not before.guild:
			return
		logchannel = discord.utils.get(before.guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		embed = discord.Embed(title=f"Message Edited in #{before.channel.name}", description=f"**Before:**```{before.clean_content.replace('`', '​`​')}```**After:**```{after.clean_content.replace('`', '​`​')}```Message link: [click here]({before.jump_url})", color=0x1184ff, timestamp=datetime.now())
		embed.set_author(name=before.author, icon_url=before.author.avatar_url)
		embed.set_footer(text=f"Author ID: {before.author.id}")
		if (message.embeds and not message.content):
			embed.description=f"**Before:**```{before.cclean_content.replace('`', '​`​')}```**After:**```Message has Embed Only```Message link: [click here]({before.jump_url})"
		await logchannel.send(embed=embed)
	
	@commands.Cog.listener()
	async def on_message_delete(self, message):
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
		logchannel = discord.utils.get(before.guild.text_channels, name="utilibot-logs")
		embed=discord.Embed(color=0x1184ff, timestamp=datetime.now())
		embed.set_footer(text=f"User ID: {before.id}")
		embed.set_author(name=before, icon_url=before.avatar_url)
		# Nickname change
		if before.nick != after.nick:
			embed.title="Nickname Changed"
			if before.nick == None:
				embed.title="Nickname Added"
			elif after.nick == None:
				embed.title="Nickname Removed"
			embed.add_field(name="Before:", value=f"```{before.nick}```", inline=False)
			embed.add_field(name="After:", value=f"```{after.nick}```", inline=False)
		# role change
		elif before.roles != after.roles:
			embed.title="Member Roles Updated"
			if len(before.roles) < len(after.roles):
				embed.title="Role Added"
			elif len(before.roles) > len(after.roles):
				embed.title="Role Removed"
			embed.description="Lol idk how to detect specific role yet"
		# status change
		# elif before.status != after.status:
		#	embed.title="Status Changed"
		#	embed.add_field(name="Before:", value=f"`{before.status}`")
		#	embed.add_field(name="After:", value=f"`{after.status}`")
		#activity change
		# elif before.activity != after.activity:
		# 	embed.title="Status Changed"
		# 	if before.activity == None:
		# 		embed.title="Status Added"
		# 	elif after.activity == None:
		# 		embed.title="Activity Removed"
		# 	embed.add_field(name="Before:", value=f"```{before.activity.name}\n{before.activity.details}```", inline=False)
		# 	embed.add_field(name="After:", value=f"```{after.activity.details}```", inline=False)
		if embed.title != embed.Empty:
			await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_user_update(self, before, after):
		for guild in self.bot.guilds:
			logchannel = discord.utils.get(guild.text_channels, name="utilibot-logs")
			if logchannel == None:
				return
			embed=discord.Embed(color=0x1184ff, timestamp=datetime.now())
			embed.set_footer(text=f"User ID: {before.id}")
			embed.set_author(name=before, icon_url=before.avatar_url)
			#Username change
			if before.name != after.name:
				embed.title="Username Changed"
				embed.add_field(name="Before:", value=f"```{before.name}```", inline=False)
				embed.add_field(name="After:", value=f"```{after.name}```", inline=False)
			#Discriminator change
			elif before.discriminator != after.discriminator:
				embed.title="Discriminator Changed"
				embed.add_field(name="Before:", value=f"```{before.discriminator}```", inline=False)
				embed.add_field(name="After:", value=f"```{after.discriminator}```", inline=False)
			#Avatar change
			elif before.avatar_url != after.avatar_url:
				embed.title="Avatar Updated"
				embed.add_field(name="Before:", value=f"[Link]({before.avatar_url})", inline=False)
				embed.add_field(name="After:", value=f"[Link]({after.avatar_url})", inline=False)
				embed.set_thumbnail(after.avatar_url)
			await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		logchannel = discord.utils.get(member.guild.text_channels, name="utilibot-logs")
		embed=discord.Embed(timestamp=datetime.now())
		embed.set_author(name=member, icon_url=member.avatar_url)
		embed.set_footer(text=f"User ID: {member.id}")
		if before.channel == None:
			embed.title = "Member Joined Voice Channel"
			embed.description = f"{str(member)} joined {after.channel.name}"
			embed.color = 5496236
		elif after.channel == None:
			embed.title = "Member Left Voice Channel"
			embed.description = f"{str(member)} left {before.channel.name}"
			embed.color=0xe41212
		else:
			embed.title = "Member Moved Voice Channels"
			embed.add_field(name="Before:", value=before.channel.name)
			embed.add_field(name="After:", value=after.channel.name)
			embed.color=0x1184ff
		await logchannel.send(embed=embed)

#Ban/Unban
	@commands.Cog.listener()
	async def on_member_ban(self, guild, user: typing.Union[discord.User, discord.Member]):
		logchannel = discord.utils.get(guild.text_channels, name="utilibot-logs")
		embed=discord.Embed(title="🔨 Member Banned", description="📄lmao work in progress", color=0xe41212)
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_member_unban(self, guild, user):
		logchannel = discord.utils.get(guild.text_channels, name="utilibot-logs")
		embed=discord.Embed(title="🔓 Member Unbanned", description=f"📄lmao work in progress", color=5496236)
		await logchannel.send(embed=embed)

#Server Update
	@commands.Cog.listener()
	async def on_guild_update(self, before, after):
		logchannel = discord.utils.get(before.text_channels, name="utilibot-logs")
		embed=discord.Embed(title="✏️ Guild Updated", description="lmao work in progress", color=0x1184ff)
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_guild_emojis_update(self, guild, before, after):
		logchannel = discord.utils.get(guild.text_channels, name="utilibot-logs")
		embed=discord.Embed(title="Emoji Updated", description="lmao work in progress", color=0x1184ff)
		if len(before.emojis) > len(after.emojis):
			embed.title="Emoji Deleted"
			embed.color=0xe41212
		elif len(before.emojis) < len(after.emojis):
			embed.title="Emoji Created"
			embed.color=5496236
		await logchannel.send(embed=embed)


#Role Logging
	@commands.Cog.listener()
	async def on_guild_role_create(self, role):
		logchannel = discord.utils.get(role.guild.text_channels, name="utilibot-logs")
		embed=discord.Embed(title="➕ Role Created", description=f"Name: {role.name}\nColor: {role.color}", color=role.color)
		embed.set_footer(text=f"Role ID: {role.id}")
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_guild_role_update(self, before, after):
		logchannel = discord.utils.get(before.guild.text_channels, name="utilibot-logs")
		embed=discord.Embed(title="✏️ Role Updated", color=after.color)
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
		logchannel = discord.utils.get(before.guild.text_channels, name="utilibot-logs")
		embed=discord.Embed(title="❌ Role Deleted", description=f"""
Name: {role.name}
Color: {role.color}
Mentionable: {role.mentionable}
Displayed separately: {role.hoist}
Position: {role.position}
Number of Members with Role: {len(role.members)}
Created at: {role.created_at}""", color=role.color)
		embed.set_footer(text=f"Role ID: {role.id}")
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		message = reaction.message
		logchannel = discord.utils.get(message.guild.text_channels, name="utilibot-logs")
		embed=discord.Embed(title=f"Reaction Added by {user.nick or user.name}", color=563482)
		embed.description=f"""
**User:** {user} (`{user.id}`)
**Message:** [This Message]({message.jump_url}) in {message.channel.mention} (`#{message.channel.name}`)
**Author:** {message.author} (`{message.author.id}`)
**Message Sent At:** {message.created_at}
**Reaction:** {reaction} (`{reaction}`)
"""
		embed.set_footer(text=user, icon_url=user.avatar_url)
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_reaction_remove(self, reaction, user):
		message = reaction.message
		logchannel = discord.utils.get(message.guild.text_channels, name="utilibot-logs")
		embed=discord.Embed(title=f"Reaction Removed by {user.nick or user.name}", color=11337728)
		embed.description=f"""
**User:** {user} (`{user.id}`)
**Message:** [This Message]({message.jump_url}) in {message.channel.mention} (`#{message.channel.name}`)
**Author:** {message.author} (`{message.author.id}`)
**Message Sent At:** {message.created_at}
**Reaction:** {reaction} (`{reaction}`)
"""
		embed.set_footer(text=user, icon_url=user.avatar_url)
		await logchannel.send(embed=embed)

	@commands.Cog.listener()
	async def on_reaction_clear(self, message, reactions):
		logchannel = discord.utils.get(message.guild.text_channels, name="utilibot-logs")
		embed=discord.Embed(title="Reactions Cleared", color=0xa50003)
		embed.description=f"""
**Message:** [This Message]({message.jump_url}) in {message.channel.mention} (`#{message.channel.name}`)
**Author:** {message.author} (`{message.author.id}`)
**Message Sent At:** {message.created_at}
**Reactions Cleared:** {reaction} (`{reaction}`)
"""
		await logchannel.send(embed=embed)


def setup(bot):
	bot.add_cog(Logging(bot))
	print('[LoggingCog] Logging cog loaded')