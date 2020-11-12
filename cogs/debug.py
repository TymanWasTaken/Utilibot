import discord, sys, os, json, aiofiles
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
		User: `{str(ctx.author)}`
		Guild: `{ctx.guild.name}`
		Command: `{ctx.command.qualified_name}`
		""".replace("	", "")
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

def setup(bot):
	cog = Debug(bot)
	bot.add_cog(cog)
	print('[DebugCog] Debug cog loaded')
