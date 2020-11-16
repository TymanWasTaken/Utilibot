import discord, dpytils, postbin, aiofiles, json
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
		logchannel = discord.utils.get(before.guild.text_channels, name="utilibot-logs")
		if logchannel == None:
			return
		embed = discord.Embed(title=f"Message Edited in #{before.channel.name}", description=f"**Before:**```{before.clean_content.replace('`', '​`​')}```**After:**```{after.clean_content.replace('`', '​`​')}```Message link: [click here]({before.jump_url})", color=0x1184ff, timestamp=datetime.now())
		embed.set_author(name=before.author, icon_url=before.author.avatar_url)
		embed.set_footer(text=f"Author ID: {before.author.id}")
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
		logchannel = discord.utils.get(self.bot.guild.text_channels, name="utilibot-logs")
		embed=discord.Embed(color=0x1184ff, timestamp=datetime.now())
		embed.set_thumbnail(member.avatar_url)
		if before == None:
			embed.title = "Member joined vc"
			embed.description = f"{str(member)} joined {after.mention}"
		await logchannel.send(embed=embed)
		


def setup(bot):
	bot.add_cog(Logging(bot))
	print('[LoggingCog] Logging cog loaded')