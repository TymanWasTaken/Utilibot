import discord, random, datetime, asyncio, postbin, traceback
from discord.ext import commands
import concurrent.futures

async def Average(bot, lst): 
    with concurrent.futures.ProcessPoolExecutor() as pool:
        result = await bot.loop.run_in_executor(
            pool, lambda lst: sum(lst) / len(lst), lst)
		

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

def setup(bot):
	bot.add_cog(Guilds(bot))
	print('[Guilds] Guilds cog loaded')