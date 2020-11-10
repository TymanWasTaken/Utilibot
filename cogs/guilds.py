import discord, random, datetime, asyncio, postbin, traceback
from discord.ext import commands

class Guilds(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(invoke_without_command=True)
	@commands.is_owner()
	async def guilds(self, ctx):
		await ctx.send("Soon:tm:")

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