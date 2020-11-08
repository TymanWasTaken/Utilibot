import discord, random, asyncio, string, aiofiles, json
from discord.ext import commands
import datetime
import importlib

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

class Config(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	async def setprefix(self, ctx, *, prefix=None):
		if prefix == None:
			d = await readDB()
			if not str(ctx.guild.id) in d["prefixes"]:
				return await ctx.send("I can't remove the custom prefix because it doesn't exist!")
			del d["prefixes"][str(ctx.guild.id)]
			await writeDB(d)
			await ctx.send("Reset the prefix for this server!")
		else:
			d = await readDB()
			d["prefixes"][str(ctx.guild.id)] = prefix
			await writeDB(d)
			await ctx.send(f"Changed the prefix to `{prefix}` for this server!")

def setup(bot):
	bot.add_cog(Config(bot))
	print('[ConfigCog] Config cog loaded')
