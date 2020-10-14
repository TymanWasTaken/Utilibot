import discord, random
from discord.ext import commands

class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def hello(self, ctx):
		"""
		:)
		"""
		await ctx.send("Hello there.")

	@commands.command()
	async def say(self, ctx, *, message):
		"""
		Says what you tell it to, self-explanitory
		"""
		await ctx.message.delete()
		await ctx.send(message)

	@commands.command()
	async def paroot(self, ctx):
		await ctx.send("<a:paroot:755947816165048431>")

	@commands.command()
	async def choose(self, ctx, *, choices: str):
		if not "|" in choices:
			return await ctx.send("Please seperate the choices with a |.")
		choices = choices.split("|")
		await ctx.send(random.choice(choices))

def setup(bot):
	bot.add_cog(Fun(bot))
	print('[FunCog] Fun cog loaded')