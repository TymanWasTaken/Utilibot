# Imports
import discord, os, time, glob, postbin, traceback, asyncio, cogs, importlib, aiofiles, json, textwrap, re, sys, aiosqlite, dpytils, aiohttp
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv
from io import BytesIO
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

bot = commands.Bot(command_prefix=getPrefix, case_insensitive=True, allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=False, replied_user=False), intents=intents)

bot.setPrefix = setPrefix
bot.dbquery = query
bot.dbexec = dbexec
bot.dbinsert = dbinsert
bot.utils = dpytils.utils()

class BlacklistedError(commands.CommandError):
	pass

async def is_blacklisted(id: int):
	# Check if user is owner, if so ignore everthing
	if id in bot.owner_ids:
		return False
	data = await readDB()
	if id in data["banned_users"]:
			return True
	else:
			return False

@bot.check
async def blacklist_users(ctx):
	if await is_blacklisted(ctx.author.id) == True:
		raise BlacklistedError("I'm sorry, but you have been blacklisted from using this bot.")
	else:
		return True

@bot.event
async def on_ready():
	bot.const_emojis = {}
	for e in bot.get_guild(778487633205788712).emojis:
		bot.const_emojis[e.name] = str(e)
	print(f'Bot logged in as {bot.user}')
	await bot.get_channel(755979601788010527).send(content=datetime.now().strftime("[%m/%d/%Y %I:%M:%S] ") + "Bot online")
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Clari's screams of frustration"))

@bot.event
async def on_command_error(ctx, error):
	try:
		nocommandblacklist = [264445053596991498, 458341246453415947, 735615909884067930]
		errorchannel = bot.get_channel(764333133738541056)
		longTextRegex = re.match(r"Command raised an exception: HTTPException: 400 Bad Request \(error code: 50035\): Invalid Form Body\nIn (.+): Must be (\d+) or fewer in length.", str(error))
		if isinstance(error, commands.TooManyArguments):
			await ctx.reply('Too many arguments')
		elif isinstance(error, commands.NotOwner):
			await ctx.reply('Nice try, but you are not one of the developers.')
			await errorchannel.send(f"{ctx.author} tried to run `{ctx.command.qualified_name}`, but they are not owner.")
		elif isinstance(error, commands.CommandNotFound):
			if ctx.guild and ctx.guild.id in nocommandblacklist:
				return
			await ctx.send(f'`{ctx.message.content}` is not a command, <@{ctx.author.id}>')
		elif isinstance(error, commands.CheckFailure):
			await ctx.reply(error)
		elif isinstance(error, BlacklistedError):
			await ctx.reply(error)
		elif isinstance(error, commands.DisabledCommand):
			await ctx.reply(f'Sorry, but the command `{ctx.command.qualified_name}` is currently disabled.')
		elif isinstance(error, commands.MissingRequiredArgument):
			await ctx.reply(str(error).capitalize())
		elif isinstance(error, commands.BadArgument) or isinstance(error, commands.BadUnionArgument):
			await ctx.reply(f"There was an error parsing command arguments:\n`{error}`")
		elif "VoiceError: You are not connected to a voice channel." in str(error):
			pass
		elif longTextRegex != None:
			await ctx.reply(f"Command response was too long to send. `{longTextRegex.group(1)}` must be {longTextRegex.group(2)} characters or less.")
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
	except Exception as error:
		await bot.get_channel(764333133738541056).send(content=f"<@&766132653640122419>\nIronic. The error handler errored.```py\n{''.join(traceback.format_exception(type(error), error, error.__traceback__))}```")

@bot.event
async def on_error(event, *args, **kwargs):
	errorInfo = sys.exc_info()
	tb = "".join(traceback.format_exception(errorInfo[0], errorInfo[1], errorInfo[2]))
	await bot.get_channel(764333133738541056).send(f"""
	{event} raised a {errorInfo[0].__name__}: ```py
	{tb}```
	""".replace("	", ""))

