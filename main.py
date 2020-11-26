# Imports
import discord, os, time, glob, postbin, traceback, cogs, importlib, aiofiles, json, textwrap, re, sys, aiosqlite, dpytils
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv
music = importlib.import_module("cogs.music")
load_dotenv(verbose=True)
intents = discord.Intents().all()

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

# json, not used

async def getprefixes(bot, message):
	prefixes = ['<@755084857280954550> ', '<@!755084857280954550> ']
	defaults = ['<@755084857280954550> ', '<@!755084857280954550> ', 'u!', 'U!']
	data = await readDB()
	if not message.guild:
		return defaults
	elif str(message.guild.id) in data['prefixes']:
		prefixes.append(data['prefixes'][str(message.guild.id)])
		return prefixes
	else:
		return defaults

# sqlite, used

async def query(table, value="*", condition=None):
	async with aiosqlite.connect('data.db') as db:
		async with db.execute(f"SELECT {value} FROM {table}{ ' WHERE ' + condition if condition != None else ''}") as cursor:
			return await cursor.fetchall()

async def dbinsert(table, values, params=None):
	if not isinstance(values, tuple):
		raise TypeError("Parameter \"values\" must be a tuple.")
	if not isinstance(params, tuple) and params != None:
		raise TypeError("Parameter \"params\" must be a tuple.")
	async with aiosqlite.connect('data.db') as db:
		if params != None:
			await db.execute(f"INSERT INTO {table} VALUES ({','.join(values)})")
		else:
			await db.execute(f"INSERT INTO {table} VALUES ({','.join(values)})", params)
		await db.commit()

async def dbexec(*sqls):
	for sql in sqls:
		if not isinstance(sql, tuple) and not isinstance(sql, str):
			raise TypeError("Sql must be type Union[tuple, str]")
	outputs = {}
	async with aiosqlite.connect('data.db') as db:
		for sql in sqls:
			if isinstance(sql, str):
				outputs[sql] = await db.execute(sql)
			else:
				outputs[sql[0]] = await db.execute(sql[0], sql[1])
		await db.commit()
	return outputs

async def getPrefix(bot, message):
	prefixes = ['<@755084857280954550> ', '<@!755084857280954550> ']
	defaults = ['<@755084857280954550> ', '<@!755084857280954550> ', 'u!', 'U!']
	if message.guild == None:
		return defaults
	async with aiosqlite.connect('data.db') as db:
		async with db.execute(f"SELECT * FROM prefixes WHERE guildid={message.guild.id}") as cursor:
			entries = await cursor.fetchall()
			if len(entries) < 1:
				return defaults
			else:
				if "u!" not in prefixes and message.author.id in bot.owner_ids:
					prefixes.append("u!")
				prefixes.append(entries[0][1])
				return prefixes

async def setPrefix(ctx, prefix):
	if ctx.guild == None:
		raise commands.NoPrivateMessage("You may not set a prefix in a DM.")
	gPrefix = await query("prefixes", f"guildid={ctx.guild.id}")
	if prefix == None:
		async with aiosqlite.connect('data.db') as db:
			await db.execute(f"DELETE FROM prefixes WHERE guildid={ctx.guild.id}")
			await db.commit()
	else:
		async with aiosqlite.connect('data.db') as db:
			if len(gPrefix) > 0:
				await db.execute(f"DELETE FROM prefixes WHERE guildid={ctx.guild.id}")
			await db.execute(f"INSERT INTO prefixes VALUES ({ctx.guild.id}, \"{prefix}\")")
			await db.commit()

bot = commands.Bot(command_prefix=getPrefix, case_insensitive=True, allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=False), intents=intents)

