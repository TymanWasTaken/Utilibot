import discord, random, asyncio, aiohttp, os, postbin, typing, datetime, json
from discord.ext import commands
from pytz import timezone
from dotenv import load_dotenv
load_dotenv(dotenv_path="/home/tyman/code/utilibot/.env")

def permsfromvalue(value):
	perms = discord.Permissions(permissions=value)
	perms_true = sorted([x for x,y in dict(perms).items() if y])
	perms_false = sorted([x for x,y in dict(perms).items() if not y])
	nice_perms = ""
	perms_true = [f"{bot.const_emojis['yes']} `" + s for s in perms_true]
	perms_false = [f"{bot.const_emojis['no']} `" + s for s in perms_false]
	perms_combined = sorted(perms_true + perms_false, key=lambda x: x.strip('\u2705\u274c'))
	for perm in perms_combined:
		nice_perms += f"{perm.replace('_', ' ').title()}`\n"
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
		try:
			getattr(discord.Permissions.all(), permission)
		except NameError:
			return await ctx.send("Invalid permission name.")
		if state == "true":
			state = True
		elif state == "neutral":
			state = None
		elif state == "false":
			state = False
		else:
			return await ctx.send("State must be one of: True, Neutral, or False")
		m = await ctx.send(f"Changing permission `{permission}` to state `{state}` for role {role.name} on all channels.")
		failed_channels = []
		for channel in ctx.guild.channels:
			original_overwrites = channel.overwrites_for(role)
			setattr(original_overwrites, permission, state)
			try:
				await channel.set_permissions(role, overwrite=original_overwrites)
			except:
				failed_channels.push(channel)
		await m.edit(content=f"Changed permission `{permission}` to state `{state}` for role {role.name} on all possible channels. Failed channels:\n{' '.join([ch.mention for ch in failed_channels])}")

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
		if len(newname) < 2 or len(newname) > 100:
			await ctx.send(f"This name is too {'short' if len(newname)<2 else 'long'}! Server names must be between 2 and 100 characters.")
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
		await ctx.send(embed=discord.Embed(title=f"Permissions for value {value}:", description=permsfromvalue(value), color=discord.Color.random()))

	@commands.command(name="userinfo", aliases=['ui', 'user', 'info'])
	async def userinfo(self, ctx, user=None):
		"""
		Shows some info about a user. Defaults to self.
		"""
		user = user or ctx.author.id
		user = str(user).strip("<@!>")
		bot = self.bot
		emojis = bot.const_emojis
		badges = {
			"early_supporter": "Early Supporter",
			"bug_hunter": "Bug Hunter",
			"bug_hunter_level_2": "Bug Hunter Level 2",
			"partner": "Discord Partner",
			"verified_bot_developer": "Early Verified Bot Developer",
			"staff": "Discord Employee",
			"hypesquad_bravery": "HypeSquad Bravery",
			"hypesquad_brilliance": "HypeSquad Brilliance",
			"hypesquad_balance": "HypeSquad Balance",
			"hypesquad": "HypeSquad Events",
		}
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
			user_temp = ctx.guild.get_member(user_temp.id) or user_temp
			user = user_temp
		flags_nice = []
		voice_info = "Not connected to voice in this server"
		for flag in user.public_flags.all():
			if flag.name in badges:
				flags_nice.append(f"{emojis[flag.name]} {badges[flag.name]}")
		if user.is_avatar_animated():
			flags_nice.append(f"{emojis['nitro']} Nitro")
		elif int(user.discriminator) < 7:
			flags_nice.append(f"{emojis['nitro']} Nitro (⚠ This is a guess, I cannot tell for certain.)")
		if isinstance(user, discord.Member):
			if user.premium_since != None:
				ms = round((datetime.datetime.now() - user.premium_since).days / 30, 0)
				if ms >= 24: flags_nice.append(f"{emojis['24moboost']} 24+ Month server boost")
				elif ms >= 18: flags_nice.append(f"{emojis['18moboost']} 18+ Month server boost")
				elif ms >= 15: flags_nice.append(f"{emojis['15moboost']} 15+ Month server boost")
				elif ms >= 12: flags_nice.append(f"{emojis['12moboost']} 12+ Month server boost")
				elif ms >= 9: flags_nice.append(f"{emojis['9moboost']} 9+ Month server boost")
				elif ms >= 6: flags_nice.append(f"{emojis['6moboost']} 6+ Month server boost")
				elif ms >= 3: flags_nice.append(f"{emojis['3moboost']} 3+ Month server boost")
				elif ms >= 2: flags_nice.append(f"{emojis['2moboost']} 2+ Month server boost")
				elif ms >= 1: flags_nice.append(f"{emojis['1moboost']} 1+ Month server boost")
			if user.voice:
				state = user.voice
				mute = "No"
				deaf = "No"
				video = "Off"
				stream = "No"
				if state.mute: mute = emojis['mute']
				elif state.self_mute: mute = emojis['self_mute']
				if state.deaf: deaf = emojis['deaf']
				elif state.self_deaf: deaf = emojis['self_deaf']
				if state.self_video: video = "On"
				voice_info = f"""
				Channel: {emojis['voice']} {state.channel}
				Muted: {mute}
				Deafened: {deaf}
				Video: {video}
				Streaming: {stream}
				"""
		if len(flags_nice) <= 0:
			flags_nice = "No badges."
		else:
			flags_nice = "\n".join(flags_nice)
		if isinstance(user, discord.Member):
			embed = discord.Embed(
				description=f"""**Nickname:** {user.nick}
				**User ID:** `{user.id}`
				**Role count:** {len(user.roles)}
				**Joined Server on:** {user.joined_at.astimezone(timezone('US/Mountain')).strftime("%a, %B %d, %Y at %I:%M%p MST")}
				**Account Created on:** {user.created_at.astimezone(timezone('US/Mountain')).strftime("%a, %B %d, %Y at %I:%M%p MST")}
				**Status:** {emojis[user.status.value]}
				**Bot:** {emojis["yes"] if user.bot else emojis["no"]}
				**Mobile:** {emojis["yes"] if user.is_on_mobile() else emojis["no"]}
				**Badges:**
				{flags_nice}"""
				.replace("	", ""),
				color=user.color
				)
			embed.set_author(name=f"{str(user)}'s Info:", icon_url=user.avatar_url)
			embed.add_field(name="Custom Status", value=f"```{user.activity}```", inline=False)
			embed.add_field(name=f"Voice State", value=voice_info, inline=False)
		else:
			embed = discord.Embed(
				title=f"{str(user)}'s Info:", 
				description=f"""**Name:** {user.name}
				**User ID:** `{user.id}`
				**Account Created on:** {user.created_at.astimezone(timezone('US/Mountain')).strftime("%a, %B %d, %Y at %I:%M%p MST")}
				**Bot:** {emojis["yes"] if user.bot else emojis["no"]}
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
		emojis = bot.const_emojis
		g = ctx.guild
		if guildid != None and bot.get_guild(guildid):
			g = bot.get_guild(guildid)
		humans = 0
		bots = 0
		vlevels = ["None: Unrestricted", "Low: Must have a verified email on their Discord account.", "Medium: Must also be registered on Discord for longer than 5 minutes.", "(╯°□°）╯︵ ┻━┻  (High): Must also be a member of this server for longer than 10 minutes.", "┻━┻ ﾐヽ(ಠ益ಠ)ノ彡┻━┻  (Extreme): Must have a verified phone on their Discord account."]
		filters = ["Don't scan any media content: My friends are nice most of the time.", "Scan media content from members without a role: Recommended for servers that use roles for trusted membership.", "Scan media content from all members: Recommended for when you want that squeaky clean shine."]
		for m in g.members: 
			if m.bot: bots += 1
			else: humans += 1
		rules = "None set"
		if g.rules_channel: rules = f"{emojis['rules']} {g.rules_channel.mention}"
		embed = discord.Embed(
			title=f"{g.name}'s Info",
			description=f"""**Owner:** {g.owner} ({g.owner.id})
			**Members:** Total- {g.member_count}, Humans- {humans}, Bots- {bots}
			**Channels:** {emojis['category']} {len(g.categories)} categories, {emojis['text']} {len(g.text_channels)} text, {emojis['voice']} {len(g.voice_channels)} voice
			**Roles:** {len(g.roles)-1}
			**Emojis:** {len(g.emojis)}
			**Features:** {", ".join([str(f).title().replace("_", " ") for f in g.features])}
			**System Messages:** {g.system_channel.mention if g.system_channel else 'None set'}
			**Rules Channel:** {rules}
			**2FA Required?** {emojis['yes'] if g.mfa_level else emojis['no']}
			**Verification Level:** {vlevels[g.verification_level.value]}
			**Explicit Content Filter:** {filters[g.explicit_content_filter.value]}
			**Region:** {str(g.region).title().replace("Us-", "US-")}
			
			[Link to Icon]({g.icon_url})"""
			.replace("	", ""),
			color=discord.Color.random()
		)
		# embed.add_field(name=f"Emojis ({len(g.emojis)}):", value=f"{for e in g.emojis: ems = f'{ems} {e}'}")
		embed.set_footer(text=f"ID: {g.id} | Created on ", icon_url=g.icon_url)
		embed.timestamp=g.created_at #Created on {g.created_at.astimezone(timezone('US/Mountain')).strftime("%a, %B %d, %Y at %I:%M%p MST")}")
		await ctx.send(embed=embed)
	
	@commands.command(name="roleinfo", aliases=['ri'])
	@commands.guild_only()
	async def roleinfo(self, ctx, role: typing.Optional[discord.Role]):
		role = role or ctx.author.top_role
		embed=discord.Embed(
		title=f"{role.name}'s Info",
		description=f"""
		**Members:** {len(role.members)}
		**Position:** {role.position}
		**Color:** {role.color}
		**Hoisted:** {self.bot.const_emojis['yes'] if role.hoist else self.bot.const_emojis['no']}
		**Mentionable:** {self.bot.const_emojis['yes'] if role.mentionable else self.bot.const_emojis['no']}
		**Bot Managed:** {self.bot.const_emojis['yes'] if role.is_bot_managed() else self.bot.const_emojis['no']}
		{f'**Bot User:** {ctx.guild.get_member(role.tags.bot_id)} ({role.tags.bot_id})' if role.tags else ''}
		""".replace("	", ""),
		color=role.color)
		embed.set_footer(text=f"ID: {role.id}| Created on ")
		embed.timestamp=role.created_at
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
	async def newrole(self, ctx, color: typing.Optional[discord.Color], hoist: typing.Optional[bool]=False, *, name):
		r = await ctx.guild.create_role(name=name, color=color, hoist=hoist, reason=f"Role created by {ctx.author} ({ctx.author.id})")
		await ctx.send(f"Created {r.mention}!", allowed_mentions=discord.AllowedMentions(roles=False))
		
	@commands.command(name="delrole")
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True)
	@commands.guild_only()
	async def delrole(self, ctx, role: discord.Role):
		if ctx.author.top_role <= role:
			await ctx.send(f"You can't delete {role.mention} as it's above your highest role!")
		else:
			await role.delete(reason=f"Role deleted by {ctx.author} ({ctx.author.id})")
			await ctx.send(f"Deleted `{role.name}`!")

	@commands.command(name="hoist")
	@commands.has_permissions(manage_roles=True)
	@commands.bot_has_permissions(manage_roles=True)
	async def hoist(self, ctx, role: discord.Role):
		am = discord.AllowedMentions(roles=False)
		if role >= ctx.author.top_role:
			await ctx.send(f"You can't edit {role.mention} as it's above your highest role!", allowed_mentions=am)
		elif role >= ctx.guild.me.top_role:
			await ctx.send(f"I can't edit {role.mention} as it's above my highest role!", allowed_mentions=am)
		else:
			if role.hoist == True:
				await role.edit(hoist=False, reason=f"Role dehoisted by {ctx.author} ({ctx.author.id}).")
				await ctx.send(f"Dehoisted {role.mention}!", allowed_mentions=am)
			else:
				await role.edit(hoist=True)
				await ctx.send(f"Hoisted {role.mention}!", allowed_mentions=am)

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
			await ctx.send(f"Gave {member.mention} some roles!\nRoles given: {', '.join([x.mention for x in given]) if len(given) > 0 else 'None'}\n{'Roles failed: ' + {', '.join([r.mention for r in failed])} if len(failed) > 0 else 'None'}", allowed_mentions=discord.AllowedMentions(users=True, roles=False, everyone=False))

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
					taken.append(role)
			await ctx.send(f"Removed some role from {member.mention}!\nRoles taken: {', '.join([x.mention for x in taken])}", allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False))

	@commands.command(name="setnick")
	@commands.bot_has_permissions(manage_nicknames=True)
	async def setnick(self, ctx, member: typing.Optional[discord.Member], *, newnick=None):
		mem = member or ctx.author
		oldnick = mem.nick
		if ctx.author.id != mem.id and (getattr(ctx.author.guild_permissions, "manage_nicknames") == False):
			await ctx.send("You don't have permission to change other users' nicknames!")
		elif ctx.author.id != mem.id and (getattr(ctx.author.guild_permissions, "manage_nicknames") == True):
			if mem.top_role >= ctx.guild.me.top_role and mem.id != self.bot.user.id:
				return await ctx.send("I can't change this user's nickname as their highest role is above mine!")
			if mem.top_role > ctx.guild.me.top_role and mem.id == self.bot.user.id:
				await ctx.guild.me.edit(nick=newnick, reason=f"Nickname changed from {oldnick} to {mem.nick} by {ctx.author} ({ctx.author.id})!")
				await ctx.send(f"Changed my nickname from `{oldnick}` to `{mem.nick}`")
			if mem.top_role >= ctx.author.top_role:
				return await ctx.send("You can't change this user's nickname as their highest role is above yours!")
			if (newnick != None) and (len(newnick) > 32):
				return await ctx.send("This nickname is too long! It must be 32 characters or less.")
			await mem.edit(nick=newnick, reason=f"Nickname changed from {oldnick} to {mem.nick} by {ctx.author} ({ctx.author.id})!")
			await ctx.send(f"Changed {mem}'s nickname from `{oldnick}` to `{mem.nick}`")
		elif ctx.author.id == mem.id and (getattr(ctx.author.guild_permissions, "change_nickname") == False):
			await ctx.send("You don't have permission to change your nickname!")
		elif ctx.author.id == mem.id and (getattr(ctx.author.guild_permissions, "change_nickname") == True):
			if mem.top_role >= ctx.guild.me.top_role:
				return await ctx.send("I can't change your nickname as your highest role is above mine!")
			await mem.edit(nick=newnick, reason=f"User changed their nickname from {oldnick} to {newnick}")
			await ctx.send(f"Changed your nickname from `{oldnick}` to `{mem.nick}`!")
			
	@commands.command(name="dehoist")
	@commands.has_permissions(manage_nicknames=True)
	@commands.bot_has_permissions(manage_nicknames=True)
	async def dehoist(self, ctx, hoister: str="!"):
		msg = await ctx.send("Dehoisting...")
		total = 0
		success = 0
		failed = 0
		for m in ctx.guild.members:
			if m.display_name.startswith(hoister):
				total += 1
				if m.top_role >= ctx.author.top_role:
					failed += 1
				elif m.top_role >= ctx.guild.me.top_role:
					failed += 1
				else:
					success += 1
					newnick = m.nick or m.name
					newnick = newnick.replace(hoister, "") or "Dehoisted"
					await m.edit(nick=newnick, reason=f"Dehoisted by {ctx.author} ({ctx.author.id})")
		await msg.edit(content=f"Successfully dehoisted {success} members! (Attempted: {total}, Failed: {failed})")

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

	@commands.command()
	async def embedsource(self, ctx, messageid: int, channelid: typing.Optional[int]):
		"""
		Gets the raw json source of an embed.
		"""
		message = await ctx.channel.fetch_message(messageid)
		embed = discord.Embed(title="Embed Source")
		if not message:
			channel = ctx.guild.get_channel(channelid)
			if not channel:
				return await ctx.send("Invalid channel ID")
			message = await channel.fetch_message(messageid)
			if not message:
				return await ctx.send("Could not find the given message in this channel or the given channel")
		if not message.embeds:
			return await ctx.send("The message has no embeds.")
		embeds = message.embeds
		embed.color = embeds[0].color
		dump = json.dumps([e.to_dict() for e in message.embeds])
		embed.description = f"```\n{dump}```"
		if len(embed.description) >= 2048:
			embed.description = f"Source was too long to send, you can find it here: {await postbin.postAsync(dump)}"
		await ctx.send(embed=embed)

	@commands.command(name="msglink", aliases=['mlink'])
	@commands.has_permissions(manage_messages=True)
	async def msglink(self, ctx):
		"""
		Toggle to enable/disable the message link preview in the current guild.
		"""
		action = "Enabled"
		db = await self.bot.dbquery("msglink", "enabled", "guildid=" + str(ctx.guild.id))
		if db:
			action = "Disabled"
			await self.bot.dbexec((f"DELETE FROM msglink WHERE guildid={ctx.guild.id}"))
		else:
			await self.bot.dbexec((f"DELETE FROM msglink WHERE guildid={ctx.guild.id}"))
			await self.bot.dbexec(("INSERT INTO msglink VALUES (?, ?)", (ctx.guild.id, "true")))
		await ctx.send(f"{action} message link preview in **{ctx.guild.name}**!")


	@commands.command(name="globalafk", aliases=['gafk'])
	async def globalafk(self, ctx, *, afkmessage="AFK"):
		"""
		Sets your global AFK message.
		"""
		await ctx.message.delete(delay=10)
		db = await self.bot.dbquery("globalafk", "message", f"userid={ctx.author.id}")
		if db:
			await self.bot.dbexec((f"DELETE FROM globalafk WHERE userid={ctx.author.id}"))
			if afkmessage == "AFK":
				await ctx.send(f"{ctx.author.mention}, I removed your AFK!", delete_after=10)
			else:
				await ctx.send(f"{ctx.author.mention}, I set your global AFK message to: ```\n{afkmessage}```", delete_after=10)
				await self.bot.dbexec((f"INSERT INTO globalafk VALUES (?, ?)", (str(ctx.author.id), str(afkmessage))))
		else:
			await ctx.send(f"{ctx.author.mention}, I set your global AFK message to: ```\n{afkmessage}```", delete_after=10)
			await self.bot.dbexec((f"INSERT INTO globalafk VALUES (?, ?)", (str(ctx.author.id), str(afkmessage))))
			
	@commands.command(name="afk")
	@commands.guild_only()
	async def afk(self, ctx, *, afkmessage="AFK"):
		"""
		Sets your local AFK message.
		"""
		await ctx.message.delete(delay=10)
		db = await self.bot.dbquery("afk", "data", f"guildid={ctx.guild.id}")
		guilddata={}
		if db:
			guilddata = json.loads((db[0][0]).replace("'", '"'))
			await self.bot.dbexec("DELETE FROM afk WHERE guildid=" + str(ctx.guild.id))
		if afkmessage == "AFK":
			try: 
				message = guilddata[str(ctx.author.id)]
			except: 
				message = None
			if message:
				guilddata.pop(str(ctx.author.id))
				await ctx.send(f"{ctx.author.mention}, I removed your AFK!", delete_after=10)
				newnick = str(ctx.author.nick).replace("{AFK} ", "")
				if newnick == str(ctx.author.name): newnick = None
				try: await ctx.author.edit(nick=newnick, reason="Removing AFK tag.")
				except: pass
				return await self.bot.dbexec(("INSERT INTO afk VALUES (?, ?)", (str(ctx.guild.id), str(guilddata))))
			else:
				guilddata[str(ctx.author.id)] = "AFK"
		else:
			guilddata[str(ctx.author.id)] = afkmessage
		await self.bot.dbexec(("INSERT INTO afk VALUES (?, ?)", (str(ctx.guild.id), str(guilddata))))
		if ctx.author.nick != None and "{AFK}" not in ctx.author.nick:
			afk = "{AFK}"
			newnick = f"{afk} {ctx.author.nick or ctx.author.name}"
			try: await ctx.author.edit(nick=newnick, reason="Adding AFK tag.")
			except: pass
		await ctx.send(f"{ctx.author.mention}, I set your AFK message in **{ctx.guild}** to: ```\n{afkmessage}```", delete_after=10)

	@commands.command(aliases=['ae', 'steal'])
	@commands.is_owner()
	@commands.has_permissions(manage_emojis=True)
	async def addemoji(self, ctx, name, url):
		async with aiohttp.ClientSession() as s:
			async with s.get(url) as r:
				em = await ctx.guild.create_custom_emoji(name=name, image=await r.content.read())
				await ctx.send(f"Created the emoji {em} with the name `{em.name}`!")

def setup(bot):
	bot.add_cog(Utils(bot))
	print('[UtilsCog] Utils cog loaded')
