import discord, random, asyncio, aiohttp, os, postbin, typing, datetime
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

	@commands.command(name="resetinvites", aliases=['wipeinv', 'delinvs'])
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	async def resetinvites(self, ctx, *ignore: discord.Invite):
		"""
		Deletes all invites in the server, pass invite arguments after the command to ignore said invites.
		"""
		if len(await ctx.guild.invites()) < 1:
			return await ctx.send(f"**{ctx.guild}** has no invites!")
		else:
			m = await ctx.send(f"Deleting {ctx.guild}'s invites...")
		deleted = []
		ignored = []
		failed = []
		embed = discord.Embed(title=f"Bulk Deleted {ctx.guild}'s Invites!")
		for inv in await ctx.guild.invites():
			if not inv in ignore:
				try:
					await inv.delete(reason=f"Bulk delete by {ctx.author} ({ctx.author.id})")
					deleted.append(f"`{inv.code}`")
				except: 
					failed.append(f"`{inv.code}`")
			else:
				ignored.append(f"`{inv.code}`")
		embed.add_field(name="Deleted:", value=((", ".join(deleted)) or "None"))
		embed.add_field(name="Ignored:", value=((", ".join(ignored)) or "None"))
		embed.add_field(name="Couldn't Delete:", value=((", ".join(failed)) or "None"))
		await m.edit(content=None, embed=embed)

	@commands.command(name="servername", aliases=['sname', 'guildname', 'gname'])
	@commands.has_permissions(manage_guild=True)
	@commands.guild_only()
	async def guildname(self, ctx, *, newname):
		"""
		Changes the server's name.
		"""
		oldname = ctx.guild.name
		if len(newname) > 100:
			await ctx.send("This name is too long! Server names must be between 2 and 100 characters.")
		elif len(newname) < 2:
			await ctx.send("This name is too short! Server names must be between 2 and 100 characters.")
		else:
			await ctx.guild.edit(name=newname, reason=(f"Server name changed by {ctx.author} ({ctx.author.id})"))
			await ctx.send(f"Changed the server's name!\nBefore: `{oldname}`\nAfter: `{ctx.guild.name}`")

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
			url = await postbin.postAsync(members)
			await ctx.send(f"List is too big to send, view the hastebin link below.\n{url}")
		else:
			embed.description=members
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
	async def userinfo(self, ctx, user=None):
		"""
		Shows some info about a user. Defaults to self.
		"""
		user = user or ctx.author.id
		badges = {
			discord.UserFlags.early_supporter: f"{self.bot.get_emoji(778489157055414272)} Early supporter",
			discord.UserFlags.bug_hunter: f"{self.bot.get_emoji(778489159551025162)} Bug hunter",
			discord.UserFlags.bug_hunter_level_2: f"{self.bot.get_emoji(778489160080162826)} Bug hunter level 2",
			discord.UserFlags.partner: f"{self.bot.get_emoji(778489162847879179)} Discord partner",
			discord.UserFlags.verified_bot_developer: f"{self.bot.get_emoji(778489155977216050)} Early verified bot developer",
			discord.UserFlags.staff: f"{self.bot.get_emoji(778489158221955103)} Discord staff",
			discord.UserFlags.hypesquad_bravery: f"{self.bot.get_emoji(778489151288246273)} Hypesquad bravery",
			discord.UserFlags.hypesquad_brilliance: f"{self.bot.get_emoji(778489152228163604)} Hypesquad brilliance",
			discord.UserFlags.hypesquad_balance: f"{self.bot.get_emoji(778489153405845544)} Hypesquad balance",
			discord.UserFlags.hypesquad: f"{self.bot.get_emoji(778489154585362442)} Hypesquad events",
			"nitro": f"{self.bot.get_emoji(779954141262774293)} Nitro",
			"nitro_guess": f"{self.bot.get_emoji(779954141262774293)} Nitro (⚠ This is a guess, I cannot tell for certain.)",
		}
		bot = self.bot
		try: user = int(user)
		except: pass
		if isinstance(user, int):
			user_temp = bot.get_user(user)
			if user_temp == None:
				try:
					user_temp = await bot.fetch_user(user)
				except discord.errors.NotFound:
					return await ctx.send("I detected that you gave an id, but could not find the user.")
			else:
				user_temp_temp = ctx.guild.get_member(user)
				if user_temp_temp != None:
					user_temp = user_temp_temp
			user = user_temp
		else:
			user_temp = discord.utils.get(bot.users, name=user)
			if user_temp == None:
				return await ctx.send("The text you gave was not an id, but I could not find them by name.")
			user = user_temp
		flags_nice = []
		for flag in user.public_flags.all():
			if flag in badges:
				flags_nice.append(badges[flag])
		if user.is_avatar_animated():
			flags_nice.append(badges["nitro"])
		elif int(user.discriminator) < 7:
			flags_nice.append(badges["nitro_guess"])
		if isinstance(user, discord.Member):
			if user.premium_since != None:
				ms = round((datetime.datetime.now() - user.premium_since).days / 30, 0)
				if ms >= 24: flags_nice.append(f"{bot.get_emoji(779966418006442004)} 24+ Month server boost")
				elif ms >= 18: flags_nice.append(f"{bot.get_emoji(779966630016581653)} 18+ Month server boost")
				elif ms >= 15: flags_nice.append(f"{bot.get_emoji(779966518352019466)} 15+ Month server boost")
				elif ms >= 12: flags_nice.append(f"{bot.get_emoji(779966734177927209)} 12+ Month server boost")
				elif ms >= 9: flags_nice.append(f"{bot.get_emoji(779966686614650959)} 9+ Month server boost")
				elif ms >= 6: flags_nice.append(f"{bot.get_emoji(779966584298012683)} 6+ Month server boost")
				elif ms >= 3: flags_nice.append(f"{bot.get_emoji(779966455407706132)} 3+ Month server boost")
				elif ms >= 2: flags_nice.append(f"{bot.get_emoji(779966286426931202)} 2+ Month server boost")
				elif ms >= 1: flags_nice.append(f"{bot.get_emoji(779966812321349653)} 1+ Month server boost")
		if len(flags_nice) <= 0:
			flags_nice = "No badges."
		else:
			flags_nice = "\n".join(flags_nice)
		if isinstance(user, discord.Member):
			if user.status == discord.Status.online:
				status = bot.get_emoji(778489146703609896)
			elif user.status == discord.Status.idle:
				status = bot.get_emoji(778489147420704789)
			elif user.status == discord.Status.dnd:
				status = bot.get_emoji(778489150148050996)
			elif user.status == discord.Status.offline:
				status = bot.get_emoji(778489148750561292)
			if user.is_on_mobile():
				mobile = "✅"
			else:
				mobile = "❌"
			embed = discord.Embed(
				title=f"{str(user)}'s Info:", 
				description=f"""**Nickname:** {user.nick}
				**User ID:** `{user.id}`
				**Role count:** {len(user.roles)}
				**Joined Server on:** {user.joined_at.astimezone(timezone('US/Mountain')).strftime("%a, %B %d, %Y at %I:%M%p MST")}
				**Account Created on:** {user.created_at.astimezone(timezone('US/Mountain')).strftime("%a, %B %d, %Y at %I:%M%p MST")}
				**Status:** {status}
				**Bot:** {'✅' if user.bot else '❌'}
				**Mobile:** {mobile}
				**Badges:**
				{flags_nice}"""
				.replace("	", ""),
				thumbnail=user.avatar_url,
				color=user.color
				)
			embed.add_field(name="Custom Status", value=f"```{user.activity}```", inline=False)
		else:
			embed = discord.Embed(
				title=f"{str(user)}'s Info:", 
				description=f"""**Name:** {user.name}
				**User ID:** `{user.id}`
				**Account Created on:** {user.created_at.astimezone(timezone('US/Mountain')).strftime("%a, %B %d, %Y at %I:%M%p MST")}
				**Bot:** {'✅' if user.bot else '❌'}
				**Badges:**
				{flags_nice}"""
				.replace("	", ""),
				thumbnail=user.avatar_url,
				)
			embed.set_footer(text="⚠ The user was not in the current server, so I can only get minimal info.")
		await ctx.send(embed=embed)

	@commands.command(name="avatar", aliases=['av', 'pfp'])
	async def avatar(self, ctx, user: discord.Member=None):
		"""
		Shows the user's avatar.
		"""
		user = user or ctx.author
		embed=discord.Embed(title=f"{user}'s Avatar", description=f"Download avatar here: [Download Link]({str(user.avatar_url)})", color=user.color)
		embed.set_image(url=user.avatar_url)
		embed.set_footer(text=f"ID: {user.id}")
		await ctx.send(embed=embed)

	@commands.command(name="serverinfo", aliases=['si', 'server', 'guildinfo', 'gi', 'guild'])
	@commands.guild_only()
	async def serverinfo(self, ctx, guildid: int=None):
		"""
		Shows some info about the server.
		"""
		bot = self.bot
		g = ctx.guild
		if guildid != None and bot.get_guild(guildid):
			g = bot.get_guild(guildid)
		humans = 0
		bots = 0
		systemchan = 'None set'
		if g.system_channel != None:
			systemchan = g.system_channel.mention
		ruleschan = 'None set'
		if g.rules_channel != None:
			ruleschan = g.rules_channel.mention
		authreq = 'No'
		if g.mfa_level > 0:
			authreq = 'Yes'
		vlevels = ["None: Unrestricted", "Low: Must have a verified email on their Discord account.", "Medium: Must also be registered on Discord for longer than 5 minutes.", "(╯°□°）╯︵ ┻━┻  (High): Must also be a member of this server for longer than 10 minutes.", "┻━┻ ﾐヽ(ಠ益ಠ)ノ彡┻━┻  (Highest): Must have a verified phone on their Discord account."]
		for m in g.members:
			if m.bot:
				bots = bots + 1
			else:
				humans = humans + 1
		embed = discord.Embed(
			title=f"{g.name}'s Info",
			description=f"""**Owner:** {g.owner} ({g.owner.id})
			**Members:** Total- {g.member_count}, Humans- {humans}, Bots- {bots}
			**Channels:** {bot.get_emoji(778489166316175413)} {len(g.categories)} categories, {bot.get_emoji(778489167649701898)} {len(g.text_channels)} text, {bot.get_emoji(778489169000661002)} {len(g.voice_channels)} voice
			**Roles:** {len(g.roles)-1}
			**Emojis:** {len(g.emojis)}
			**Features:** {', '.join(g.features)}
			**System Messages:** {systemchan}
			**Rules Channel:** {ruleschan}
			**2FA Required?** {authreq}
			**Verification Level:** {vlevels[g.verification_level.value]}
			**Region:** {g.region}
			
			[Link to Icon]({g.icon_url})"""
			.replace("	", ""),
			color=bot.utils.randcolor()
		)
		# embed.add_field(name=f"Emojis ({len(g.emojis)}):", value=f"{for e in g.emojis: ems = f'{ems} {e}'}")
		embed.set_footer(text=f"ID: {g.id} | Created on ", icon_url=g.icon_url)
		embed.timestamp=g.created_at #Created on {g.created_at.astimezone(timezone('US/Mountain')).strftime("%a, %B %d, %Y at %I:%M%p MST")}")
		await ctx.send(embed=embed)
	
