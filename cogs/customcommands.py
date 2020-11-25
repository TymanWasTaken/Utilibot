import discord, random, re, aiohttp
from discord.ext import commands
from discord.ext.commands import MemberConverter
nomention = discord.AllowedMentions(everyone=False, roles=False, users=False)

class dictToClass:
	def __init__(self, dictionary):
		for key in dictionary:
			setattr(self, key, dictionary[key])

class ccAuthor:
	def __init__(self, obj):
		self.id = obj.author.id
		self.name = obj.author.name
		self.nick = obj.author.nick or obj.author.name
		self.tag = str(obj.author)
		self.discriminator = obj.author.discriminator
		self.mention = obj.author.mention

class ccMessage:
	def __init__(self, obj):
		self.content = obj.message.content
		self.clean_content = obj.message.clean_content
		self.id = obj.message.id
		self.link = obj.message.jump_url

class ccChannel:
	def __init__(self, obj):
		self.id = obj.channel.id
		self.name = obj.channel.name
		self.mention = f"<#{obj.channel.id}>"

class ccGuild:
	def __init__(self, obj):
		self.id = obj.guild.id
		self.name = obj.guild.name

# def parseVars

async def runcode(code, ctx):
	lines = code.split("\n")
	member = ctx.guild.get_member(ctx.author.id)
	variables = {
		"author": ccAuthor,
		"message": ccMessage,
		"channel": ccChannel,
		"guild": ccGuild
	}
	for line in lines:
		n = "\n"
		nn = "\\n"
		sendMatch = re.match(r"^send\((.*)\)$", line)
		sendChannelMatch = re.match(r"^sendChannel\((.*)\)$", line)
		# varMatch = re.match(r"^(.*)=(.*)$")
		if sendMatch:
			line = line.replace("\\n", "\n")
			sendText = sendMatch.group(1)
			if sendText == "":
				return await ctx.send(f"Line ```\n{line.replace('`', '​`​').replace(n, nn)}``` is invalid. You cannot send an empty message", allowed_mentions=nomention)
			for var, value in variables.items():
				if var in sendText:
					varReg = re.search(fr"\${var}\.(.*)\$", sendText)
					if varReg == None:
						continue
					attrRaw = varReg.group(1)
					try:
						attr = getattr(variables[var](ctx), attrRaw)
					except:
						return await ctx.send(f"Line ```\n{line.replace('`', '​`​').replace(n, nn)}``` is invalid. Variable `${var}.{attrRaw}$` is not a valid variable.", allowed_mentions=nomention)
					sendText = sendText.replace(f"${var}.{attrRaw}$", str(attr))
			await ctx.send(sendText, allowed_mentions=nomention)
		elif sendChannelMatch:
			line = line.replace("\\n", "\n")
			args = sendChannelMatch.group(1).split(",")
			if len(args) != 2:
				return await ctx.send(f"Line ```\n{line.replace('`', '​`​').replace(n, nn)}``` threw an error while parsing arguments for `sendChannel()`. You must give 2 arguments.", allowed_mentions=nomention)
			for var, value in variables.items():
				if var in args[0]:
					varReg = re.search(fr"\${var}\.(.*)\$", args[0])
					if varReg == None:
						continue
					attrRaw = varReg.group(1)
					try:
						attr = getattr(variables[var](ctx), attrRaw)
					except:
						return await ctx.send(f"Line ```\n{line.replace('`', '​`​').replace(n, nn)}``` is invalid. Variable `${var}.{attrRaw}$` is not a valid variable.", allowed_mentions=nomention)
					args[0] = args[0].replace(f"${var}.{attrRaw}$", str(attr))
				if var in args[1]:
					varReg = re.search(fr"\${var}\.(.*)\$", args[1])
					if varReg == None:
						continue
					attrRaw = varReg.group(1)
					try:
						attr = getattr(variables[var](ctx), attrRaw)
					except:
						return await ctx.send(f"Line ```\n{line.replace('`', '​`​').replace(n, nn)}``` is invalid. Variable `${var}.{attrRaw}$` is not a valid variable.", allowed_mentions=nomention)
					args[1] = args[1].replace(f"${var}.{attrRaw}$", str(attr))
			try:
				channel = await commands.TextChannelConverter().convert(ctx, args[0])
			except commands.ChannelNotFound:
				return await ctx.send(f"Line ```\n{line.replace('`', '​`​').replace(n, nn)}``` threw an error while parsing argument `channel`.", allowed_mentions=nomention)
			if channel.guild.id != ctx.guild.id:
				return await ctx.send(f"Line ```\n{line.replace('`', '​`​').replace(n, nn)}``` threw an error, as you cannot send messages to channels not in the current guild.", allowed_mentions=nomention)
			await channel.send(args[1], allowed_mentions=nomention)
		# elif varMatch:
		# 	if varMatch.group(0) == "" or varMatch.group(2) == "":
		# 		return await ctx.send(f"Line ```\n{line.replace('`', '​`​').replace(n, nn)}``` is invalid. Either the var name or value was empty.", allowed_mentions=nomention)
		# 	variables[varMatch.group(1)] = varMatch.group(2)
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