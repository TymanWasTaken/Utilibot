import discord, random, asyncio, string, aiofiles, json, DiscordUtils, postbin
from discord.ext import commands
import datetime
import importlib

async def readDB():
	try:
		async with aiofiles.open('/home/tyman/code/utilibot/data.json', mode='r') as f:
			return json.loads(await f.read())
	except Exception as e:
		print(f"An error occurred, {e}")

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

def randcolor():
	return int("%06x" % random.randint(0, 0xFFFFFF), 16)

def permsfromvalue(value):
	perms = discord.Permissions(permissions=int(value))
	perms_true = sorted([x for x,y in dict(perms).items() if y])
	perms_false = sorted([x for x,y in dict(perms).items() if not y])
	nice_perms = ""
	perms_true = ["\u2705 `" + s for s in perms_true]
	perms_false = ["\u274c `" + s for s in perms_false]
	perms_combined = sorted(perms_true + perms_false, key=lambda x: x.strip('\u2705\u274c'))
	for perm in perms_combined:
		nice_perms = nice_perms + perm.replace("_", " ").capitalize() + "`\n"
	return nice_perms

class Info(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def ping(self, ctx):
		"""
		Get the bot's latency, in miliseconds.
		"""
		if ctx.channel.permissions_for(ctx.me).embed_links == False:
			return await ctx.send("It appears I do not have permission to `Link embeds` in this channel. Please give me this permission or try in a channel where I do have it, as it is necessary to run this command.")
		embed1 = discord.Embed(title="Pong!", description=f"Given Latency:`{round(self.bot.latency * 1000)}ms`", color=randcolor())
		m = await ctx.send(embed=embed1)
		time = m.created_at - ctx.message.created_at
		embed2 = discord.Embed(title="Pong!", description=f"Given Latency: `{round(self.bot.latency * 1000)}ms`\nMeasured Latency: `{int(time.microseconds / 1000)}ms`", color=randcolor())
		await m.edit(embed=embed2)

	@commands.command()
	async def invite(self, ctx):
		"""
		Get the invite for the bot, and support server.
		"""
		bot = self.bot
		invitelink = f"https://discord.gg/"
		for invite in await bot.get_guild(755887706386726932).invites():
			if invite.temporary == True:
				pass
			else:
				invitelink = invitelink + invite.code
				break
		else:
			newinvite = await bot.get_channel(755910440533491773).create_invite(reason="Creating invite to the server for an invite command.")
			invitelink = invitelink + newinvite.code
		if ctx.channel.permissions_for(ctx.me).embed_links == False:
			return await ctx.send("It appears I do not have the `Embed Links` permission in this channel. Please give me this permission or try again in a channel where I do have it, as it is necessary to run this command.")
		embed = discord.Embed(title="Invite link", description=f"Click the links below to invite the bot to your server, or join our support server!\n[Click me to invite the bot!](https://discord.com/oauth2/authorize?client_id=755084857280954550&scope=bot&permissions=3501078)\n[Click me to join the support server!]({invitelink})", color=randcolor())
		await ctx.send(embed=embed)
	
	@commands.command(name="botperms", aliases=['botpermissions'])
	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	async def _bot_permissions(self, ctx, channel_permissions="False"):
		"""
		Shows all of the bot's permissions, neatly sorted.

		channel_permissions = Whether or not to check the channel permissions, instead of the guild ones (default false)
		"""
		if ctx.channel.permissions_for(ctx.me).embed_links == False:
			return await ctx.send("It appears I do not have the `Embed Links` permission in this channel. Please give me this permission or try again in a channel where I do have it, as it is necessary to run this command.")
		if channel_permissions.lower() == "true":
			await ctx.send(embed=discord.Embed(title="All of the bot's permissions in this channel (Permissions not able to be used in this type of channel will show as denied):", description=permsfromvalue(ctx.channel.permissions_for(ctx.me).value) + "\nRun `u!requiredperms` to see which ones the bot needs.", color=randcolor()))
		elif channel_permissions.lower() == "false":
			await ctx.send(embed=discord.Embed(title="All of the bot's permissions in this server:", description=permsfromvalue(ctx.me.guild_permissions.value) + "\nRun `u!requiredperms` to see which ones the bot needs.", color=randcolor()))

	@commands.command()
	async def requiredperms(self, ctx):
		if ctx.channel.permissions_for(ctx.me).embed_links == False:
			return await ctx.send("It appears I do not have the `Embed Links` permission in this channel. Please give me this permission or try again in a channel where I do have it, as it is necessary to run this command.")
		embed=discord.Embed(title="Required permissions for the bot:", description="Necessary perms:\n`Read messages`, `Send messages`, `Embed links`\nPerms for commands to run:\n`Kick members`, `Ban members`, `Manage messages`, `Manage channels`", color=randcolor())
		await ctx.send(embed=embed)

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

	@commands.command()
	@commands.is_owner()
	async def chelp(self, ctx, *, argument=None):
		"""
		Displays the help command, self-explanatory.
		"""
		if argument == None:
			bot_commands = self.bot.commands
			embed = discord.Embed(title="Commands")
			sorted_commands = {}
			for cog_name in self.bot.cogs:
				cog = self.bot.get_cog(cog_name)
				sorted_commands[cog_name] = cog.get_commands()
			sorted_commands["No category"] = [cmd for cmd in bot_commands if cmd.cog == None]
			help_texts = []
			for cmds in sorted_commands:
				if len(sorted_commands[cmds]) < 1:
					continue
				category_text = f"**__{cmds}__**:\n"
				for cmd in sorted_commands[cmds]:
					if not cmd.hidden:
						if cmd.short_doc:
							if len(cmd.help) < 65:
								category_text = category_text + f"**{cmd.name}**: {cmd.short_doc}\n"
							else:
								category_text = category_text + f"**{cmd.name}**: {cmd.short_doc[0:65]}...\n"
						else:
							category_text = category_text + f"**{cmd.name}**: No description.\n"
				help_texts.append(category_text)
			help_texts = [txt + "\n" for txt in help_texts]
			pages, current = [], next(iter(help_texts))
			passed_start = False
			for text in help_texts:
				if passed_start == False:
					passed_start = True
					continue
				if len(current) + 1 + len(text) > 2048:
					pages.append(current)
					current = text
				else:
					current += " " + text
			embeds = [discord.Embed(title="Bot commands", description=page) for page in pages]
			if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
				paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, timeout=60, remove_reactions=True, auto_footer=True)
			else:
				paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, timeout=60, remove_reactions=False, auto_footer=True)
			paginator.add_reaction('⏮️', "first")
			paginator.add_reaction('⏪', "back")
			paginator.add_reaction('⏹', "lock")
			paginator.add_reaction('⏩', "next")
			paginator.add_reaction('⏭️', "last")
			return await paginator.run(embeds)
		cmd = None
		for command in self.bot.commands:
			if isinstance(command, commands.core.Group):
				for subcommand in command.commands:
					if command.qualified_name.lower() == argument.lower():
						cmd = command
						break
					for alias in command.aliases:
						if alias.lower() == argument.lower():
							cmd = command
							break
				else:
					if command.qualified_name.lower() == argument.lower():
						cmd = command
						break
					for alias in command.aliases:
						if alias.lower() == argument.lower():
							cmd = command
							break
			else:
				if command.qualified_name.lower() == argument.lower():
					cmd = command
					break
				for alias in command.aliases:
					if alias.lower() == argument.lower():
						cmd = command
						break
		if cmd != None:
			n = "\n"
			if isinstance(cmd, commands.core.Group):
				command_text = f"\n**__{cmd.qualified_name}__**:\n"
				for command in cmd.commands:
					if not command.hidden:
						if command.short_doc:
							if len(command.help) < 65:
								command_text = command_text + f"**{command.name}**: {command.short_doc}\n"
							else:
								command_text = command_text + f"**{command.name}**: {command.short_doc[0:65]}...\n"
						else:
							command_text = command_text + f"**{command.name}**: No description.\n"
				gcs = command_text
			else:
				gcs = ""
			if len(cmd.aliases) > 0:
				embed = discord.Embed(description=f"`{ctx.prefix}[{cmd.name}|{'|'.join(cmd.aliases)}]{f' {cmd.signature}' if cmd.signature != '' else ''}`\n\nCategory name: {cmd.cog.qualified_name if command.cog else 'none'}\n{f'```{n}{cmd.help}```' if cmd.help != None else ''}{gcs}")
			else:
				embed = discord.Embed(description=f"`{ctx.prefix}{cmd.qualified_name}{f' {cmd.signature}' if cmd.signature != '' else ''}`\n\nCategory name: {cmd.cog.qualified_name if command.cog else 'none'}\n{f'```{n}{cmd.help}```' if cmd.help != None else ''}{gcs}")
			return await ctx.send(embed=embed)
		cog = [cog for cog in self.bot.cogs if cog.lower() == argument.lower()]
		if len(cog) > 0: cog = self.bot.get_cog(cog[0])
		else: cog = None
		if cog != None:
			cog_text = ""
			for cmd in cog.get_commands():
				if not cmd.hidden:
					if cmd.short_doc:
						if len(cmd.help) < 65:
							cog_text = cog_text + f"**{cmd.name}**: {cmd.short_doc}\n"
						else:
							cog_text = cog_text + f"**{cmd.name}**: {cmd.short_doc[0:65]}...\n"
					else:
						cog_text = cog_text + f"**{cmd.name}**: No description.\n"
			embed = discord.Embed(title=f"{cog.qualified_name} commands", description=cog_text)
			return await ctx.send(embed=embed)
		await ctx.send(f"Could not find command/cog `{argument}`.")


def setup(bot):
	bot.add_cog(Info(bot))
	commands.HelpCommand.cog = Info(bot)
	print('[InfoCog] Info cog loaded')
