import discord, random, typing, json, string
from discord.ext import commands

class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

#	@commands.command()
#	async def hello(self, ctx):
#		"""
#		:)
#		"""
#		await ctx.send("Hello there.")

	@commands.command()
	@commands.is_owner()
	@commands.guild_only()
	async def say(self, ctx, reference: typing.Optional[discord.Message], *, message):
		"""
		Says what you tell it to, self-explanatory.
		"""
		try: await ctx.message.delete()
		except: pass
		await ctx.send(message, reference=reference)

	@commands.command(name="emojispeak", aliases=['el', 'emojiletter'])
	async def emojispeak(ctx, *, message):
		"""
		Turns a message into emojis
		"""
		message = message.lower().replace()
		newmessage = ""
		for char in message:
			if char not in string.ascii_lowercase:
				newmessage += char
			else:
				newmessage += f":regional_indicator_{char}:"
		if len(newmessage) + len(ctx.author) <= 2000:
			newmessage += f"\n{ctx.author}"
		await ctx.send(newmessage)
		await ctx.message.delete()

	@commands.command(name="quote")
	@commands.guild_only()
	async def quote(self, ctx, message: discord.Message, *, response):
		"""
		Quotes a message.
		"""
		if not message.channel == ctx.channel: return
		quoted = str(message.content).replace("\n", "\n> ")
		await ctx.message.delete()
		w = await ctx.channel.create_webhook(name=ctx.author.name)
		await w.send(f"> {quoted}\n{message.author.mention} {response}", avatar_url=ctx.author.avatar_url)
		await w.delete()


	@commands.command()
	@commands.is_owner()
	async def webhook(self, ctx, name, *, text):
		await ctx.message.delete()
		w = await ctx.channel.create_webhook(name=name)
		await w.send(text)
		await w.delete()

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
		db = await self.bot.dbquery("pressf", "enabled", "channelid=" + str(ch.id))
		if db:
			action = "Disabled"
			await self.bot.dbexec((f"DELETE FROM pressf WHERE channelid={ch.id}"))
		else:
			await self.bot.dbexec((f"DELETE FROM pressf WHERE channelid={ch.id}"))
			await self.bot.dbexec(("INSERT INTO pressf VALUES (?, ?)", (ch.id, "true")))
		await ctx.send(f"{action} `Press F` autoresponse for <#{ch.id}>!")

	@commands.command(name="turkeyday", aliases=['thanksgiving', 'turkey'])
	async def turkeyday(self, ctx):
			embed=discord.Embed(title=":turkey: Happy Turkey Day! :turkey:", description="To those of you in the United States, we wish you a happy Thanksgiving. What are you going to give thanks for today? We want to tell you: Thank *you* for choosing Utilibot! Have a great day!\n\n||This message appeared for one day on Novemeber 26th, 2020.||", color=0xcb611d)
			embed.set_author(name="Special Thanksgiving Day message from the Utilibot Development Team")
			embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
			await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(Fun(bot))
	print('[FunCog] Fun cog loaded')
