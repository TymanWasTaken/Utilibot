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
		Says what you tell it to, self-explanitory (pings won't actually ping)
		"""
		# await ctx.message.delete()
		await ctx.send(f"{str(ctx.author)} says:\n{message}", allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))

	@commands.command()
	async def paroot(self, ctx):
		await ctx.send(self.bot.get_emoji(755947816165048431))

	@commands.command()
	async def choose(self, ctx, *, choices: str):
		if not "|" in choices:
			return await ctx.send("Please seperate the choices with a |.")
		choices = choices.split("|")
		await ctx.send(random.choice(choices))
		
	@commands.command(name="randomnumber", aliases=['pick','rannum'])
	@commands.bot_has_permissions(embed_links=True, send_messages=True)
	async def randomnumber(self, ctx, maxnumber: int):
		numb = random.randint(0, maxnumber)
		await ctx.send(embed=discord.Embed(title="Random Number Picked", description=numb, color=0x7289da))

def setup(bot):
	bot.add_cog(Fun(bot))
	print('[FunCog] Fun cog loaded')
