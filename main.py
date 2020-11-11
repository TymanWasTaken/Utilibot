# Imports
import discord, os, time, glob, postbin, traceback, cogs, importlib, aiofiles, json, textwrap
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

bot = commands.Bot(command_prefix=getprefixes, case_insensitive=True, allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=False), intents=intents)

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
	print(f'Bot logged in as {bot.user}')
	await bot.get_channel(755979601788010527).send(content=datetime.now().strftime("[%m/%d/%Y %I:%M:%S] ") + "Bot online")

@bot.event
async def on_command_error(ctx, error):
	nocommandblacklist = [264445053596991498, 458341246453415947, 735615909884067930]
	errorchannel = bot.get_channel(764333133738541056)
	if isinstance(error, commands.TooManyArguments):
		await ctx.send('Too many arguments')
	elif isinstance(error, commands.NotOwner):
		await ctx.send('Nice try, but you are not one of the developers.')
		await errorchannel.send(f"{ctx.author} tried to run `{ctx.command.qualified_name}`, but they are not owner.")
	elif isinstance(error, commands.CommandNotFound):
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
	elif isinstance(error, commands.BadArgument):
		await ctx.send(f"There was an error parsing command arguments:\n`{error}`")
	elif "VoiceError: You are not connected to a voice channel." in str(error):
		pass
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
		tb = f"Command ran: {ctx.message.content}\nUser id:{ctx.author.id}\bGuild id:{ctx.guild.id}\n\n{tb}"
		embed = discord.Embed(title="Oh no!", description=f"An error occured.\nIf you are a normal user, you may try and contact the developers, they just got a log of the error.\nYou can join the support server [here]({invitelink})\nError message: \n`{str(error)}`", color=0xff1100)
		await ctx.send(embed=embed)
		m = await errorchannel.send(allowed_mentions=discord.AllowedMentions(everyone=False, roles=True, users=False),content=f"<@&766132653640122419>\n{ctx.author} tried to run the command `{ctx.command.qualified_name}`, but this error happened:\nHastebin: {str(bot.get_emoji(769398108064710717))}", embed=embed)
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
@bot.event
async def on_message(message):
	if message.channel.id == 755982484444938290 and not message.content.startswith('=>'):
		for emoji in message.guild.emojis:
			if emoji.id == 755947356834365490:
				yes = emoji
			elif emoji.id == 755947345212080160:
				no = emoji
		await message.add_reaction(yes)
		await message.add_reaction(no)
	if message.author.id == 764868481371602975 and message.content == "online please leave me alone":
		await message.channel.send("no")
	if message.content == "utilibot prefix?" and message.guild:
		ps = await getprefixes(bot, message)
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
bot.load_extension("jishaku")
os.chdir("cogs")
for file in sorted(glob.glob("*.py")):
	file = file.replace(".py", "")
	try:
		bot.load_extension(f"cogs.{file}")
	except:
		pass
bot.load_extension("riftgun")
bot.run(os.getenv("BOT_TOKEN"))
