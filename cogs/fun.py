import discord, random, typing, json
from discord.ext import commands

class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def fcheck(self, channel):
		db = await self.bot.dbquery("pressf", "channelid=" + str(channel.id))
		if len(db) < 1:
			return None
		data = json.loads(db[0][1])
		return data

	@commands.command()
	async def hello(self, ctx):
		"""
		:)
		"""
		await ctx.send("Hello there.")

	@commands.command()
	async def say(self, ctx, *, message: commands.clean_content(fix_channel_mentions=True)):
		"""
		Says what you tell it to, self-explanatory.
		"""
		await ctx.message.delete()
		await ctx.send(message)

	@commands.command()
	async def paroot(self, ctx):
		await ctx.send(self.bot.get_emoji(778489137001922591))

	@commands.command()
	async def choose(self, ctx, *, choices: str):
		if not "|" in choices:
			return await ctx.send("Please separate the choices with a |.")
		choices = choices.split("|")
		await ctx.send(random.choice(choices))
		
	@commands.command(name="randomnumber", aliases=['pick','rannum'])
	@commands.bot_has_permissions(embed_links=True, send_messages=True)
	async def randomnumber(self, ctx, maxnumber: int):
		numb = random.randint(0, maxnumber)
		await ctx.send(embed=discord.Embed(title="Random Number Picked", description=str(numb), color=0x7289da))

	@commands.command(hidden=True)
	async def dogs(self, ctx):
		await ctx.send("https://media.discordapp.net/attachments/499750909190864918/776309869946208266/unknown.png")

	@commands.command(name="pressf", aliases=['enablepressf', 'pressfenable', 'pf'])
	@commands.has_permissions(manage_messages=True)
	async def pressf(self, ctx, channel: typing.Optional[discord.TextChannel]):
		"""
		Toggle to enable/disable the `Press F` autoresponse in a channel. Defaults to current channel.
		"""
		ch = channel or ctx.channel
		action = "Enabled"
		if await self.fcheck(ch) == True:
			await self.bot.dbexec(f"DELETE FROM pressf WHERE channelid={ctx.channel.id}")
			action = "Disabled"
		elif await self.fcheck(ch) == None: 
			await self.bot.dbexec(("INSERT INTO pressf VALUES (?, ?)", (ch.id, "true")))
		await ctx.send(f"{action} `Press F` autoresponse!")
		#await ctx.send("doesn't do anything until clari figures out sql :joy: press f to pay respects autoresponse will be always disabled for the time being.")

def setup(bot):
	bot.add_cog(Fun(bot))
	print('[FunCog] Fun cog loaded')
