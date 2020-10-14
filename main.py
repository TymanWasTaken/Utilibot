# Imports
import discord, os, time, glob, postbin, traceback, cogs, importlib
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv
music = importlib.import_module("cogs.music")
load_dotenv(verbose=True)
intents = discord.Intents()
intents.value = 32511
bot = commands.Bot(command_prefix=commands.when_mentioned_or('u!'), case_insensitive=True, allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=False), intents=intents)

@bot.check
async def globally_block_dms(ctx):
	if ctx.guild is not None:
		return True
	else:
		await ctx.send("DM's are disabled, please use an actual server.")
		return False

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
		await ctx.send('Nice try but you are not the owner.')
		await errorchannel.send(f"{ctx.author} tried to run `{ctx.command.qualified_name}`, but they are not owner.")
	elif isinstance(error, commands.CommandNotFound):
		if ctx.guild.id in nocommandblacklist:
			return
		await ctx.send(f'Not a command, <@{ctx.author.id}>')
	elif isinstance(error, commands.CheckFailure):
		await ctx.send(error)
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(str(error).capitalize())
	elif isinstance(error, commands.BadArgument):
		await ctx.send(f"There was an error parsing command arguments:\n`{error}`")
	elif isinstance(error, music.VoiceError):
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
		tb = f"Command ran: {ctx.message.content}\n\n{tb}"
		try:
			url = await postbin.postAsync(content=tb, retry=1)
		embed = discord.Embed(title="Oh no!", description=f"An error occured.\nIf you are a normal user, you may try and contact the developers, they just got a log of the error.\nYou can join the support server [here]({invitelink})\nError message: \n`{str(error)}`", color=0xff1100)
		await ctx.send(embed=embed)
		await errorchannel.send(content=f"{ctx.author} tried to run the command `{ctx.command.qualified_name}`, but this error happened:\nHastebin: <{url}>", embed=embed)

@bot.event
async def on_message(message):
	if message.channel.id == 755982484444938290:
		for emoji in message.guild.emojis:
			if emoji.id == 755947356834365490:
				yes = emoji
			elif emoji.id == 755947345212080160:
				no = emoji
		await message.add_reaction(yes)
		await message.add_reaction(no)

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
		await guild.owner.send(f"You or someone else has added me to your server, but it appears I do not have the following needed permissions:\n{', '.join(denied)}")
"""
@bot.event
async def on_voice_state_update(member, before, after):
	channel = bot.get_channel(before.voice.voice_channel.id)
	if member.guild.me.voice.channel == before.channel and before.voice.voice_channel is not None and after.voice.voice_channel is None:
		if channel.members == [bot.user.id]:
			vc = member.guild.voice_client
			await vc.disconnect()
			vc.cleanup()
"""
bot.load_extension("jishaku")
# bot.load_extension("riftgun")
# bot.load_extension("guildmanager")
# This loads all cogs in the directory, so I don't have to manually add cogs when I make/change them
os.chdir("cogs")
for file in glob.glob("*.py"):
	file = file.replace(".py", "")
	bot.load_extension(f"cogs.{file}")
bot.run(os.getenv("BOT_TOKEN"))