bot.setPrefix = setPrefix
bot.dbquery = query
bot.dbexec = dbexec
bot.dbinsert = dbinsert
bot.utils = dpytils.utils()
bot.const_emojis = {
	'no': '<:no:778489134741979186>',
	'yes': '<:yes:778489135870377994>',
	'paroot': '<a:paroot:778489137001922591>',
	'banhammer': '<:banhammer:778489141356658690>',
	'loading': '<a:loading:778489145524748298>',
	'online': '<:online:778489146703609896>',
	'idle': '<:idle:778489147420704789>',
	'offline': '<:offline:778489148750561292>',
	'dnd': '<:dnd:778489150148050996>',
	'bravery': '<:bravery:778489151288246273>',
	'briliance': '<:briliance:778489152228163604>',
	'balance': '<:balance:778489153405845544>',
	'hypesquad_events': '<:hypesquad_events:778489154585362442>',
	'bot_dev_badge': '<:bot_dev_badge:778489155977216050>',
	'early_supporter': '<:early_supporter:778489157055414272>',
	'discord_staff_badge': '<:discord_staff_badge:778489158221955103>',
	'bug_hunter_badge': '<:bug_hunter_badge:778489159551025162>',
	'golden_bug_hunter_badge': '<:golden_bug_hunter_badge:778489160080162826>',
	'bot_tag': '<:bot_tag:778489161027420170>',
	'verified_bot_tag': '<:verified_bot_tag:778489161627861013>',
	'new_partner_badge': '<:new_partner_badge:778489162847879179>',
	'category': '<:category:778489166316175413>',
	'text_channel': '<:text_channel:778489167649701898>',
	'voice_channel': '<:voice_channel:778489169000661002>',
	'locking_lock': '<a:locking_lock:778489170703548437>',
	'unlocking_lock': '<a:unlocking_lock:778489172833992704>',
	'nitro': '<:nitro:779954141262774293>',
	'2moboost': '<:2moboost:779966286426931202>',
	'24moboost': '<:24moboost:779966418006442004>',
	'3moboost': '<:3moboost:779966455407706132>',
	'15moboost': '<:15moboost:779966518352019466>',
	'6moboost': '<:6moboost:779966584298012683>',
	'18moboost': '<:18moboost:779966630016581653>',
	'9moboost': '<:9moboost:779966686614650959>',
	'12moboost': '<:12moboost:779966734177927209>',
	'1moboost': '<:1moboost:779966812321349653>'
}
			if ctx.guild and ctx.guild.id in nocommandblacklist:
				return
			await ctx.send(f'`{ctx.message.content}` is not a command, <@{ctx.author.id}>')
		elif isinstance(error, commands.CheckFailure):
			await ctx.send(error)
		elif isinstance(error, BlacklistedError):
			await ctx.send(error)
		elif isinstance(error, commands.DisabledCommand):
			await ctx.send(f'Sorry, but the command `{ctx.command.qualified_name}` is currently disabled.')
		elif isinstance(error, commands.MissingRequiredArgument):
			await ctx.send(str(error).capitalize())
		elif isinstance(error, commands.BadArgument) or isinstance(error, commands.BadUnionArgument):
			await ctx.send(f"There was an error parsing command arguments:\n`{error}`")
		elif "VoiceError: You are not connected to a voice channel." in str(error):
			pass
		elif longTextRegex != None:
			await ctx.send(f"Command response was too long to send. `{longTextRegex.group(1)}` must be {longTextRegex.group(2)} characters or less.")
		else:
			invitelink = f"https://discord.gg/"
			for invite in await bot.get_guild(755887706386726932).invites():
				if invite.temporary == True:
					pass
				else:
					invitelink = invitelink + invite.code
					break
			else:
				newinvite = await bot.get_channel(755910440533491773).create_invite(reason="Creating invite to the server for an error message.")
				invitelink = invitelink + newinvite.code
			tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
			tb = f"Command ran: {ctx.message.content}\nUser id:{ctx.author.id}\nGuild id:{ctx.guild.id}\n\n{tb}"
			embed = discord.Embed(title="Oh no!", description=f"An error occured.\nIf you are a normal user, you may try and contact the developers, they just got a log of the error.\nYou can join the support server [here]({invitelink})\nError message: \n`{str(error)}`", color=0xff1100)
			await ctx.send(embed=embed)
			m = await errorchannel.send(allowed_mentions=discord.AllowedMentions(everyone=False, roles=True, users=False),content=f"<@&766132653640122419>\n{ctx.author} tried to run the command `{ctx.command.qualified_name}`, but this error happened:\nHastebin: {str(bot.get_emoji(778489145524748298))}", embed=embed)
			try:
				url = await postbin.postAsync(content=tb, retry=0, find_fallback_on_retry_runout=True)
				await m.edit(allowed_mentions=discord.AllowedMentions(everyone=False, roles=True, users=False),content=f"<@&766132653640122419>\n{ctx.author} tried to run the command `{ctx.command.qualified_name}`, but this error happened:\nHastebin: <{url}>", embed=embed)
			except Exception as e:
				tb2 = "".join(traceback.format_exception(type(e), e, e.__traceback__))
				tb_wrap = [f"```py\n{line}```" for line in textwrap.wrap(tb, 1500)]
				await errorchannel.send(f"Loading a hastebin errored. Since that didn't work, here is the raw traceback in discord:")
				for message in tb_wrap:
					await errorchannel.send(message)
				tb2_wrap = [f"```py\n{line}```" for line in textwrap.wrap(tb2, 1500)]
				await errorchannel.send(f"Here is the error that happened when trying to post to hastebin:")
				for message in tb2_wrap:
					await errorchannel.send(message)
	except:
		await bot.get_channel(764333133738541056).send(content="<@&766132653640122419>\nIronic. The error handler errored.")

@bot.event
async def on_error(event, *args, **kwargs):
	errorInfo = sys.exc_info()
	tb = "".join(traceback.format_exception(errorInfo[0], errorInfo[1], errorInfo[2]))
	await bot.get_channel(764333133738541056).send(f"""
	{event} raised a {errorInfo[0].__name__}: ```py
	{tb}```
	""".replace("	", ""))

