import discord, random, asyncio, aiohttp, os, postbin, typing
from discord.ext import commands
from pytz import timezone
from dotenv import load_dotenv
load_dotenv(dotenv_path="/home/tyman/code/utilibot/.env")

def randcolor():
	return int("%06x" % random.randint(0, 0xFFFFFF), 16)

def permsfromvalue(value):
	perms = discord.Permissions(permissions=value)
	perms_true = sorted([x for x,y in dict(perms).items() if y])
	perms_false = sorted([x for x,y in dict(perms).items() if not y])
	nice_perms = ""
	perms_true = ["\u2705 `" + s for s in perms_true]
	perms_false = ["\u274c `" + s for s in perms_false]
	perms_combined = sorted(perms_true + perms_false, key=lambda x: x.strip('\u2705\u274c'))
	for perm in perms_combined:
		nice_perms = nice_perms + perm.replace("_", " ").capitalize() + "`\n"
	return nice_perms

class Utils(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="allperms")
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	@commands.guild_only()
	async def loop_channels(self, ctx, permission, state, role: discord.Role):
		"""
		Change permission overrides for all channels.
		"""
		state = state.lower()
		permission = permission.lower()
		if state == "true":
			state = True
		elif state == "neutral":
			state = None
		elif state == "false":
			state = False
		else:
			return await ctx.send("State must be one of: True, Neutral, or False")
		m = await ctx.send(f"Changing permission `{permission}` to state `{state}` for role {role.name} on all channels.")
		for channel in ctx.guild.channels:
			await channel.set_permissions(role, **{permission: state})
		await m.edit(content=f"Changed permission `{permission}` to state `{state}` for role {role.name} on all channels.")

	@commands.command(name="announcechannel", aliases=['ac', 'achan',])
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	@commands.guild_only()
	async def annoucechannel(self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel]=None):
		"""
		A simple toggle to convert channels between Text and Announcements.
		"""
		if "NEWS" in ctx.guild.features:
			c = channel or ctx.channel
			curtype = c.type
			newtype = discord.ChannelType.news
			if curtype == discord.ChannelType.news:
				newtype = discord.ChannelType.text
			await c.edit(type=newtype, reason=f"{ctx.author} ({ctx.author.id}) converted this channel to type {newtype}.")
			await ctx.send(f"Changed <#{c.id}> to type `{newtype}`!")
		else:
			await ctx.send("❌ This server can't have announcement channels! Ask somebody with the `Manage Server` permission to enable Community in Server Settings, then try again.\nPlease do not run this command again until community has been enabled.")

	@commands.command(name="publish")
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.guild_only()
	async def publish(self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel]=None, message=None):
		"""
		Publishes a message.
		"""
		publishing = False
		if not "NEWS" in ctx.guild.features:
			await ctx.send("This server has no announcement channels!")
		else:
			ch = channel or ctx.channel
			if ch.type != discord.ChannelType.news:
				er = await ctx.send(f"<#{ch.id}> is not an announcement channel!")
				await er.delete(delay=5)
			else:
				msg = await ch.fetch_message(message)
				if msg.author.id != ctx.author.id:
					if ctx.channel.permissions_for(ctx.author).manage_messages == False:
						return await ctx.send("You can't publish this message as you did not write it and you do not have manage messages permissions!")
					else:
						publishing = True
				else:
					publishing = True
				if publishing == True:
					await msg.publish()
					conf = await ctx.send(f"Sucessfully published <https://discord.com/channels/{ctx.guild.id}/{ch.id}/{msg.id}>!")
					await conf.delete(delay=5)

	@commands.command(name="nuke", aliases=['nukechan', 'clone', 'resetchan'])
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def nuke(self, ctx, channel: typing.Optional[discord.TextChannel]=None):
		"""
		Resets a channel- Clones it and deletes the old one. Useful for clearing all the messages in a channel quickly.
		"""
		chan = channel or ctx.channel
		c = await chan.clone(reason=f"Channel reset by {ctx.author} ({ctx.author.id})")
		await c.edit(position=chan.position)
		try: 
			await chan.delete(reason=f"Channel reset by {ctx.author} ({ctx.author.id})")
		except:
			await chan.send(f"{ctx.author.mention}, I cannot delete this channel! (most likely cause is that it's set as a channel required for community servers)")
		await c.send(f"I reset this channel, {ctx.author.mention}!")

	@commands.command(name="resetinvites", aliases=['wipeinv', 'delinvs'])
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def resetinvites(self, ctx):
		"""
		Deletes all invites in the server.
		"""
		for inv in await ctx.guild.invites:
			await inv.delete(reason=f"Bulk delete by {ctx.author} ({ctx.author.id})")

	@commands.command(name="rolemembers", aliases=['members'])
	@commands.guild_only()
	async def rolemembers(self, ctx, *, role: discord.Role):
		if ctx.channel.permissions_for(ctx.me).embed_links == False:
			return await ctx.send("It appears I do not have the `Embed Links` permission in this channel. Please give me this permission or try again in a channel where I do have it, as it is necessary to run this command.")
		color = role.color
		members = ""	
		embed = discord.Embed(title=f"Members with the role __{role.name}__", color=color.value)
		for member in role.members:
			members = f"{members}\n• Username: `{member.name}#{member.discriminator}` ~ ID: `{member.id}` ~ Nickname: `{member.nick}`"
		if len(members) > 2048:
			url = postbin.postAsync(members)
			await ctx.send(f"List is too big to send, view the hastebin link below.\n{url}")
		else:
			embed.description=members
			await ctx.send(embed=embed)

	@commands.command(name="humans")
	@commands.guild_only()
	@commands.has_permissions(kick_members=True)
	async def humans(self, ctx):
		humans = ""
		embed = discord.Embed(title=f"Humans in __{ctx.guild.name}__")
		for member in ctx.guild.members:
			if member.bot:
				pass
			else:
				humans = f"{humans}\n• Username: `{member.name}#{member.discriminator}` ~ ID: `{member.id}` ~ Nickname: `{member.nick}`"
		if len(humans) > 2048:
			url = await postbin.postAsync(humans)
			await ctx.send(f"List is too big to send, view the hastebin link below.\n{url}")
		else:
			embed.description=humans
			await ctx.send(embed=embed)

	@commands.command(name="bots")
	@commands.guild_only()
	@commands.has_permissions(kick_members=True)
	async def bots(self, ctx):
		bots = ""
		embed = discord.Embed(title=f"Bots in __{ctx.guild.name}__")
		for member in ctx.guild.members:
			if not member.bot:
				pass
			else:
				bots = f"{bots}\n• Username: `{member.name}#{member.discriminator}` ~ ID: `{member.id}` ~ Nickname: `{member.nick}`"
		if len(bots) > 2048:
			url = await postbin.postAsync(bots)
			await ctx.send(f"List is too big to send, view the hastebin link below.\n{url}")
		else:
			embed.description=bots
			await ctx.send(embed=embed)

	@commands.command(name="allmembers")
	@commands.guild_only()
	@commands.has_permissions(kick_members=True)
	async def allmembers(self, ctx):
		allmembers = ""
		embed = discord.Embed(title=f"All members in __{ctx.guild.name}__")
		for member in ctx.guild.members:
			allmembers = f"{allmembers}\n• Username: `{member.name}#{member.discriminator}` ~ ID: `{member.id}` ~ Nickname: `{member.nick}`"
		if len(allmembers) > 2048:
			url = await postbin.postAsync(allmembers)
			await ctx.send(f"List is too big to send, view the hastebin link below.\n{url}")
		else:
			embed.description=allmembers
			await ctx.send(embed=embed)



	# @commands.command(name="allroles")
	# @commands.has_permissions(manage_roles=True)
	# @commands.bot_has_permissions(manage_roles=True)
	# async def loop_roles(self, ctx, permission, state):
	# 	"""
	# 	Change permission overrides for all roles.
	# 	"""
	# 	state = state.lower()
	# 	permission = permission.lower()
	# 	if state == "true":
	# 		state = True
	# 	elif state == "neutral":
	# 		state = None
	# 	elif state == "false":
	# 		state = False
	# 	else:
	# 		return await ctx.send("State must be one of: True, Neutral, or False")
	# 	for role in ctx.guild.roles:
	# 		await ctx.send(f"Role: {role}")
	# 		if role == ctx.guild.default_role:
	# 			continue
	# 		perms = role.permissions.update(**{permission: state})
	# 		await role.edit(permissions=perms)
	
	@commands.command(name="permissions", aliases=['perms', 'permsvalue'])
	async def permissions_from_value(self, ctx, value: int):
		"""
		Shows the permissions that correspond to a permissions value
		"""
		if ctx.channel.permissions_for(ctx.me).embed_links == False:
			return await ctx.send("It appears I do not have permission to `Link embeds` in this channel. Please give me this permission or try in a channel where I do have it, as it is necessary to run this command.")
		await ctx.send(embed=discord.Embed(title=f"Permissions for value {value}:", description=permsfromvalue(value), color=randcolor()))

	@commands.command(name="userinfo", aliases=['ui', 'user', 'info'])
	async def userinfo(self, ctx, user: discord.Member=None):
		bot = self.bot
		if user is None:
			user = ctx.guild.get_member(ctx.author.id)
		if user.status == discord.Status.online:
			status = bot.get_emoji(774816041632137226)
		elif user.status == discord.Status.idle:
			status = bot.get_emoji(774816228739907624)
		elif user.status == discord.Status.dnd:
			status = bot.get_emoji(774816849908727888)
		elif user.status == discord.Status.offline:
			status = bot.get_emoji(774816333912473611)
		if user.is_on_mobile():
			mobile = "✅"
		else:
			mobile = "❌"
		embed = discord.Embed(
			title=f"{str(user)}'s info:", 
			description=f"""**Nickname:** {user.nick}
			**User ID:** `{user.id}`
			**Role count:** {len(user.roles)}
			**Joined Server on:** {user.joined_at.astimezone(timezone('US/Mountain')).strftime("%a %B %d %Y %I:%M%p MST")}
			**Account Created on:** {user.created_at.astimezone(timezone('US/Mountain')).strftime("%a %B %d %Y %I:%M%p MST")}
			**Status:** {status}
			**Bot:** {'✅' if user.bot else '❌'}
			**Mobile:** {mobile}"""
			.replace("	", ""),
			thumbnail=user.avatar_url,
			color=user.color
			)
		await ctx.send(embed=embed)

	@commands.command(aliases=["tr"])
	async def translate(self, ctx, lang, *, text):
		"""
		A command that will translate text you give it to the language code you give it. You can see language codes with u!langs.	
		"""
		async with aiohttp.ClientSession() as s:
			async with ctx.typing():
				async with s.get("https://api.cognitive.microsofttranslator.com/languages?api-version=3.0") as resp:
					langs = await resp.json()
					langs = langs["translation"]
				if not lang in langs:
					return await ctx.send("Not a valid language code.")
				async with s.post(f"https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to={lang}", headers={"Ocp-Apim-Subscription-Key": os.getenv('TRANSLATE_TOKEN'), "Ocp-Apim-Subscription-Region": "centralus", "Content-Type": "application/json"}, data="[{'Text':'"+text+"'}]") as resp:
					response = await resp.json()
					await ctx.send(f'Translated from:\n - Lang: `{langs[response[0]["detectedLanguage"]["language"]]["name"]}`\n - Certainty: `{response[0]["detectedLanguage"]["score"]*100}%`\n\nTranslation:\n - `{response[0]["translations"][0]["text"]}`')

	@commands.command(aliases=["ftr"])
	async def fromtranslate(self, ctx, fromlang, tolang, *, text):
		"""
		Same as u!translate, but takes a language to translate from.	
		"""
		async with aiohttp.ClientSession() as s:
			async with ctx.typing():
				async with s.get("https://api.cognitive.microsofttranslator.com/languages?api-version=3.0") as resp:
					langs = await resp.json()
					langs = langs["translation"]
				if not (tolang in langs and fromlang in langs):
					return await ctx.send("Not a valid language code.")
				async with s.post(f"https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to={tolang}&from={fromlang}", headers={"Ocp-Apim-Subscription-Key": os.getenv('TRANSLATE_TOKEN'), "Ocp-Apim-Subscription-Region": "centralus", "Content-Type": "application/json"}, data="[{'Text':'"+text+"'}]") as resp:
					response = await resp.json()
					await ctx.send(f'Translation:\n - `{response[0]["translations"][0]["text"]}`')

	@commands.command()
	async def langs(self, ctx):
		async with aiohttp.ClientSession() as s:
			async with ctx.typing():
				async with s.get("https://api.cognitive.microsofttranslator.com/languages?api-version=3.0") as resp:
					langs = await resp.json()
					langsDict = langs["translation"]
					niceLangs = ""
					for key, value in langsDict.items():
						niceLangs = niceLangs + f"`{key}`: `{value['name']}`, "
					await ctx.send(niceLangs)

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.guild)
	async def web(self, ctx, *, url: str):
		async with ctx.typing():
			async with aiohttp.ClientSession() as s:
				async with s.post("http://magmachain.herokuapp.com/api/v1", headers=dict(website=url)) as r:
					website = (await r.json())["snapshot"]
					await ctx.send(embed=discord.Embed(color=discord.Color.blurple()).set_image(url=website))

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if reaction.emoji == "📣":
			ch = reaction.message.channel
			if ch.type != discord.ChannelType.news:
				er = await reaction.message.channel.send(f"<#{ch.id}> is not an announcement channel!")
				await er.delete(delay=5)
			else:
				msg = await ch.fetch_message(reaction.message.id)
				try:
					await msg.publish()
				except discord.HTTPException:
					pass
				conf = await reaction.message.channel.send(f"Sucessfully published <https://discord.com/channels/{msg.guild.id}/{ch.id}/{msg.id}>!")
				await conf.delete(delay=5)

def setup(bot):
	cog = Utils(bot)
	bot.add_listener(cog.on_reaction_add)
	bot.add_cog(cog)
	print('[UtilsCog] Utils cog loaded')