fReg = re.compile(r"(^|\A|\s)f($|\Z|\s)", flags=(re.IGNORECASE|re.MULTILINE))
afkReg = re.compile(r"<@!?(\d+)>", flags=(re.MULTILINE))

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
		if not message.author.bot:
			db = await bot.dbquery("pressf", "enabled", f"channelid={message.channel.id}")
			if db:
				async with aiohttp.ClientSession() as s:
					async with s.get("https://i.imgur.com/q3h9bED.png") as r:
						await message.reply(f"{message.author.mention} has paid their respects.", file=discord.File(BytesIO(await r.content.read()), filename="press_f.png"))
	afksearch=afkReg.search(message.content)
	if afksearch:
		try: user = message.guild.get_member(int(afksearch.group(1)))
		except: user = None
		if user and not message.author.bot:
			localafk = await bot.dbquery("afk", "data", f"guildid={message.guild.id}")
			globalafk = await bot.dbquery("globalafk", "message", f"userid={user.id}")
			localmsg = ""
			globalmsg = ""
			if localafk:
				localdata = json.loads((localafk[0][0]).replace("'", '"'))
				try:
					localmsg = localdata[str(user.id)]
				except:
					pass
			if globalafk:
				globalmsg = globalafk[0][0]
			if globalmsg or localmsg:
				embed = discord.Embed(description=globalmsg, color=bot.utils.randcolor())
				inguild = ""
				scope = "Global"
				if localmsg:
					embed.description=localmsg
					inguild = f" in {message.guild}"
					scope = "Local"
				embed.set_author(name=f"{user.nick if user.nick else user.name}#{user.discriminator} is currently AFK{inguild}.", icon_url=user.avatar_url)
				embed.set_footer(text=f"Scope: {scope} AFK Message")
				await message.channel.send(embed=embed, delete_after=10)
	if message.guild.id == 728107941126864927 and "wholesome" or "beth" in message.content: await message.channel.send("BETH IS WHOLESOME")
	if message.channel.type == discord.ChannelType.news:
		autopubdb = await bot.dbquery("autopublish_channels", "data", "guildid=" + str(message.guild.id))
		try: chans = json.loads(autopubdb[0][0])
		except: chans = []
		chans
		if message.channel.id in chans and not message.author.bot:
			try:
				await message.publish()
				await message.add_reaction("📣")
				await asyncio.sleep(3)
				await message.remove_reaction("📣", message.guild.me)
			except:
				await message.author.send(f"Failed to publish {message.jump_url}.")
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

#@bot.event
#async def on_command(ctx):
#	if not ctx.author.bot:
#		table = turkeyday
#		db = (await bot.dbquery(table, "notfirst", "userid=" + str(ctx.author.id)))
#		if not db:
#			embed=discord.Embed(title=":turkey: Happy Turkey Day! :turkey:", description="To those of you in the United States, we wish you a happy Thanksgiving. What are you going to give thanks for today? We want to tell you: Thank *you* for choosing Utilibot! Have a great day!\n\n||This message will disappear at 12 AM (CST). You can type `u!turkey` to see it again.||", color=0xcb611d)
#			embed.set_author(name="Special Thanksgiving Day message from the Utilibot Development Team")
#			embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
#			await bot.dbexec(f"INSERT INTO {table} VALUES ({str(ctx.author.id)}, 'true')")
#			await ctx.send(embed=embed)
#			await bot.get_channel(781596395739152414).send(content=f"{ctx.author} received their turkey day message in **{ctx.guild.name}** ({ctx.channel.mention}).")


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
		BOLD = "\033[1m"
		RED = "\033[0;31m"
		print(f"{RED}{BOLD}Cog {file} failed to load.\n{error}\033[0m")
		tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
		# errlog(f"Cog {file} failed to load.```py\n{tb}```")
# bot.load_extension("riftgun")

disabled_commands = ['mute']

for cmd in disabled_commands:
	try: bot.get_command(cmd).update(enabled=False)
	except: pass
def run_api(bot):
	from uvicorn import Server, Config
	web_cog = bot.get_cog("web")
	if web_cog is None:
		return
	server = Server(Config(web_cog.app, host="0.0.0.0", port=1234))
	server.config.setup_event_loop()
	return bot.loop.create_task(server.serve())
try:
	run_api(bot)
	bot.run(os.getenv("BOT_TOKEN"))
except KeyboardInterrupt:
	exit()
