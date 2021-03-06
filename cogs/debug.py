import discord, sys, os, json, aiofiles, typing
from discord.ext import commands
from jishaku import models

class ManualError(Exception):
	pass

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
		print(f"An error occurred, {e}")

class Debug(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command(self, ctx):
		log = self.bot.get_channel(776466538156130314)
		e = discord.Embed(title="Command ran", description=f"""
		User: `{str(ctx.author)}` ({ctx.author.id})
		Guild: `{ctx.guild.name + f" ({ctx.guild.id})" if ctx.guild else 'None'}`
		Channel: `{ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else "DM"}` ({ctx.channel.id})
		Message: `{ctx.message.id}`
		Command: `{ctx.command.qualified_name}`
		""".replace("	", ""), color=0x2F3138
		)
		await log.send(embed=e)

	@commands.command()
	@commands.is_owner()
	async def quit(self, ctx):
		"""
		Kill the bot.
		"""
		await ctx.send('Shutting down...')
		print('Received quit command, shutting down.')
		sys.exit()

	@commands.command()
	@commands.is_owner()
	async def restart(self, ctx):
		"""
		Uses pm2 to restart the bot. Will not work if the bot is not hosted with pm2.
		"""
		await ctx.send("soon:tm:")
		await ctx.send("maybe restarting?")
		print('Received restart command, rebooting.')
		sys.Restart()

	@commands.command()
	@commands.is_owner()
	async def wipedb(self, ctx, table: str, key: str):
#		try:
		db = await self.bot.dbquery(table)
#		except:
#			return await ctx.send(f"The table `{table}` doesn't exist.")
		m = await ctx.send(f"Wiping `{table}`...")
		for i in db:
			await self.bot.dbexec(f"DELETE FROM {table} WHERE {key}={i[0]}")
		await m.edit(content=f"{self.bot.const_emojis['yes']}Wiped the `{table}` table.")
		
	@commands.group(invoke_without_command=True)
	@commands.is_owner()
	async def dbinfo(self, ctx):
		"""
		Gives tables, and their data structure.
		"""
		embed = discord.Embed(title="Tables")
		dbs = await self.bot.dbquery("sqlite_master", "name", "type=\"table\"")
		for dbname in dbs:
			dbname = dbname[0]
			dbinfo = await self.bot.dbquery(f"pragma_table_info('{dbname}')")
			embed.add_field(name=dbname, value="\n".join([f"Column {i[0]}: {i[1]} {i[2]}" for i in dbinfo]))
		await ctx.send(embed=embed)

	@dbinfo.command()
	@commands.is_owner()
	async def query(self, ctx, table, search=None):
		tables = [tb[0] for tb in await self.bot.dbquery("sqlite_master", "name", "type=\"table\"")]
		if table not in tables:
			return await ctx.send("Not a valid table.")
		tableinfo = await self.bot.dbquery(f"pragma_table_info('{table}')")
		result = await self.bot.dbquery(table=table, condition=search)
		embed = discord.Embed(title="Query results")
		for i, res in enumerate(result):
			nice = []
			for ii, r in enumerate(res):
				nice.append(f"{tableinfo[ii][1]}: {r}")
			embed.add_field(name=f"Result {i+1}", value="\n".join(nice))
		await ctx.send(embed=embed)

	@commands.command()
	@commands.is_owner()
	async def git(self, ctx, *, message=""):
		"""
		Upload code to github.
		"""
		m = await ctx.send("Updating repo...")
		code = os.system(f'../git.sh {message}')
		await m.edit(content=f'Updated repo successfully, with return code {code}!')

	@commands.command(name="su")
	@commands.is_owner()
	async def bypass_all(self, ctx: commands.Context, *, command_string: str):
		"""
		Runs a command bypassing all checks, basically forcing the command to run.
		"""

		alt_ctx = await models.copy_context_with(ctx, content=ctx.prefix + command_string)

		if alt_ctx.command is None:
			return await ctx.send(f'Command "{alt_ctx.invoked_with}" is not found')

		return await alt_ctx.command.reinvoke(alt_ctx)

	@commands.command()
	@commands.is_owner()
	async def error(self, ctx, silence="no"):
		if silence.lower() in ['true', 'y', 'yes']:
			raise ManualError("Error caused by command, probably for debugging purposes​​​​​​​​​​")
		else:
			raise ManualError("Error caused by command, probably for debugging purposes")

	@commands.command()
	@commands.is_owner()
	async def botstatus(self, ctx, online: typing.Optional[discord.Status], activity: typing.Optional[discord.ActivityType], *, newstatus=None):
		online = online or ctx.guild.me.status
		activity = activity or (ctx.guild.me.activity.type if ctx.guild.me.activity else None) or discord.ActivityType.listening
		newstatus = str(newstatus)
		setactivity = discord.Activity(type=activity, name=newstatus) if newstatus != 'None' else None
		await self.bot.change_presence(status=(online), activity=setactivity)
		await ctx.send(f"Changed my status to ```{newstatus}``` and set my indicator to {self.bot.const_emojis[str(online)]} `{str(online).capitalize()}`")

	@commands.command()
	@commands.is_owner()
	async def blacklist(self, ctx, id: int):
		data = ""
		async with aiofiles.open("/home/tyman/code/utilibot/data.json", mode="r") as f_read:
			data = json.loads(await f_read.read())
			try:
				user = await self.bot.fetch_user(id)
			except:
				user = None
			if user is None:
				return await ctx.send("User does not exist.")
			elif id in data["banned_users"]:
				return await ctx.send("User is already blacklisted.")
			else:
				async with aiofiles.open("/home/tyman/code/utilibot/data.json", mode="w") as f_write:
					data["banned_users"].append(id)
					await f_write.write(json.dumps(data))
					await ctx.send(f"Successfully blacklisted {str(user)}.")
	
	@commands.command()
	@commands.is_owner()
	async def unblacklist(self, ctx, id: int):
		data = ""
		async with aiofiles.open("/home/tyman/code/utilibot/data.json", mode="r") as f_read:
			data = json.loads(await f_read.read())
			user = await self.bot.fetch_user(id)
			if user is None:
				return await ctx.send("User does not exist.")
			elif not id in data["banned_users"]:
				return await ctx.send("User is not blacklisted.")
			else:
				async with aiofiles.open("/home/tyman/code/utilibot/data.json", mode="w") as f_write:
					data["banned_users"].remove(id)
					await f_write.write(json.dumps(data))
					await ctx.send(f"Successfully unblacklisted {str(user)}.")
	
	@commands.command()
	@commands.is_owner()
	async def react(self, ctx, message: discord.Message, reaction, channel: discord.TextChannel=None):
		"""
		Reacts to a message with the given reaction.
		"""
		chan = channel or ctx.channel
#		try: msg = await chan.fetch_message(message)
#		except: return await ctx.send(f"`{message}` is not a valid message ID! (Either the message is not in the current/specified channel or it doesn't exist)")
		try: await msg.add_reaction(str(reaction))
		except: return await ctx.send(f"'{reaction}' is not a valid reaction!")
	@commands.command()
	@commands.is_owner()
	async def dm(self, ctx, user: discord.User, silent: typing.Union[bool, None], *, message):
		"""
		DMs the specified user.
		"""
		if user.bot: return await ctx.send("You can't DM a bot with another bot!")
		try:
			await user.send(f"{message}\n{f'-{ctx.author}' if not silent else ''}")
			await ctx.reply(f"Successfully DMed {user}!")
		except Exception as e:
			await ctx.send(f"Failed to DM {user}! Error:\n{e}")


def setup(bot):
	cog = Debug(bot)
	bot.add_cog(cog)
	print('[DebugCog] Debug cog loaded')