fReg = re.compile(r"(^|\A|\s)f($|\Z|\s)", flags=(re.IGNORECASE|re.MULTILINE))

@bot.event
async def on_message(message):
	if not message.guild:
		log = bot.get_channel(776466538156130314)
		e = discord.Embed(title="Bot DMed", description=f"""
		User: `{str(message.author)}` ({message.author.id})
		Content: `{await postbin.postAsync(message.content)}`
		""".replace("	", "")
		)
		await log.send(embed=e)
	if message.channel.id == 755982484444938290 and not message.content.startswith('=>'):
		await message.add_reaction(bot.get_emoji(778489135870377994))
		await message.add_reaction(bot.get_emoji(778489134741979186))
	if message.author.id == 764868481371602975 and message.content == "online please leave me alone":
		await message.channel.send("no")
	if fReg.search(message.content):
		db = await bot.dbquery("pressf", "enabled", f"channelid={message.channel.id}")
		if db:
			await message.channel.send(f"{message.author.mention} has paid their respects.")
	if message.webhook_id != None and message.mention_everyone:
		webhook_guilds = [693225390130331661, 755887706386726932]
		if message.guild.id in webhook_guilds:
			for w in message.channel.webhooks:
				try: 
					await w.delete()
					await message.channel.send("Detected webhook everyone ping, removed webhook.")
				except: 
					await bot.get_channel(776466538156130314).send(f"couldn't remove webhook in {message.channel.mention}.")
	if message.content == f"<@{bot.user.id}>" or message.content == f"<@!{bot.user.id}>":
		ps = await getPrefix(bot, message)
		ps_formatted = [f"`{x}`" for x in ps]
		ps_formatted.remove(f"`<@{bot.user.id}> `")
		ps_formatted.remove(f"`<@!{bot.user.id}> `")
		ps_formatted = str(ps_formatted).replace("[", "").replace("]", "").replace("'", "")
		embed = discord.Embed(title=f"Prefixes for the server \"{message.guild.name}\":", description=ps_formatted).set_footer(text="Note: if you ping the bot with a space after the ping but before the command, it will always work as a prefix. For example: \"@Utilibot ping\"")
		await message.channel.send(embed=embed)
	if message.content == "utilibot prefix?" and message.guild:
		ps = await getPrefix(bot, message)
		ps_formatted = [f"`{x}`" for x in ps]
		ps_formatted.remove(f"`<@{bot.user.id}> `")
		ps_formatted.remove(f"`<@!{bot.user.id}> `")
		ps_formatted = str(ps_formatted).replace("[", "").replace("]", "").replace("'", "")
		embed = discord.Embed(title=f"Prefixes for the server \"{message.guild.name}\":", description=ps_formatted).set_footer(text="Note: if you ping the bot with a space after the ping but before the command, it will always work as a prefix. For example: \"@Utilibot ping\"")
		await message.channel.send(embed=embed)
	elif message.content == "utilibot prefix?" and not message.guild:
		await message.channel.send("As this is a dm channel, there is no prefix. Just say the name of the command and it will run. For example, `ping`.")
	else:
		await bot.process_commands(message)

@bot.event
async def on_guild_join(guild):
	print("Joined server")
	perms = [x for x,y in dict(guild.me.guild_permissions).items() if not y]
	denied = []
	if "send_messages" in perms:
		denied.append("send_messages")
	if "read_messages" in perms:
		denied.append("read_messages")
	if "embed_links" in perms:
		denied.append("embed_links")
	if denied != []:
		await guild.owner.send(f"You or someone else has added me to your server, but it appears I do not have the following needed permissions:\n{', '.join(denied)}\n\nIf this is intentional, just ignore this message.")
"""
@bot.event
async def on_voice_state_update(member, before, after):
	channel = bot.get_channel(before.channel.id)
	if member.guild.me.voice.channel == before.channel and before.channel is not None and after.channel is None:
		if channel.members == [bot.user.id]:
			vc = member.guild.voice_client
			await vc.disconnect()
			vc.cleanup()
"""

def errlog(message):
	asyncio.create_task(bot.get_channel(764333133738541056).send(message))

bot.load_extension("jishaku")
for file in sorted(glob.glob("cogs/*.py")):
	file = file.replace(".py", "").replace("/", ".")
	try:
		bot.load_extension(file)
	except Exception as error:
		print(f"\033[1mCog {file} failed to load.\n{error}\033[0m")
		tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
		errlog(f"Cog {file} failed to load.```py\n{tb}```")
# bot.load_extension("riftgun")

disabled_commands = ['mute']

for cmd in disabled_commands:
	try: bot.get_command(cmd).update(enabled=False)
	except: pass

bot.run(os.getenv("BOT_TOKEN"))