#	@commands.command(name="poll")
#	async def poll(self, ctx, question: str, desc: str=None, pingrole: typing.Optional[discord.Role]=None):
#		content = ""
#		if pingrole != None:
#			content = pingrole.mention
#		await ctx.message.delete()
#		m = await ctx.send(embed=discord.Embed(title=question, description=desc))
#		await m.add_reaction("👍")
#		await m.add_reaction("👎")

	@commands.command(name="newrole", aliases=['createrole', 'crole', 'addrole'])
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True)
	@commands.guild_only()
	async def newrole(self, ctx, color: discord.Color=None, hoist: bool=False, position: int=None, *name):
		r = await ctx.guild.create_role(name=name, color=color, hoist=hoist, reason=f"Role created by {ctx.author} ({ctx.author.id})")
		await ctx.send(f"Created {r.mention}!", allowed_mentions=discord.AllowedMentions(roles=False))


	@commands.command(name="giverole", aliases=['giveroles', 'grole', 'groles'])
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True)
	@commands.guild_only()
	async def giverole(self, ctx, member: discord.Member, *roles: discord.Role):
		"""
		Gives a role or list of roles to another user that you have permission to add them to.
		"""
		given = []
		failed = []
		if len(roles) == 0:
			await ctx.send("You have to specify at least one role to give!")
		else:
			for role in roles:
				if role >= ctx.guild.me.top_role:
					await ctx.send(f"I can't give {role.name} to other users as it is above my highest role!")
					failed.append(role)
				elif role > ctx.author.top_role:
					await ctx.send("You can't give roles above your highest role!")
					failed.append(role)
				elif member.top_role > ctx.author.top_role:
					await ctx.send("You can't change the roles of people above you!")
					failed.append(role)
				else:
					await member.add_roles(role, reason=f"{ctx.author} gave {member.name} {role.name}.")
					given.append(role)
			await ctx.send(f"Gave {member.mention} some roles!\nRoles given: {', '.join([x.mention for x in given])}", allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False))

	@commands.command(name="takerole", aliases=['takeroles', 'trole', 'troles', 'removerole', 'removeroles', 'rrole'])
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True)
	@commands.guild_only()
	async def takerole(self, ctx, member: discord.Member, *roles: discord.Role):
		"""
		Takes a role or list of roles from another user that you have permission to remove them from.
		"""
		taken = []
		if len(roles) == 0:
			await ctx.send("You have to specify at least one role to remove!")
		else:
			for role in roles:
				if role >= ctx.guild.me.top_role:
					await ctx.send(f"I can't remove {role.name} from other users as it is above my highest role!")
				elif role > ctx.author.top_role:
					await ctx.send("You can't remove roles above your highest role!")
				elif member.top_role > ctx.author.top_role:
					await ctx.send("You can't change the roles of people above you!")
				else:
					await member.remove_roles(role, reason=f"{ctx.author} removed {role.name} from {member.name}.")
			await ctx.send(f"Removed some role from {member.mention}!\nRoles taken: {', '.join([x.mention for x in taken])}", allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False))

	@commands.command(name="setnick")
	@commands.bot_has_permissions(manage_nicknames=True)
	async def setnick(self, ctx, member: discord.Member, *, newnick=None):
		mem = member or ctx.author
		oldnick = member.nick
		if ctx.author.id != mem.id and (getattr(ctx.author.guild_permissions, "manage_nicknames") == False):
			await ctx.send("You don't have permissions to change other users' nicknames!")
		elif ctx.author.id != mem.id and (getattr(ctx.author.guild_permissions, "manage_nicknames") == True):
			if mem.top_role >= ctx.guild.me.top_role:
				await ctx.send("I can't change this user's nickname as their highest role is above mine!")
			elif mem.top_role >= ctx.author.top_role:
				await ctx.send("You can't change this user's nickname as their highest role is above yours!")
			elif (newnick != None) and (len(newnick) > 32):
				await ctx.send("This nickname is too long! It must be 32 characters or less.")
			else:
				await mem.edit(nick=newnick, reason=f"Nickname changed from {oldnick} to {mem.nick} by {ctx.author} ({ctx.author.id})!")
				await ctx.send(f"Changed {mem.mention}'s nickname from `{oldnick}` to `{mem.nick}`")
		elif ctx.author.id == mem.id and (getattr(ctx.author.guild_permissions, "change_nickname") == False):
			await ctx.send("You don't have permission to change your nickname!")
		elif ctx.author.id == mem.id and (getattr(ctx.author.guild_permissions, "change_nickname") == True):
			await mem.edit(nick=newnick, reason=f"User changed their nickname from {oldnick} to {newnick}")
			await ctx.send(f"Changed your nickname from `{oldnick}` to `{mem.nick}`!")

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
					try:
						website = (await r.json())["snapshot"]
						await ctx.send(embed=discord.Embed(color=discord.Color.blurple()).set_image(url=website))
					except aiohttp.ContentTypeError:
						await ctx.send("Failed to decode json, here is raw web response: " + await postbin.postAsync(await r.text()))

	@commands.command(name="afk")
	async def afk(self, ctx, *, afkmessage="AFK"):
		"""
		Sets your AFK message.
		"""
		db = await self.bot.dbquery("afk", "message", f"userid={ctx.author.id}")
		if db:
			await self.bot.dbexec((f"DELETE FROM afk WHERE userid={ctx.author.id}"))
			if afkmessage == "AFK":
				await ctx.send(f"{ctx.author.mention}, I removed your AFK!")
			else:
				await ctx.send(f"{ctx.author.mention}, I set your AFK message to `{afkmessage}`!")
				await self.bot.dbexec((f"INSERT INTO afk VALUES (?, ?)", (str(ctx.author.id), str(afkmessage))))
		else:
			await ctx.send(f"{ctx.author.mention}, I set your AFK message to `{afkmessage}`!")
			await self.bot.dbexec((f"INSERT INTO afk VALUES (?, ?)", (str(ctx.author.id), str(afkmessage))))


	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		ch = self.bot.get_channel(payload.channel_id)
		if str(payload.emoji) == "📣":
			if ch.type != discord.ChannelType.news:
				await ch.send(f"<#{ch.id}> is not an announcement channel!", delete_after=5)
			else:
				msg = await ch.fetch_message(payload.message_id)
				try:
					await msg.publish()
					await ch.send(f"Sucessfully published <{msg.jump_url}>!", delete_after=5)
				except discord.HTTPException:
					await ch.send(f"Couldn't publish <{msg.jump_url}>.", delete_after=5)

def setup(bot):
	bot.add_cog(Utils(bot))
	print('[UtilsCog] Utils cog loaded')
