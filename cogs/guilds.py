import discord, random, datetime, asyncio, postbin, traceback, re
from discord.ext import commands
import concurrent.futures

def func(lst):
	return sum(lst) / len(lst)

async def Average(bot, l):
	with concurrent.futures.ProcessPoolExecutor() as pool:
		return await bot.loop.run_in_executor(pool, func, l)

def func2(num):
	return round(num, 2)

async def Round(bot, num):
	with concurrent.futures.ProcessPoolExecutor() as pool:
		return await bot.loop.run_in_executor(pool, func2, num)

class Guilds(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(invoke_without_command=True)
	@commands.is_owner()
	async def guilds(self, ctx):
		guilds = len(self.bot.guilds)
		users = len(self.bot.users)
		avg = await Average(self.bot, [g.member_count for g in self.bot.guilds])
		await ctx.send(embed=discord.Embed(title="Guild data", description=f"""
		Guild count: {guilds}
		Total user count: {users}
		Average member count: {avg}
		""".replace("	", "")
		))

	@guilds.command()
	@commands.is_owner()
	async def leave(self, ctx, guild: discord.Guild):
		async with ctx.typing():
			try:
				await guild.leave()
				await ctx.send(f"Successfuly left guild \"{guild.name}\".")
			except Exception as error:
				tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
				url = await postbin.postAsync(tb)
				await ctx.send(f"An error occured while trying to leave that guild. Hastebin: {url}")

	@guilds.command()
	@commands.is_owner()
	async def botfarms(self, ctx):
		message = await ctx.send("Calculating...")
		text = ""
		e = discord.Embed(title="Bot farms detected:")
		for g in self.bot.guilds:
			await g.chunk()
			bots = []
			for m in g.members:
				if m.bot:
					bots.append(m.id)
			btm = (len(bots)/g.member_count)*100
			btmround = await Round(self.bot, btm)
			if btm >= 75 and g.member_count > 20:
				e.add_field(name=g.name+":", value=f"- Bot %: `{btmround}%`\n- Bots/membercount: `{len(bots)}/{g.member_count}`\n- Guild ID: `{g.id}`\n\n")
		await message.edit(content="", embed=e)


def setup(bot):
	bot.add_cog(Guilds(bot))
	print('[Guilds] Guilds cog loaded')