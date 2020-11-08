import discord, random, re, aiohttp
from discord.ext import commands
from discord.ext.commands import MemberConverter
nomention = discord.AllowedMentions(everyone=False, roles=False, users=False)
async def runcode(code, ctx):
	lines = code.split("\n")
	member = ctx.guild.get_member(ctx.author.id)
	variables = {
		"$message.content": str(ctx.message.content),
		"$message.id": str(ctx.message.id),
		"$author.tag": str(ctx.author),
		"$author.id": str(ctx.author.id),
		"$author.nick": str(member.nick or member.name),
		"$author.name": str(member.name)
	}
	for line in lines:
		n = "\n"
		nn = "\\n"
		sendMatch = re.match(r"^send\(.*\)$", line)
		sendChannelMatch = re.match(r"^sendChannel\(.*\)$", line)
		if sendMatch:
			line = line.replace("\\n", "\n")
			sendText = line[sendMatch.start():sendMatch.end()].lstrip("send(").rstrip(")")
			for var, value in variables.items():
				if var in sendText:
					sendText = sendText.replace(var, value)
			await ctx.send(sendText, allowed_mentions=nomention)
		elif sendChannelMatch:
			line = line.replace("\\n", "\n")
			args = line[sendChannelMatch.start():sendChannelMatch.end()].lstrip("sendChannel(").rstrip(")").split(",")
			if len(args) != 2:
				return await ctx.send(f"Line ```\n{line.replace('`', '​`​').replace(n, nn)}``` threw an error while parsing arguments for `sendChannel()`.", allowed_mentions=nomention)
			for var, value in variables.items():
				if var in args[0]:
					args[0] = args[0].replace(var, value)
				if var in args[1]:
					aargs[1] = args[1].replace(var, value)
			try:
				channel = await commands.TextChannelConverter().convert(ctx, args[0])
			except commands.ChannelNotFound:
				return await ctx.send(f"Line ```\n{line.replace('`', '​`​').replace(n, nn)}``` threw an error while parsing argument `channel`.", allowed_mentions=nomention)
			if channel.guild.id != ctx.guild.id:
				return await ctx.send(f"Line ```\n{line.replace('`', '​`​').replace(n, nn)}``` threw an error, as you cannot send messages to channels not in the current guild.", allowed_mentions=nomention)
			await channel.send(args[1], allowed_mentions=nomention)
		else:
			return await ctx.send(f"Line ```\n{line.replace('`', '​`​').replace(n, nn)}``` is invalid.", allowed_mentions=nomention)

class CustomCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot			

	@commands.command()
	async def run(self, ctx, *, CCcode):
		"""
		Basically evals a line of code from the arguments.
		"""
		await runcode(CCcode, ctx)

	@commands.command(aliases=['rfh'])
	async def runfromhaste(self, ctx, id):
		"""
		Runs code from a hastebin.com key. It must be the key and only the key, which is the part after hastebin.com/.
		"""
		async with aiohttp.ClientSession() as s:
			async with s.get("https://hastebin.com/raw/" + id) as resp:
				code = await resp.text()
				await runcode(code, ctx)

	@commands.command(aliases=['vars'])
	async def variables(self, ctx):
		"""
		Shows all of the default variables for custom commands.
		"""
		await ctx.send(embed=discord.Embed(title="Default variables", description="""
		**$message.content**: The content of the message used to invoke this.
		**$message.id**: The id of the message used to invoke this.
		**$author.tag**: The tag of the user who invoked this.
		**$author.id**: The id of the user who invoked this.
		**$author.nick**: The nickname (or name if they do not have one) of the user who invoked this.
		**$author.name**: The name of the user who invoked this.
		""".replace("	", "")
		))

def setup(bot):
	bot.add_cog(CustomCommands(bot))
	print('[CCCog] Custom commands cog loaded')
